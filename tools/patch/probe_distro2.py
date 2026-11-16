import sys, tarfile
import zstandard

path = sys.argv[1]
dctx = zstandard.ZstdDecompressor()
hits = []
osr = {}
n = 0
with open(path, 'rb') as fh:
    with dctx.stream_reader(fh) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tf:
            for m in tf:
                n += 1
                name = m.name.lstrip('./')
                if name in ('etc/os-release', 'usr/lib/os-release', 'etc/lsb-release') and m.isfile():
                    osr[name] = tf.extractfile(m).read().decode('utf-8', 'replace')
                if 'xfce4-panel' in name or 'panel/plugins' in name:
                    if n % 1 == 0 and len(hits) < 60:
                        hits.append((name, m.type.decode('latin1'), m.size))
print("scanned", n)
for k, v in osr.items():
    print("---", k, "---")
    print(v)
print("=== xfce4-panel related (first 60) ===")
for h in hits:
    print("   ", h)
