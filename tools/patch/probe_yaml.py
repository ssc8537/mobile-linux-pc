import sys, tarfile
import zstandard

IMG = sys.argv[1]
dctx = zstandard.ZstdDecompressor()
want_yaml = True
sudo_like = []
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n = m.name
            if n == '.tiny.yaml' and want_yaml and m.isfile():
                data = tf.extractfile(m).read().decode('utf-8', 'replace')
                want_yaml = False
                print('##### .tiny.yaml (%d bytes) #####' % len(data))
                print(data)
            elif n in ('usr/bin/sudo', 'usr/bin/apt', 'usr/bin/xfconf-query',
                       'usr/bin/xfce4-panel', 'usr/bin/pkexec', 'usr/bin/apt-get'):
                sudo_like.append((n, m.size, oct(m.mode)))
print('##### binaries #####')
for x in sudo_like:
    print(x)
