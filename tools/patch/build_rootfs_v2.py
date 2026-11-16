"""Build the v2 rootfs tar: patch panel/shortcuts/export.sh, add docklike + taskmanager +
clipman + screenshooter + libqrencode4, keeping every original
tar member byte-identical (uid/gid/mode/mtime/uname/gname preserved).

argv[1] = input plain .tar (seekable)
argv[2] = output plain .tar
"""
import io
import os
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBS = os.path.join(ROOT, 'build-env-toolchain', 'cache-downloads-deletable', 'debs')
DUMP = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'imagedump')

OWNER_UID = 10258
OWNER_GID = 10258
OWNER_UNAME = 'aid_u0_a258'
OWNER_GNAME = 'aid_u0_a258'

# --------------------------------------------------------------------- utilities

def ar_members(path):
    data = io.open(path, 'rb').read()
    pos, out = 8, {}
    while pos < len(data):
        hdr = data[pos:pos + 60]
        if len(hdr) < 60:
            break
        name = hdr[0:16].decode('ascii', 'replace').strip().rstrip('/')
        size = int(hdr[48:58].decode('ascii').strip())
        out[name] = data[pos + 60:pos + 60 + size]
        pos += 60 + size
        if pos % 2:
            pos += 1
    return out


def deb_data_tar(path):
    members = ar_members(path)
    key = [k for k in members if k.startswith('data.tar')][0]
    return tarfile.open(fileobj=io.BytesIO(members[key]), mode='r:*')


def norm(name):
    """Strip only a literal leading './' (NOT lstrip, which would eat dotfiles)."""
    while name.startswith('./'):
        name = name[2:]
    return name


def new_info(name, size=0, mode=0o644, is_dir=False, linkname=''):
    info = tarfile.TarInfo(name)
    info.size = 0 if is_dir else size
    info.mode = mode
    info.uid = OWNER_UID
    info.gid = OWNER_GID
    info.uname = OWNER_UNAME
    info.gname = OWNER_GNAME
    info.mtime = 1767225600  # 2026-01-01, keeps output deterministic
    if is_dir:
        info.type = tarfile.DIRTYPE
    elif linkname:
        info.type = tarfile.SYMTYPE
        info.linkname = linkname
        info.mode = 0o777
    else:
        info.type = tarfile.REGTYPE
    return info


# ------------------------------------------------------------------ file patches

def build_panel_xml():
    """tasklist (plugin-2) becomes docklike; everything else verbatim."""
    src = io.open(os.path.join(
        DUMP, 'home__tiny__.config__xfce4__xfconf__xfce-perchannel-xml__xfce4-panel.xml'),
        encoding='utf-8').read()
    old = ('    <property name="plugin-2" type="string" value="tasklist">\n'
           '      <property name="grouping" type="uint" value="1"/>\n'
           '      <property name="show-labels" type="bool" value="true"/>\n'
           '      <property name="flat-buttons" type="bool" value="false"/>\n'
           '      <property name="show-handle" type="bool" value="false"/>\n'
           '    </property>')
    new = ('    <property name="plugin-2" type="string" value="docklike">\n'
           '      <!-- Local fork: Windows-style grouped taskbar with pinning -->\n'
           '      <property name="indicatorStyle" type="int" value="1"/>\n'
           '      <property name="indicatorOrientation" type="int" value="1"/>\n'
           '      <property name="onlyDisplayScreen" type="bool" value="true"/>\n'
           '    </property>')
    if old not in src:
        raise SystemExit('panel xml: tasklist block not found')
    return src.replace(old, new).encode('utf-8')


def build_shortcuts_xml():
    src = io.open(os.path.join(
        DUMP, 'home__tiny__.config__xfce4__xfconf__xfce-perchannel-xml__xfce4-keyboard-shortcuts.xml'),
        encoding='utf-8').read()
    anchor_default = '    <property name="default" type="empty">\n'
    anchor_custom = '    <property name="custom" type="empty">\n'
    for a in (anchor_default, anchor_custom):
        if a not in src:
            raise SystemExit('shortcuts xml: anchor not found: %r' % a)
    src = src.replace(
        anchor_custom,
        anchor_custom
        + '      <!-- Local fork: Super+V pops the clipboard history, like Windows Win+V -->\n'
        + '      <property name="&lt;Super&gt;v" type="string" value="xfce4-popup-clipman"/>\n'
        + '      <!-- Local fork: Super+Shift+V pops the full clipboard manager window -->\n'
        + '      <property name="&lt;Super&gt;&lt;Shift&gt;v" type="string" value="xfce4-clipman-history"/>\n', 1)
    return src.encode('utf-8')


def build_export_sh():
    src = io.open(os.path.join(DUMP, 'opt__tiny__export.sh'), encoding='utf-8').read()
    kept = []
    for line in src.splitlines(True):
        stripped = line.strip()
        if stripped.startswith('apt clean'):
            continue          # never touch the package cache on export
        if stripped.startswith('rm -rvf') or stripped.startswith('rm -rf'):
            continue          # never delete ~/.mozilla etc: the snapshot keeps user data
        kept.append(line)
    out = ''.join(kept)
    if 'tar --zstd' not in out:
        raise SystemExit('export.sh: tar line lost')
    if 'rm -rvf' in out or 'apt clean' in out:
        raise SystemExit('export.sh: cleanup lines still present')
    return out.encode('utf-8')


CLIPMAN_AUTOSTART = (
    '[Desktop Entry]\n'
    'Type=Application\n'
    'Name=Clipman\n'
    'Comment=Clipboard manager (Windows-style Win+V history)\n'
    'Exec=xfce4-clipman\n'
    'Icon=xfce4-clipman-plugin\n'
    'Terminal=false\n'
    'NoDisplay=true\n'
    'X-GNOME-Autostart-enabled=true\n'
)



def build_extras():
    """returns list of (name, TarInfo, payload-bytes-or-None)"""
    out = []

    def reg(name, data, mode=0o644):
        out.append((name, new_info(name, size=len(data), mode=mode), data))

    def lnk(name, target):
        out.append((name, new_info(name, linkname=target), None))

    # --- debs: binary payloads with their own modes/symlinks -------------------
    debs = [
        'libqrencode4_4.1.1-2+b2_arm64.deb',
        'xfce4-taskmanager_1.5.8-1_arm64.deb',
        'xfce4-screenshooter_1.11.3-1_arm64.deb',
        'xfce4-clipman_1.6.6-1+b2_arm64.deb',
        'xfce4-clipman-plugin_1.6.6-1+b2_arm64.deb',
        'xfce4-docklike-plugin_0.4.3-1_arm64.deb',
    ]
    for deb in debs:
        path = os.path.join(DEBS, deb)
        if not os.path.exists(path):
            raise SystemExit('missing deb: ' + path)
        tf = deb_data_tar(path)
        for ti in tf:
            if ti.isdir():
                continue
            name = norm(ti.name)
            if not name or name.startswith('usr/share/doc/') or name.startswith('usr/share/lintian/'):
                continue
            if ti.issym():
                lnk(name, ti.linkname)
            elif ti.islnk():
                lnk(name, ti.linkname)
            elif ti.isreg():
                data = tf.extractfile(ti).read()
                if name.startswith('usr/bin/') or name.endswith('.so') or '.so.' in name:
                    reg(name, data, mode=0o755)
                else:
                    reg(name, data, mode=0o644)
            else:
                continue

    # --- clipboard manager autostart (the packaged one is Hidden=true) -------
    reg('home/tiny/.config/autostart/tiny-clipman.desktop',
        CLIPMAN_AUTOSTART.encode('utf-8'))

    # --- docklike pin list (plugin id 2, see panel xml) ------------------------
    docklike_rc = (
        '[user]\n'
        # Local fork: the user does not want anything pinned by default.
        'pinned=\n'
        'indicatorStyle=1\n'
        'indicatorOrientation=1\n'
        'onlyDisplayScreen=true\n'
    )
    reg('home/tiny/.config/xfce4/panel/docklike-2.rc', docklike_rc.encode('utf-8'))

    return out


# ------------------------------------------------------------------- main pass

REPLACEMENTS = {
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml': build_panel_xml,
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml': build_shortcuts_xml,
    'opt/tiny/export.sh': build_export_sh,
}


def main():
    src_path, dst_path = sys.argv[1], sys.argv[2]
    replacements = dict((k, v()) for k, v in REPLACEMENTS.items())
    extras = build_extras()
    extra_names = set(name for name, _, _ in extras)

    seen_replaced = set()
    seen_extra = set()
    copied = 0
    src = tarfile.open(src_path, 'r:')
    # The original image was produced by GNU tar (`ustar  \0` magic + @LongLink),
    # so write the same dialect back to stay byte-compatible with proot's tar.
    dst = tarfile.open(dst_path, 'w:', format=tarfile.GNU_FORMAT)
    try:
        for ti in src:
            name = norm(ti.name)
            if name in extra_names:
                seen_extra.add(name)
                continue            # will be appended after the pass
            if name in replacements:
                data = replacements[name]
                info = new_info(name, size=len(data), mode=ti.mode or 0o644)
                info.uid, info.gid = ti.uid, ti.gid
                info.uname, info.gname = ti.uname, ti.gname
                info.mtime = ti.mtime
                dst.addfile(info, io.BytesIO(data))
                seen_replaced.add(name)
                copied += 1
                continue
            if ti.isreg():
                dst.addfile(ti, src.extractfile(ti))
            else:
                dst.addfile(ti)
            copied += 1
        for name, info, data in extras:
            if name in seen_extra:
                continue            # already replaced in place
            dst.addfile(info, io.BytesIO(data) if data is not None else None)
    finally:
        dst.close()
        src.close()

    missing = set(replacements) - seen_replaced
    print('copied members      : %d' % copied)
    print('patched files       : %d (%s)' % (len(seen_replaced), ', '.join(sorted(seen_replaced))))
    print('missing patches     : %s' % (sorted(missing) or 'none'))
    print('appended new members: %d' % len(extras))
    print('output size         : %d bytes' % os.path.getsize(dst_path))


if __name__ == '__main__':
    main()
