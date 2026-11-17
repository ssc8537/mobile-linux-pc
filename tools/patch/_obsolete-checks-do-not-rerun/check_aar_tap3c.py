import zipfile, io, sys, re
aar = sys.argv[1]
z = zipfile.ZipFile(aar)
z2 = zipfile.ZipFile(io.BytesIO(z.read('classes.jar')))
for n in z2.namelist():
    if 'Dispatcher' in n:
        d = z2.read(n)
        hits = set(re.findall(rb'[A-Za-z]*[Oo]sk[A-Za-z]*', d))
        print(n, sorted(x.decode() for x in hits))
