import io, os, re, sys, tarfile

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
DEBS = ROOT + r'\build-env-toolchain\cache-downloads-deletable\debs'


def ar_members(path):
    data = io.open(path, 'rb').read()
    pos, out = 8, {}
    while pos < len(data):
        hdr = data[pos:pos + 60]
        if len(hdr) < 60:
            break
        name = hdr[0:16].decode('ascii', 'replace').strip().rstrip('/')
        size = int(hdr[48:58].decode('ascii').strip())
        out[name] = data[pos + 60:pos + 60 + size]
        pos += 60 + size
        if pos % 2:
            pos += 1
    return out


def data_tar(deb):
    m = ar_members(deb)
    key = [k for k in m if k.startswith('data.tar')][0]
    return tarfile.open(fileobj=io.BytesIO(m[key]), mode='r:*')


deb = os.path.join(DEBS, 'xfce4-docklike-plugin_0.4.3-1_arm64.deb')
tf = data_tar(deb)
out = []
for ti in tf:
    if ti.isreg() and ti.name.endswith('libdocklike.so'):
        blob = tf.extractfile(ti).read()
        strs = [s.decode('latin-1') for s in re.findall(rb'[\x20-\x7e]{3,}', blob)]
        out.extend(strs)

io.open(ROOT + r'\tools-probe-scripts-deletable\debcat-docklike-strings.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('total', len(out))
# short lowercase-ish tokens that look like rc keys
cand = sorted({s for s in out if 3 <= len(s) <= 22 and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', s)})
io.open(ROOT + r'\tools-probe-scripts-deletable\debcat-docklike-keys.txt', 'w', encoding='utf-8').write('\n'.join(cand))
print('candidates', len(cand))
