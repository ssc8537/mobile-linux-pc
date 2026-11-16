"""Verify the freshly built v2 rootfs tar before compressing it."""
import io
import os
import sys
import tarfile

path = sys.argv[1]
want = [
    'opt/tiny/export.sh',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml',
    'home/tiny/.config/xfce4/panel/docklike-2.rc',
    'home/tiny/.config/autostart/tiny-osk.desktop',
    'usr/share/applications/tiny-osk.desktop',
    'usr/local/share/tiny-osk/tiny_osk.py',
    'usr/local/bin/tiny-osk',
    'usr/local/bin/tiny-osk-toggle',
    'usr/bin/xfce4-taskmanager',
    'usr/bin/xfce4-screenshooter',
    'usr/bin/xfce4-clipman',
    'usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libdocklike.so',
    'usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libclipman.so',
    'usr/lib/aarch64-linux-gnu/libqrencode.so.4.1.1',
]

DUMP_TEXT = {
    'opt/tiny/export.sh',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml',
    'home/tiny/.config/xfce4/panel/docklike-2.rc',
    'home/tiny/.config/autostart/tiny-osk.desktop',
    'usr/share/applications/tiny-osk.desktop',
    'usr/local/bin/tiny-osk',
    'usr/local/bin/tiny-osk-toggle',
}

found = {}
extra_count = 0
total = 0
tf = tarfile.open(path, 'r:')
for ti in tf:
    total += 1
    n = ti.name
    while n.startswith('./'):
        n = n[2:]
    if n in want:
        found[n] = ti
out = []
out.append('total members: %d' % total)
for n in want:
    ti = found.get(n)
    if ti is None:
        out.append('MISSING  %s' % n)
        continue
    out.append('OK       %s type=%s size=%d mode=%o uid=%d gid=%d'
               % (n, ti.type, ti.size, ti.mode, ti.uid, ti.gid))
for n in sorted(DUMP_TEXT):
    ti = found.get(n)
    if ti is None or not ti.isreg():
        continue
    body = tf.extractfile(ti).read().decode('utf-8', 'replace')
    out.append('===== %s (%d bytes) =====' % (n, len(body)))
    out.append(body)
io.open(os.path.splitext(path)[0] + '-verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:25]))
