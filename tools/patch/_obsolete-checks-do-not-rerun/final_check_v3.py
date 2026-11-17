import tarfile, sys
tar = tarfile.open(sys.argv[1], 'r:')
names = {m.name: m for m in tar.getmembers()}
for p in ('opt/tiny/export.sh','home/tiny/.config/xfce4/panel/docklike-2.rc'):
    print('==', p, names[p].size)
k = tar.extractfile(names['home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml']).read().decode()
print('Super+v:', '&lt;Super&gt;v' in k, '| Super+Shift+v:', '&lt;Super&gt;&lt;Shift&gt;v' in k, '| Launch0:', k.count('XF86Launch0'))
print('clipman autostart:', 'home/tiny/.config/autostart/tiny-clipman.desktop' in names)
print('osk settings present:', b'_open_settings' in tar.extractfile(names['usr/local/share/tiny-osk/tiny_osk.py']).read())
