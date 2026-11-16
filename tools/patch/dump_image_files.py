import io, os, sys
sys.path.insert(0, r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\pyz2')
import zstandard, tarfile

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
IMG = ROOT + r'\build-env-toolchain\cache-downloads-deletable\xfce-zh-20260808-160507.tar.zst'
OUT = ROOT + r'\tools-probe-scripts-deletable\imagedump'
os.makedirs(OUT, exist_ok=True)

WANT = [
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml',
    'etc/xdg/xfce4/panel/default.xml',
    'opt/tiny/export.sh',
    '.tiny.yaml',
]
want = set(WANT)
with io.open(IMG, 'rb') as f:
    dr = zstandard.ZstdDecompressor()
    with dr.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for ti in tf:
            if ti.name in want and ti.isreg():
                data = tf.extractfile(ti).read()
                name = ti.name.replace('/', '__')
                io.open(os.path.join(OUT, name), 'wb').write(data)
                want.discard(ti.name)
                print('dumped', ti.name, len(data))
            if not want:
                break
print('missing', want)
