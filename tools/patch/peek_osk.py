import tarfile, sys, io
p = sys.argv[1]
tar = tarfile.open(p, 'r:')
m = tar.getmember('usr/local/share/tiny-osk/tiny_osk.py')
data = tar.extractfile(m).read().decode('utf-8')
print('size', m.size)
for needle in ('_open_settings', 'CONFIG_FILE', 'save_settings', 'key_height', 'b_settings'):
    print(needle, needle in data)
