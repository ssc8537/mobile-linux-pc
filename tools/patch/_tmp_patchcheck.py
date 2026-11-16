import tarfile, os
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = os.path.join(R, r"build-env-toolchain\cache-downloads-deletable\rootfs-patch-v5.tar")
need = ["usr/bin/xfce4-taskmanager", "usr/bin/xfce4-screenshooter", "usr/bin/xfce4-clipman",
        "usr/lib/aarch64-linux-gnu/xfce4/panel/plugins/libdocklike.so",
        "usr/local/share/tiny-osk/tiny_osk.py", "usr/local/bin/tiny-osk",
        "usr/local/bin/tiny-osk-toggle", "usr/local/bin/tiny-osk",
        "home/tiny/.config/xfce4/panel/docklike-2.rc",
        "home/tiny/.config/autostart/tiny-osk.desktop",
        "home/tiny/.config/autostart/tiny-clipman.desktop",
        "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml",
        "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml",
        "opt/tiny/export.sh"]
found = {}
with tarfile.open(p) as t:
    for m in t:
        found[m.name] = m.size
print("patch members:", len(found))
for n in need:
    print("  %-70s %s" % (n, found.get(n, "MISSING")))
