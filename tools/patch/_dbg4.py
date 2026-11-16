import os, tarfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
t = os.path.join(R, "build-env-toolchain", "cache-downloads-deletable", "rootfs-v7.tar")
want = {
 "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml": ["XF86Launch0", "tiny-osk", "xfce4-popup-clipman", "xfce4-clipman-history", "xfce4-taskmanager"],
 "home/tiny/.config/xfce4/panel/docklike-2.rc": ["pinned="],
 "opt/tiny/export.sh": ["apt clean", "mozilla", "tar --zstd"],
 "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml": ["docklike", "tasklist"],
}
with tarfile.open(t, "r:", encoding="utf-8") as tf:
    for m in tf:
        if m.name in want:
            data = tf.extractfile(m).read().decode("utf-8", "replace")
            print("---", m.name, len(data))
            for token in want[m.name]:
                print("   %-22s %s" % (token, token in data))
            if m.name.endswith("docklike-2.rc"):
                print("   BODY:", repr(data))
