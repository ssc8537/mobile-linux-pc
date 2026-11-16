import io, sys, tarfile
import zstandard

path = sys.argv[1]
dctx = zstandard.ZstdDecompressor()
count = 0
tiny = None
first = []
with open(path, 'rb') as fh:
    with dctx.stream_reader(fh) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tf:
            for m in tf:
                count += 1
                if count <= 15:
                    first.append(("%-12s %10d %s" % ('dir' if m.isdir() else 'file', m.size, m.name)))
                base = m.name.rsplit('/', 1)[-1]
                if base in ('.tiny.yaml', 'tiny.yaml', '.tiny.yml'):
                    tiny = (m.name, tf.extractfile(m).read().decode('utf-8', 'replace'))
                if count >= 400 and tiny is not None:
                    break
print("scanned entries:", count)
print("--- first entries ---")
for x in first:
    print(x)
print("--- tiny config ---")
if tiny:
    print("FOUND at", tiny[0])
    print(tiny[1][:3000])
else:
    print("NOT FOUND in first", count, "entries")
