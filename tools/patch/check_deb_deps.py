import io, os, re, pickle, sys, lzma, tarfile

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
IDX = pickle.load(io.open(ROOT + r'\tools-probe-scripts-deletable\image_index.pkl', 'rb'))
installed = set(IDX['depends'].keys())
paths = IDX['paths']
lowerbases = set(p.rsplit('/', 1)[-1].lower() for p in paths)

DEBDIR = ROOT + r'\build-env-toolchain\cache-downloads-deletable\debs'


def ar_members(path):
    data = io.open(path, 'rb').read()
    pos = 8
    out = {}
    while pos < len(data):
        hdr = data[pos:pos + 60]
        if len(hdr) < 60:
            break
        name = hdr[0:16].decode('ascii', 'replace').strip().rstrip('/')
        size = int(hdr[48:58].decode('ascii').strip())
        out[name] = data[pos + 60:pos + 60 + size]
        pos += 60 + size
        if pos % 2:
            pos += 1
    return out


def control_of(deb):
    m = ar_members(deb)
    key = [k for k in m if k.startswith('control.tar')][0]
    tf = tarfile.open(fileobj=io.BytesIO(m[key]), mode='r:*')
    for ti in tf:
        if ti.name.endswith('control'):
            return tf.extractfile(ti).read().decode('utf-8', 'replace')
    return ''


def parse_deps(txt):
    for line in txt.splitlines():
        if line.startswith('Depends:'):
            raw = line[8:].strip()
            deps = []
            for part in raw.split(','):
                name = part.strip().split(' ')[0].split('(')[0].strip()
                if name:
                    deps.append(name)
            return deps
    return []


def dep_ok(name):
    """A dependency is satisfied by an installed package whose name matches,
    or by an existing shared library file."""
    if name in installed:
        return True
    # allow virtual/ABI names like libc6 -> libc.so.6
    m = re.match(r'^lib(.+?)(\d)$', name)
    if m:
        stem = m.group(1).replace('-', '_')
        return any(b.startswith('lib' + stem) for b in lowerbases)
    return False


for fn in sorted(os.listdir(DEBDIR)):
    if not fn.endswith('.deb'):
        continue
    ctrl = control_of(os.path.join(DEBDIR, fn))
    deps = parse_deps(ctrl)
    missing = [d for d in deps if not dep_ok(d)]
    ver = re.search(r'Version: (.+)', ctrl)
    print('%-58s %-14s deps=%-2d missing=%s' % (
        fn, ver.group(1).strip() if ver else '?', len(deps),
        missing if missing else 'NONE'))
