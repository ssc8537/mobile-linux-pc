import sys, tarfile, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyz2'))
import zstandard

IMG = r'Linux-小小容器\04-下载缓存-可删除\xfce-zh-20260808-160507.tar.zst'

targets = {
    'usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libtasklist.so': ['pin', 'Pin', 'launcher', 'docklike'],
    'usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/liblauncher.so': ['desktop', 'Desktop', 'items'],
    'usr/bin/xfce4-panel': ['pin', 'docklike'],
}

blobs = {}
with open(IMG, 'rb') as f:
    with zstandard.ZstdDecompressor().stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            if m.name in targets:
                blobs[m.name] = tf.extractfile(m).read()
            if len(blobs) == len(targets):
                break

for name, pats in targets.items():
    b = blobs.get(name)
    print(f'\n===== {name} ({len(b) if b else 0} bytes) =====')
    if not b:
        print('MISSING')
        continue
    strings = re.findall(rb'[ -~]{4,}', b)
    txt = [s.decode('ascii', 'replace') for s in strings]
    for p in pats:
        hits = sorted({t for t in txt if p in t})
        print(f'-- pattern {p!r}: {len(hits)} unique')
        for h in hits[:40]:
            print('   ', h)
