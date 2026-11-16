import sys, tarfile
import zstandard

IMG = sys.argv[1]

# Onboard runtime deps (python3-gi based) + XTest + typelibs
WANT_EXACT = {
    'usr/lib/aarch64-linux-gnu/libXtst.so.6': 'libXtst6',
    'usr/lib/aarch64-linux-gnu/libxkbfile.so.1': 'libxkbfile1',
    'usr/lib/aarch64-linux-gnu/libcanberra.so.0': 'libcanberra0',
    'usr/lib/aarch64-linux-gnu/libhunspell-1.7.so.0': 'libhunspell',
    'usr/lib/aarch64-linux-gnu/libdconf.so.1': 'libdconf1',
    'usr/bin/dconf': 'dconf-cli',
    'usr/bin/xkbcomp': 'xkbcomp',
    'usr/bin/xmodmap': 'xmodmap',
}
TYPO = [
    'Gtk-3.0', 'Gdk-3.0', 'GdkPixbuf-2.0', 'Pango-1.0', 'PangoCairo-1.0',
    'Atspi-2.0', 'Gio-2.0', 'GLib-2.0', 'GObject-2.0', 'cairo-1.0',
    'xklavier-1.0', 'X11-2.0',
]
PYMODS = [
    'gi/__init__.py', 'cairo/__init__.py', 'dbus/__init__.py',
    'gi/repository/__init__.py',
]
dctx = zstandard.ZstdDecompressor()
exact = {}
typos = {}
pymods = {}
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n = m.name
            if n in WANT_EXACT:
                exact[n] = m.size
            if n.startswith('usr/lib/aarch64-linux-gnu/girepository-1.0/'):
                b = n.rsplit('/', 1)[-1]
                if b.endswith('.typelib'):
                    typos[b[:-8]] = m.size
            if n.startswith('usr/lib/python3/dist-packages/'):
                rel = n[len('usr/lib/python3/dist-packages/'):]
                for p in PYMODS:
                    if rel == p:
                        pymods[p] = m.size
print('== exact ==')
for k, label in WANT_EXACT.items():
    print('  %-46s %-14s %s' % (k.rsplit('/', 1)[-1], label, exact.get(k, 'MISSING')))
print('== typelibs (%d total) ==' % len(typos))
for t in TYPO:
    print('  %-16s %s' % (t, typos.get(t, 'MISSING')))
print('== python modules ==')
for p in PYMODS:
    print('  %-28s %s' % (p, pymods.get(p, 'MISSING')))
