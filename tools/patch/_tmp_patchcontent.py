import tarfile, os, io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = os.path.join(R, r"build-env-toolchain\cache-downloads-deletable\rootfs-patch-v5.tar")
want = {
 "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml": ["docklike", "plugin-2"],
 "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml":
    ["XF86Launch0", "Super>v", "Super>Shift>v", "xfce4-popup-clipman", "xfce4-clipman-history", "xfce4-taskmanager"],
 "opt/tiny/export.sh": ["apt clean", "mozilla", "tar --zstd"],
 "home/tiny/.config/xfce4/panel/docklike-2.rc": ["firefox-esr.desktop", "thunar.desktop", "mousepad"],
 "usr/local/bin/tiny-osk-toggle": ["pgrep", "nohup", "tiny_osk_toggle"],
 "usr/local/bin/tiny-osk": ["X11-unix", "tiny_osk.log"],
 "usr/local/share/tiny-osk/tiny_osk.py": ["_open_settings", "_ensure_display", "_log", "tiny-osk.conf"],
}
out = []
with tarfile.open(p) as t:
    for m in t:
        if m.name in want and m.isfile():
            s = t.extractfile(m).read().decode("utf-8", "ignore")
            for k in want[m.name]:
                out.append("%-42s %-22s %s" % (m.name.split("/")[-1], k, k in s))
io.open(os.path.join(R, r"tools-probe-scripts-deletable\_patch_verify.txt"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
