import sys, tarfile, re
import zstandard

IMG = sys.argv[1]
dctx = zstandard.ZstdDecompressor()

NEED = [
    'libxfce4windowing',
    'xfce4-panel-profiles',
    'xfce4-docklike',
    'libwnck-3',
    'xfce4-appfinder',
    'gtk-3.0',
    'Fluent-Light',
    'xfce4-taskmanager',
    'xfce4-screenshooter',
    'flameshot',
]
hits = {k: [] for k in NEED}
count = 0
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            count += 1
            n = m.name
            for k in NEED:
                if k in n and len(hits[k]) < 6:
                    hits[k].append((n, m.size))
print('entries:', count)
for k in NEED:
    print('##', k)
    for n, s in hits[k]:
        print('   ', s, n)
    if not hits[k]:
        print('    (none)')
