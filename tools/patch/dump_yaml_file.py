import sys, tarfile, io, os
import zstandard as zstd

IMG = sys.argv[1]
OUT = sys.argv[2]
with open(IMG, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            if m.name.endswith(".tiny.yaml"):
                data = tf.extractfile(m).read()
                with open(OUT, 'wb') as o:
                    o.write(data)
                print(f"wrote {len(data)} bytes")
                break
