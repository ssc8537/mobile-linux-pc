import io, sys, lzma, tarfile, os

def deb_payload(path):
    """Return (control_text, [tarinfo names]) reading the deb's ar archive."""
    data = io.open(path, 'rb').read()
    assert data[:8] == b'!<arch>\n', 'not an ar archive'
    pos = 8
    members = {}
    while pos < len(data):
        hdr = data[pos:pos + 60]
        if len(hdr) < 60:
            break
        name = hdr[0:16].decode('ascii', 'replace').strip().rstrip('/')
        size = int(hdr[48:58].decode('ascii').strip())
        body = data[pos + 60: pos + 60 + size]
        members[name] = body
        pos += 60 + size
        if pos % 2:
            pos += 1
    return members

def walk_tar(raw):
    """Yield (TarInfo, bytes|None) from an xz/gz/zst tar payload."""
    tf = tarfile.open(fileobj=io.BytesIO(raw), mode='r:*')
    for ti in tf:
        yield ti, (tf.extractfile(ti).read() if ti.isreg() else None)

for deb in sys.argv[1:]:
    print('=' * 70)
    print(deb)
    m = deb_payload(deb)
    print('members:', list(m.keys()))
    ctrl = None
    for key in ('control.tar.xz', 'control.tar.gz', 'control.tar.zst', 'control.tar'):
        if key in m:
            ctrl = m[key]
            break
    if ctrl:
        for ti, body in walk_tar(ctrl):
            if ti.name.endswith('./control') or ti.name == 'control':
                txt = body.decode('utf-8', 'replace')
                for line in txt.splitlines():
                    if line.startswith(('Package:', 'Version:', 'Depends:', 'Installed-Size:')):
                        print(' ', line)
    data_name = None
    for key in ('data.tar.xz', 'data.tar.gz', 'data.tar.zst', 'data.tar'):
        if key in m:
            data_name = key
            break
    print('  payload:', data_name)
    if data_name:
        n = 0
        for ti, body in walk_tar(m[data_name]):
            if ti.isreg():
                n += 1
                if n <= 40:
                    print('   %8d %s' % (ti.size, ti.name))
        print('  ... total regular files:', n)
