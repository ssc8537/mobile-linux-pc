"""List autostart entries and a few extra paths in a rootfs tar."""
import sys
import tarfile

path = sys.argv[1]
tf = tarfile.open(path, 'r:')
rows = []
for ti in tf:
    n = ti.name
    while n.startswith('./'):
        n = n[2:]
    if n.startswith('etc/xdg/autostart/') or n.startswith('home/tiny/.config/autostart/'):
        rows.append('%s  size=%d mode=%o' % (n, ti.size, ti.mode))
    elif n.startswith('usr/share/xfce4/panel/plugins/') and 'docklike' in n:
        rows.append('%s  size=%d' % (n, ti.size))
    elif n in ('usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libdocklike.so',
               'usr/bin/xfce4-taskmanager', 'usr/bin/xfce4-screenshooter',
               'usr/local/share/tiny-osk/tiny_osk.py'):
        rows.append('%s  size=%d mode=%o' % (n, ti.size, ti.mode))
print('\n'.join(sorted(rows)))
print('count=%d' % len(rows))
