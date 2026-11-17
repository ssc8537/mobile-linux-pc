import tarfile, sys
tar = tarfile.open(sys.argv[1], 'r:')
names = {m.name: m for m in tar.getmembers()}
s = 'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml'
k = tar.extractfile(names[s]).read().decode('utf-8')
for line in k.split('\n'):
    if 'clipman' in line or 'Super>v' in line or 'taskmanager' in line:
        print(line.strip())
