import sys, tarfile
import zstandard

path = sys.argv[1]
want = ['opt/tiny/export.sh']
dctx = zstandard.ZstdDecompressor()
found = {}
n = 0
with open(path, 'rb') as fh:
    with dctx.stream_reader(fh) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tf:
            for m in tf:
                n += 1
                name = m.name.lstrip('./')
                if name in want:
                    data = tf.extractfile(m).read().decode('utf-8', 'replace')
                    found[name] = data
                    if len(found) == len(want):
                        break
for k, v in found.items():
    print("=" * 20, k, "=" * 20)
    print(v)
print("scanned", n, "entries; found:", list(found))
