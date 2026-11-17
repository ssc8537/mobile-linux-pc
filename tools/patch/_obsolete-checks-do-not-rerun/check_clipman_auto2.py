import tarfile, sys
tar = tarfile.open(sys.argv[1], 'r:')
names = {m.name: m for m in tar.getmembers()}
p = 'home/tiny/.config/autostart/tiny-clipman.desktop'
m = names.get(p)
print('exists', bool(m), m.size if m else '')
if m:
    print(tar.extractfile(m).read().decode('ascii'))
