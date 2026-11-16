"""Check a handful of facts in the original tar before finalising the v2 builder."""
import os
import sys
import tarfile

path = sys.argv[1]
tf = tarfile.open(path, 'r:')
want = [
    'opt/tiny/export.sh',
    'usr/bin/pgrep',
    'usr/bin/pkill',
    'usr/local/bin',
    'usr/local/share',
    'home/tiny/.config/xfce4/panel',
    'home/tiny/.config/autostart',
    'usr/share/applications/tiny-osk.desktop',
    'usr/bin/python3.13',
]
found = {}
names = set()
for ti in tf:
    n = ti.name
    while n.startswith('./'):
        n = n[2:]
    names.add(n)
    if n in want:
        found[n] = ti
out = []
for n in want:
    ti = found.get(n)
    if ti is None:
        out.append('ABSENT   %s' % n)
    else:
        out.append('PRESENT  %s type=%r size=%d mode=%o uid=%d' % (n, ti.type, ti.size, ti.mode, ti.uid))
out.append('total names: %d' % len(names))
print('\n'.join(out))
