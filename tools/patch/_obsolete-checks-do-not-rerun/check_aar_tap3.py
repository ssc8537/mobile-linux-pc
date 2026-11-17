import zipfile, sys
aar = sys.argv[1]
z = zipfile.ZipFile(aar)
cj = z.read('classes.jar')
import io
z2 = zipfile.ZipFile(io.BytesIO(cj))
names = z2.namelist()
target = [n for n in names if n.endswith('Dispatcher$Config.class')]
print('Config classes:', target)
data = b''
for n in target:
    data += z2.read(n)
print('oskThreeFingerTap in Config:', b'oskThreeFingerTap' in data)
print('total classes:', len(names))
