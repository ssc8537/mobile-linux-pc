import sys, tarfile
import zstandard

IMG = sys.argv[1]

BINS = [
    'onboard', 'xvkbd', 'florence', 'matchbox-keyboard', 'xvkbd-settings',
    'xfce4-taskmanager', 'xfce4-clipman', 'xfce4-clipman-plugin',
    'xfce4-screenshooter', 'picom', 'xdotool', 'wmctrl', 'xclip', 'xsel',
    'python3', 'python3.13', 'gsettings', 'dbus-launch', 'xvkbd',
    'florence-hide', 'cellwriter', 'eekboard', 'caribou', 'gok',
]
DIRS = [
    'usr/lib/python3/dist-packages/gi',
    'usr/lib/python3/dist-packages/onboard',
    'usr/share/gir-1.0',
    'usr/lib/aarch64-linux-gnu/girepository-1.0',
]
PREFIX_HITS = {
    'girepository(Gtk)': 'girepository-1.0/Gtk-3.0.typelib',
    'girepository(Gio)': 'girepository-1.0/Gio-2.0.typelib',
    'girepository(GLib)': 'girepository-1.0/GLib-2.0.typelib',
    'onboard-share': 'usr/share/onboard',
    'xvkbd-share': 'usr/share/X11/app-defaults/XVkbd',
}

found_bin = {}
dir_hits = {}
prefix_hits = {}
dctx = zstandard.ZstdDecompressor()
n = 0
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n += 1
            name = m.name
            if name.startswith('usr/bin/'):
                b = name[8:]
                if b in BINS:
                    found_bin[b] = (m.size, oct(m.mode))
            for d in DIRS:
                if name == d or name.startswith(d + '/'):
                    dir_hits[d] = dir_hits.get(d, 0) + 1
            for k, suf in PREFIX_HITS.items():
                if name.endswith(suf):
                    prefix_hits[k] = (name, m.size)

print('entries:', n)
print('== binaries ==')
for b in BINS:
    if b in found_bin:
        print('  %-24s %s' % (b, found_bin[b]))
print('  (missing:', ', '.join(b for b in BINS if b not in found_bin), ')')
print('== dirs (entry counts) ==')
for d in DIRS:
    print('  %-46s %s' % (d, dir_hits.get(d, 'MISSING')))
print('== prefix hits ==')
for k in PREFIX_HITS:
    print('  %-20s %s' % (k, prefix_hits.get(k, 'MISSING')))
