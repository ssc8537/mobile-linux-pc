import io, os, sys, tarfile, pickle, zstandard

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
IMG = ROOT + r'\build-env-toolchain\cache-downloads-deletable\xfce-zh-20260808-160507.tar.zst'

paths = set()
status = None
with open(IMG, 'rb') as f:
    dctx = zstandard.ZstdDecompressor()
    with dctx.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for ti in tf:
            paths.add(ti.name)
            if ti.name == 'var/lib/dpkg/status' and ti.isreg():
                status = tf.extractfile(ti).read()

depends = {}
cur = None
for line in status.decode('utf-8', 'replace').splitlines():
    if line.startswith('Package: '):
        cur = line[9:].strip()
    elif cur and line.startswith('Depends: '):
        depends[cur] = line[9:].strip()

pickle.dump({'paths': paths, 'depends': depends},
            io.open(ROOT + r'\tools-probe-scripts-deletable\image_index.pkl', 'wb'))
print('entries:', len(paths), 'packages with depends:', len(depends))

bases = {}
for p in paths:
    bases.setdefault(p.rsplit('/', 1)[-1], 0)
    bases[p.rsplit('/', 1)[-1]] += 1


def present(lib):
    if lib in bases:
        return True
    return any(b.startswith(lib + '.') for b in bases)


for lib in ['libcairo-gobject.so.2', 'libwnck-3.so.0', 'libXmu.so.6',
            'libxfconf-0.so.3', 'libqrencode.so.4', 'libwayland-client.so.0',
            'libxtst.so.6', 'libgtk-3.so.0', 'libxfce4ui-2.so.0',
            'libxfce4panel-2.0.so.4', 'libxfce4util.so.7',
            'libgdk-pixbuf-2.0.so.0', 'libglib-2.0.so.0', 'libcairo.so.2',
            'libX11.so.6', 'libxfce4windowing-0.so.0']:
    print(('OK  ' if present(lib) else 'MISS'), lib)
