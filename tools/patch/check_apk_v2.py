"""Verify a built APK: zip entry list of interest, rootfs asset integrity, dex strings."""
import hashlib
import sys
import zipfile

apk = sys.argv[1]
out = []

zf = zipfile.ZipFile(apk)
infos = zf.infolist()
out.append('entries: %d' % len(infos))

target = None
for i in infos:
    if i.filename == 'assets/rootfs.tar.zst':
        target = i
out.append('rootfs entry: %r' % (target,))

if target is not None:
    h = hashlib.sha256()
    with zf.open(target) as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    out.append('rootfs method=%d size=%d compress=%d sha256=%s'
               % (target.compress_type, target.file_size, target.compress_size, h.hexdigest().upper()))

dex_names = [i.filename for i in infos if i.filename.startswith('classes') and i.filename.endswith('.dex')]
out.append('dex: %s' % dex_names)
blob = b''
for n in dex_names:
    with zf.open(n) as f:
        blob += f.read()
out.append('dex bytes: %d' % len(blob))

needles = [
    b'mouse_acceleration', b'mouseAccelerationStrength', b'slow_pointer_speed',
    b'scroll_speed', b'cursor_size', b'cursor_tint', b'zoom_mis_touch_guard',
    b'osk_button_ring', b'osk_three_finger_tap', b'open-osk',
    b'dev_options_phantom', b'showZoomMisTouchHint', b'openRemoteKeyboard',
    b'nudgePointer', b'SwitchPreferenceEx', b'ColorPreference', b'setFZoomLocked',
    b'setTint', b'tiny-osk-toggle', b'XF86Launch0',
]
missing = [n.decode() for n in needles if n not in blob]
out.append('missing strings: %s' % (missing or 'NONE'))

print('\n'.join(out))
