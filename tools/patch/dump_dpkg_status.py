import io, sys, tarfile

path = sys.argv[1]
tf = tarfile.open(path, 'r|*')
want = ('var/lib/dpkg/status',)
exact = sys.argv[2:] if len(sys.argv) > 2 else []
out = None
for ti in tf:
    if ti.name in want or ti.name in exact:
        out = tf.extractfile(ti).read()
        print('FOUND', ti.name, len(out))
        break
if out is None:
    print('NOT FOUND')
    sys.exit(1)
if 'dpkg/status' in (exact[0] if exact else 'dpkg/status'):
    txt = out.decode('utf-8', 'replace')
    names = {}
    cur = None
    for line in txt.splitlines():
        if line.startswith('Package: '):
            cur = line[9:].strip()
        elif cur and line.startswith('Depends: '):
            names[cur] = line[9:].strip()
    print('packages with Depends:', len(names))
    import pickle
    io.open('tools-probe-scripts-deletable\\dpkg_depends.pkl', 'wb').write(pickle.dumps(names))
    print('saved')
