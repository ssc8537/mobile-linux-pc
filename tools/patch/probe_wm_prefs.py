import sys, tarfile
import zstandard

IMG = sys.argv[1]
WANT = [
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml',
    'home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml',
    'usr/share/applications/firefox-esr.desktop',
]
dctx = zstandard.ZstdDecompressor()
with open(IMG, 'rb') as fh:
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            if m.name in WANT and m.isfile():
                data = tf.extractfile(m).read().decode('utf-8', 'replace')
                print('=' * 25, m.name, m.size)
                print(data[:9000])
                WANT.remove(m.name)
                if not WANT:
                    break
print('MISSING:', WANT)
