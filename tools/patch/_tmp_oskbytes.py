import io, sys, tarfile

T = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\cache-downloads-deletable\rootfs-v5.tar"
WANT = [
    'usr/local/bin/tiny-osk',
    'usr/local/bin/tiny-osk-toggle',
    'home/tiny/.config/autostart/tiny-osk.desktop',
    'usr/share/applications/tiny-osk.desktop',
    'home/tiny/.config/xfce4/panel/docklike-2.rc',
]

with tarfile.open(T, 'r|') as tf:
    for m in tf:
        n = m.name[2:] if m.name.startswith('./') else m.name
        if n in WANT:
            f = tf.extractfile(m)
            data = f.read() if f else b''
            print('=' * 60)
            print(n, 'mode=%o' % m.mode, 'size=%d' % len(data),
                  'CRLF=%d' % data.count(b'\r\n'), 'LF=%d' % data.count(b'\n'))
            print(data.decode('utf-8', 'replace'))
