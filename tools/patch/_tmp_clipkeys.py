import tarfile, os
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = os.path.join(R, r"build-env-toolchain\cache-downloads-deletable\rootfs-patch-v5.tar")
name = "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml"
with tarfile.open(p) as t:
    s = t.extractfile(name).read().decode("utf-8", "ignore")
for line in s.splitlines():
    if "clipman" in line:
        print(repr(line))
