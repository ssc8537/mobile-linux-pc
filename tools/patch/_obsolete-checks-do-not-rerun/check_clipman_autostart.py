import tarfile, sys
tar = tarfile.open(sys.argv[1], 'r:')
names = {m.name: m for m in tar.getmembers()}
p = 'etc/xdg/autostart/xfce4-clipman-plugin-autostart.desktop'
txt = tar.extractfile(names[p]).read().decode('utf-8')
for line in txt.splitlines():
    if line.startswith(('Exec','Hidden','OnlyShowIn','NoDisplay','Name=')):
        print(line.encode('ascii','replace').decode('ascii'))
