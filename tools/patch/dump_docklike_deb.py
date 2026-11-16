import io, os, sys, tarfile

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
lines = []
for ti in tf:
    lines.append('%s %s %d' % (ti.type.decode(), ti.name, ti.size))
    if ti.isreg() and ti.name.endswith('.desktop'):
        lines.append('---- ' + ti.name)
        lines.append(tf.extractfile(ti).read().decode('utf-8', 'replace'))
io.open(ROOT + r'\tools-probe-scripts-deletable\debcat-docklike-full.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:40]))
