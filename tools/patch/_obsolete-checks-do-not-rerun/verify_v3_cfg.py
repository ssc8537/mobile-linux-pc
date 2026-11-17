import tarfile, sys
tar = tarfile.open(sys.argv[1], 'r:')
names = {m.name: m for m in tar.getmembers()}
p = 'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml'
x = tar.extractfile(names[p]).read().decode()
i = x.find('plugin-2"')
print('--- panel plugin-2 ---')
print(x[i-20:i+260])
s = 'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml'
k = tar.extractfile(names[s]).read().decode()
print('XF86Launch0 count:', k.count('XF86Launch0'))
print('tiny-osk-toggle count:', k.count('tiny-osk-toggle'))
