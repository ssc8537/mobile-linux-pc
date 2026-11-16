import zipfile, io, sys
aar = sys.argv[1]
z = zipfile.ZipFile(aar)
z2 = zipfile.ZipFile(io.BytesIO(z.read('classes.jar')))
for n in z2.namelist():
    if 'Dispatcher' in n:
        d = z2.read(n)
        print(n, len(d), 'oskThreeFingerTap' in str(d) or b'oskThreeFingerTap' in d)
