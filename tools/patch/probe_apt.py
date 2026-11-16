import sys, tarfile, io
import zstandard

IMG = sys.argv[1]
PATTERNS = sys.argv[2].split(',')

dctx = zstandard.ZstdDecompressor()
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n = m.name
            if any(n == p or n.startswith(p) for p in PATTERNS):
                if m.isfile() and m.size < 200000:
                    data = tf.extractfile(m).read()
                    print('=' * 20, n, m.size, oct(m.mode), m.uid, m.gid)
                    try:
                        print(data.decode('utf-8', 'replace')[:4000])
                    except Exception as e:
                        print('decode err', e)
                else:
                    print('---', n, m.size, 'isfile' if m.isfile() else 'dir/other')
