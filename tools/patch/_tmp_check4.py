import zipfile, hashlib, re, io, sys
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk'
z = zipfile.ZipFile(p)
names = z.namelist()
print('entries', len(names))
for n in ('assets/rootfs.tar.zst', 'assets/rootfs.patch.tar.zst', 'assets/rootfs.stamp'):
    if n in names:
        i = z.getinfo(n)
        data_hash = hashlib.sha256()
        with z.open(n) as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                data_hash.update(chunk)
        print(n, 'len', i.file_size, 'clen', i.compress_size, 'method', i.compress_type, 'sha', data_hash.hexdigest()[:16])
    else:
        print(n, 'MISSING')
needles = ['oskPointerButton', 'cursorTintEnabled', 'osk_pointer_button', 'cursor_tint_enabled',
           'ValueLabelPreference', 'OskBridge', 'zoom_mis_touch_guard', 'dev_options_phantom',
           'applyImagePatch', 'tc4_reimport_patch', 'tiny-osk-toggle', 'setFZoomLocked',
           'positionOskButton', 'showZoomMisTouchHint', 'oskTriggerPath', 'tiny_osk.log']
blob = b''
for n in names:
    if n.startswith('classes') and n.endswith('.dex'):
        blob += z.read(n)
        print('dex', n, z.getinfo(n).file_size)
for nd in needles:
    print('  %-24s %s' % (nd, nd.encode() in blob))
print('stamp content', z.read('assets/rootfs.stamp').decode().strip())
