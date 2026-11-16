import io, os, sys, tarfile

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
DEBS = ROOT + r'\build-env-toolchain\cache-downloads-deletable\debs'
OUT = ROOT + r'\tools-probe-scripts-deletable\debcat-%s.txt'


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


deb = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else None
buf = []
tf = data_tar(os.path.join(DEBS, deb))
for ti in tf:
    if ti.isreg() and (want is None or want in ti.name):
        buf.append('=' * 60)
        buf.append('%s size=%d mode=%s uid=%d gid=%d' % (ti.name, ti.size, oct(ti.mode), ti.uid, ti.gid))
        if ti.size < 20000:
            try:
                buf.append(tf.extractfile(ti).read().decode('utf-8', 'replace'))
            except Exception as e:
                buf.append('<binary %s>' % e)
p = OUT % sys.argv[3] if len(sys.argv) > 3 else OUT % 'x'
io.open(p, 'w', encoding='utf-8').write('\n'.join(buf))
print(p)
