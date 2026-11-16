import sys, tarfile, io
import zstandard as zstd

IMG = sys.argv[1]
with open(IMG, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            if m.name.endswith(".tiny.yaml"):
                data = tf.extractfile(m).read()
                sys.stdout.write(data.decode('utf-8', 'replace'))
                break
