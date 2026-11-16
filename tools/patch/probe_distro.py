import sys, tarfile
import zstandard

path = sys.argv[1]
dctx = zstandard.ZstdDecompressor()

want_exact = {
    'etc/os-release',
    'etc/debian_version',
    'etc/xfce/xfce4-version',
}
want_prefix = {
    'usr/lib/xfce4/panel/plugins/',
    'usr/lib/arm-linux-gnueabihf/xfce4/panel/plugins/',
    'usr/share/xfce4/panel/plugins/',
    'usr/lib/firefox-esr',
    'usr/share/applications/',
}
hits = {k: [] for k in want_prefix}
found = {}
counts = {'docklike': 0, 'xfce4_panel_app': 0, 'whisker': 0}
with open(path, 'rb') as fh:
    with dctx.stream_reader(fh) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tf:
            for m in tf:
                name = m.name.lstrip('./')
                if name in want_exact and m.isfile():
                    found[name] = tf.extractfile(m).read().decode('utf-8', 'replace')
                    continue
                if 'docklike' in name:
                    counts['docklike'] += 1
                if 'whisker' in name.lower():
                    counts['whisker'] += 1
                for p in want_prefix:
                    if name.startswith(p) and len(hits[p]) < 400:
                        hits[p].append(name)
print("=== os-release ===")
for k, v in found.items():
    print("---", k, "---")
    print(v)
print("=== counts ===", counts)
print("=== panel plugins ===")
for p in ('usr/lib/xfce4/panel/plugins/', 'usr/lib/arm-linux-gnueabihf/xfce4/panel/plugins/'):
    names = sorted(set(hits[p]))
    print(p, len(names))
    for n in names:
        print("   ", n)
print("=== firefox-esr libs (sample) ===", len(hits['usr/lib/firefox-esr']))
for n in sorted(hits['usr/lib/firefox-esr'])[:12]:
    print("   ", n)
