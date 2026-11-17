import io
import os

def _find_ws():
    env = os.environ.get('TC_ROOT')
    if env:
        return env
    _d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(_d, 'build-env-toolchain')) or os.path.isdir(
            os.path.join(_d, 'source', 'app')
        ):
            return _d
        _p = os.path.dirname(_d)
        if _p == _d:
            return os.path.dirname(os.path.abspath(__file__))
        _d = _p


WS = _find_ws()
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

p = os.path.join(WS, 'tools-probe-scripts-deletable', 'build_rootfs_v2.py')
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
