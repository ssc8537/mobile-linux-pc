import tarfile, sys, re
tar = tarfile.open(sys.argv[1], 'r:')
names = {m.name: m for m in tar.getmembers()}
for p in ('usr/bin/xfce4-popup-clipman','usr/bin/xfce4-clipman-history'):
    d = tar.extractfile(names[p]).read()
    strs = set(re.findall(rb'[ -~]{5,60}', d))
    interesting = sorted(s.decode() for s in strs if b'clipman' in s.lower() or b'histor' in s.lower())
    print('==', p, len(interesting))
    for s in interesting[:25]:
        print('   ', s)
