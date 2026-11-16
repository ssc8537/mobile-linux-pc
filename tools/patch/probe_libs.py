import sys, tarfile
import zstandard

IMG = sys.argv[1]
LIBS = [
    'libc.so.6', 'libcairo.so.2', 'libgcc_s.so.1', 'libgdk_pixbuf-2.0.so',
    'libglib-2.0.so', 'libgtk-3.so.0', 'libstdc++.so.6', 'libX11.so.6',
    'libxfce4panel-2.0.so', 'libxfce4ui-2.so', 'libxfce4util.so',
    'libxfce4windowing-0.so', 'libXi.so.6',
]
found = {}
dctx = zstandard.ZstdDecompressor()
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            if m.name.startswith('usr/lib/aarch64-linux-gnu/'):
                b = m.name.rsplit('/', 1)[-1]
                for L in LIBS:
                    if b == L or b.startswith(L + '.'):
                        found.setdefault(L, []).append((b, m.size))
for L in LIBS:
    print('%-26s %s' % (L, found.get(L, 'MISSING')))
