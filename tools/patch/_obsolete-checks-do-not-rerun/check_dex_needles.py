import zipfile, sys
apk = sys.argv[1]
z = zipfile.ZipFile(apk)
blob = b''
for n in z.namelist():
    if n.endswith('.dex'):
        blob += z.read(n)
needles = [b'getOskThreeFingerTap', b'oskThreeFingerTap', b'_open_settings' , b'mouseAcceleration',
           b'cursorTint', b'zoomMisTouchGuard', b'dev_options_phantom', b'tiny-osk.conf']
for n in needles:
    print(n.decode(), n in blob)
