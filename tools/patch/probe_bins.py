import sys, tarfile
import zstandard

IMG = sys.argv[1]
WANT_BIN = [
    'flameshot', 'xfce4-taskmanager', 'xfce4-screenshooter', 'xfce4-terminal',
    'thunar', 'mousepad', 'ristretto', 'xarchiver', 'gdebi', 'firefox-esr',
    'fcitx5', 'xfce4-appfinder', 'xfce4-panel', 'xfconf-query', 'picom',
    'xdotool', 'wmctrl', 'conky', 'rofi', 'dunst', 'xfce4-clipman',
    'copyq', 'wine', 'wine64', 'code', 'onlyoffice-desktopeditors',
]
WANT_PLUGIN = ['docklike', 'clipman', 'cpufreq', 'weather', 'systemload',
               'netload', 'genmon', 'places', 'datetime', 'smartbookmark',
               'verve', 'xfce4-notes', 'xfce4-datetime']
dctx = zstandard.ZstdDecompressor()
found_bin = {}
plugins = []
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n = m.name
            if n.startswith('usr/bin/'):
                b = n[8:]
                if b in WANT_BIN:
                    found_bin[b] = (m.size, oct(m.mode))
            if '/xfce4/panel/plugins/' in n and n.endswith('.so'):
                plugins.append((n.rsplit('/', 1)[-1], m.size))
print('== binaries ==')
for b in WANT_BIN:
    print('  %-24s %s' % (b, found_bin.get(b, 'MISSING')))
print('== panel plugins (%d) ==' % len(plugins))
for p, s in sorted(plugins):
    print('  %-40s %d' % (p, s))
