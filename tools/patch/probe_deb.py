import sys, os, tarfile, io, lzma, subprocess, tempfile

# Inspect a .deb: control metadata + file list
deb = sys.argv[1]

def read_ar(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'!<arch>\n', d[:8]
    off = 8
    out = []
    while off < len(d):
        hdr = d[off:off + 60]
        if len(hdr) < 60:
            break
        name = hdr[0:16].decode('ascii', 'replace').strip()
        size = int(hdr[48:58].decode('ascii').strip())
        data = d[off + 60: off + 60 + size]
        out.append((name.rstrip('/'), data))
        off += 60 + size + (size % 2)
    return out

parts = read_ar(deb)
for name, data in parts:
    print('PART', name, len(data))

def decomp(name, data):
    if name.endswith('.xz'):
        return lzma.decompress(data)
    if name.endswith('.gz'):
        import gzip
        return gzip.decompress(data)
    if name.endswith('.zst'):
        import zstandard
        return zstandard.ZstdDecompressor().decompressobj().decompress(data)
    return data

for name, data in parts:
    if name.startswith('control.tar'):
        raw = decomp(name, data)
        tf = tarfile.open(fileobj=io.BytesIO(raw))
        for m in tf:
            if m.name.lstrip('./') == 'control':
                print('==== control ====')
                print(tf.extractfile(m).read().decode('utf-8', 'replace'))
    if name.startswith('data.tar'):
        raw = decomp(name, data)
        tf = tarfile.open(fileobj=io.BytesIO(raw))
        print('==== data files ====')
        for m in tf:
            print('%10d %s %s' % (m.size, oct(m.mode), m.name))
