import sys, tarfile, io, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyz2'))
import zstandard

IMG = r'Linux-小小容器\04-下载缓存-可删除\xfce-zh-20260808-160507.tar.zst'

want_exact = {
    'var/lib/dpkg/status',
    'etc/xdg/xfce4/panel/default.xml',
    'usr/bin/xfconf-query',
    'usr/bin/dpkg',
    'usr/bin/apt',
    'usr/bin/xfce4-panel',
    'usr/bin/xfce4-session',
    'usr/share/applications/firefox-esr.desktop',
}
# substring patterns
want_sub = [
    'libwnck-3.so',
    'libxfce4panel-2.0.so',
    'libxfce4ui-2.so',
    'libgtk-3.so',
    'xfce4/panel/plugins/',
    'xfce4/panel/launcher-',
    'docklike',
    'xfce4-panel-profiles',
    'usr/share/applications/',
    'home/tiny/.config/xfce4/panel/',
    'home/tiny/.config/autostart',
    'opt/tiny/export.sh',
]

hits = []
dpkg_status = None
default_xml = None

with open(IMG, 'rb') as f:
    dctx = zstandard.ZstdDecompressor()
    with dctx.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            name = m.name
            if name in want_exact:
                hits.append((name, m.size, m.type))
                if name == 'var/lib/dpkg/status':
                    dpkg_status = tf.extractfile(m).read().decode('utf-8', 'replace')
                elif name == 'etc/xdg/xfce4/panel/default.xml':
                    default_xml = tf.extractfile(m).read().decode('utf-8', 'replace')
            elif any(s in name for s in want_sub):
                hits.append((name, m.size, m.type))

print('=== matches ===')
for n, s, t in hits:
    print(f'{s:>10} {t} {n}')

print('\n=== default panel xml ===')
print((default_xml or '(absent)')[:2000])

print('\n=== dpkg key packages ===')
if dpkg_status:
    pkgs = {}
    cur = {}
    for line in dpkg_status.splitlines():
        if not line.strip():
            if 'Package' in cur:
                pkgs[cur['Package']] = cur
            cur = {}
        elif ': ' in line:
            k, v = line.split(': ', 1)
            cur[k] = v
    if 'Package' in cur:
        pkgs[cur['Package']] = cur
    for p in ['xfce4-panel', 'xfce4-session', 'libxfce4panel-2.0-4', 'libxfce4ui-2-0',
              'libwnck-3-0', 'firefox-esr', 'thunar', 'xfce4-whiskermenu-plugin',
              'xfce4-terminal', 'desktop-file-utils', 'gtk-3.0']:
        st = pkgs.get(p)
        print(f'{p:32} {"MISSING" if not st else st.get("Version","?")}')
    print(f'total packages: {len(pkgs)}')
