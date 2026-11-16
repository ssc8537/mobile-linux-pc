import sys, tarfile, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyz2'))
import zstandard

IMG = r'Linux-小小容器\04-下载缓存-可删除\xfce-zh-20260808-160507.tar.zst'
want = {
    'etc/xdg/xfce4/panel/default.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml',
    'opt/tiny/export.sh',
}
out = {}
with open(IMG, 'rb') as f:
    with zstandard.ZstdDecompressor().stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            if m.name in want:
                out[m.name] = tf.extractfile(m).read().decode('utf-8', 'replace')
            if len(out) == len(want):
                break

for k in want:
    print(f'\n########## {k} ##########')
    print(out.get(k, '(MISSING)'))
