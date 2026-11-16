import io, os, sys, tarfile, re

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
DEBS = ROOT + r'\build-env-toolchain\cache-downloads-deletable\debs'


def ar_members(path):
    data = io.open(path, 'rb').read()
    pos = 8
    out = {}
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
needle = sys.argv[1].encode() if len(sys.argv) > 1 else b'pinned'
tf = data_tar(deb)
for ti in tf:
    if ti.isreg() and ti.name.endswith('libdocklike.so'):
        blob = tf.extractfile(ti).read()
        print('size', len(blob))
        strs = re.findall(rb'[\x20-\x7e]{4,}', blob)
        hits = [s.decode() for s in strs if needle in s.lower()]
        seen = set()
        for h in hits:
            if h not in seen:
                seen.add(h)
                print('  ', h)
