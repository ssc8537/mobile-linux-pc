"""Build a small overlay tar containing ONLY what v2 added or changed vs the stock image.

Usage: python make_patch_tar.py <plain.tar> <v2.tar> <out-patch.tar>

The result is extracted on top of an existing container (no wipe), so the user
keeps all personal data while getting docklike / taskmanager / OSK / export.sh fix.
"""
import sys
import tarfile

PATCHED = {
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml',
    'opt/tiny/export.sh',
}


def norm(name):
    while name.startswith('./'):
        name = name[2:]
    return name


def main():
    plain_path, v2_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    base = set()
    with tarfile.open(plain_path, 'r:', encoding='utf-8') as tf:
        for m in tf:
            base.add(norm(m.name))
    print('base members: %d' % len(base))

    copied = 0
    picked_new = 0
    picked_patch = 0
    with tarfile.open(v2_path, 'r:', encoding='utf-8') as src, \
            tarfile.open(out_path, 'w:', format=tarfile.GNU_FORMAT, encoding='utf-8') as dst:
        for m in src:
            name = norm(m.name)
            is_new = name not in base and not name.startswith('.tiny.yaml')
            is_patched = name in PATCHED
            if not (is_new or is_patched):
                continue
            data = src.extractfile(m).read() if m.isreg() else None
            m.name = name
            if data is None:
                dst.addfile(m)
            else:
                import io as _io
                m.size = len(data)
                dst.addfile(m, _io.BytesIO(data))
            copied += 1
            if is_patched:
                picked_patch += 1
            else:
                picked_new += 1

    print('patch members: %d (patched=%d new=%d)' % (copied, picked_patch, picked_new))


if __name__ == '__main__':
    main()
