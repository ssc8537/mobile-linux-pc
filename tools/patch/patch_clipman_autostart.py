import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py'
s = io.open(p, encoding='utf-8', newline='').read()
old = "    reg('home/tiny/.config/autostart/tiny-osk.desktop', OSK_AUTOSTART.encode('utf-8'))\n    reg('usr/share/applications/tiny-osk.desktop', OSK_APP_ENTRY.encode('utf-8'))"
assert old in s, 'anchor missing'
new = (old + "\n"
       "    # --- clipboard manager autostart (the packaged one is Hidden=true) -------\n"
       "    reg('home/tiny/.config/autostart/tiny-clipman.desktop',\n"
       "        CLIPMAN_AUTOSTART.encode('utf-8'))")
s = s.replace(old, new, 1)
# define the constant next to OSK_AUTOSTART
old2 = 'OSK_AUTOSTART = '
i = s.find(old2)
assert i > 0, 'OSK_AUTOSTART def missing'
add = (
 "CLIPMAN_AUTOSTART = (\n"
 "    '[Desktop Entry]\\n'\n"
 "    'Type=Application\\n'\n"
 "    'Name=Clipman\\n'\n"
 "    'Comment=Clipboard manager (Windows-style Win+V history)\\n'\n"
 "    'Exec=xfce4-clipman\\n'\n"
 "    'Icon=xfce4-clipman-plugin\\n'\n"
 "    'Terminal=false\\n'\n"
 "    'NoDisplay=true\\n'\n"
 "    'X-GNOME-Autostart-enabled=true\\n'\n"
 ")\n\n"
)
s = s[:i] + add + s[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('clipman autostart added')
