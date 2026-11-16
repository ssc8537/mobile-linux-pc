import io, os, sys, tarfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
t = os.path.join(R, "build-env-toolchain", "cache-downloads-deletable", "rootfs-v7.tar")
names = []
with tarfile.open(t, "r:", encoding="utf-8") as tf:
    for m in tf:
        names.append(m.name)
print("members:", len(names))
bad = [n for n in names if "tiny_osk" in n or "tiny-osk" in n or "hk_layout" in n]
print("osk members:", bad)
for want in ("usr/bin/xfce4-taskmanager", "usr/bin/xfce4-screenshooter",
             "usr/bin/xfce4-clipman", "usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libdocklike.so",
             "home/tiny/.config/xfce4/panel/docklike-2.rc",
             "home/tiny/.config/autostart/tiny-clipman.desktop",
             "opt/tiny/export.sh"):
    print(("OK  " if want in names else "MISS"), want)
