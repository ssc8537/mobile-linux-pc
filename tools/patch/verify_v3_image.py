import tarfile, sys
tar = tarfile.open(sys.argv[1], 'r:')
want = [
 'usr/share/xfce4/panel/plugins/docklike.desktop',
 'usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libdocklike.so',
 'home/tiny/.config/xfce4/panel/docklike-2.rc',
 'usr/bin/xfce4-taskmanager',
 'usr/bin/xfce4-screenshooter',
 'usr/bin/xfce4-clipman',
 'usr/bin/xfce4-clipman-history',
 'usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libclipman.so',
 'usr/lib/aarch64-linux-gnu/libqrencode.so.4.1.1',
 'etc/xdg/autostart/xfce4-clipman-plugin-autostart.desktop',
 'usr/local/bin/tiny-osk',
 'usr/local/bin/tiny-osk-toggle',
 'usr/local/share/tiny-osk/tiny_osk.py',
 'home/tiny/.config/autostart/tiny-osk.desktop',
 'usr/share/applications/tiny-osk.desktop',
]
names = {m.name: m for m in tar.getmembers()}
for w in want:
    m = names.get(w)
    print(('OK   ' if m else 'MISS '), w, m.size if m else '')
# docklike rc content
rc = tar.extractfile(names['home/tiny/.config/xfce4/panel/docklike-2.rc']).read().decode()
print('--- docklike-2.rc ---')
print(rc)
sh = tar.extractfile(names['opt/tiny/export.sh']).read().decode()
print('--- export.sh has mozilla removal:', 'mozilla' in sh, ' apt clean:', 'apt clean' in sh)
