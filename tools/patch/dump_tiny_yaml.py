import sys, tarfile
import zstandard

path = sys.argv[1]
out = sys.argv[2]
dctx = zstandard.ZstdDecompressor()
with open(path, 'rb') as fh:
    with dctx.stream_reader(fh) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tf:
            for m in tf:
                if m.name.endswith('.tiny.yaml'):
                    data = tf.extractfile(m).read()
                    with open(out, 'wb') as f:
                        f.write(data)
                    print("saved", m.name, len(data), "bytes")
                    break
