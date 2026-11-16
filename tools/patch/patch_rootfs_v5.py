# -*- coding: utf-8 -*-
"""Patch build_rootfs_v2.py for v5:
  * embed hk_layout.py (Hacker's Keyboard port data) and tiny_osk_caret.py
  * autostart the caret bridge
  * stop pinning apps in docklike (user asked for nothing pinned)
"""
import io
import os

P = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py"
src = io.open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- constant paths
old_osk_src = "OSK_SRC = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'osk', 'tiny_osk.py')"
assert old_osk_src in src
src = src.replace(
    old_osk_src,
    old_osk_src + "\n"
    "HK_LAYOUT_SRC = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'osk', 'hk_layout.py')\n"
    "CARET_SRC = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'osk', 'tiny_osk_caret.py')",
    1,
)

# ---------------------------------------------------------- OSK_LAUNCHER rewrite
old_launcher_start = src.index("OSK_LAUNCHER = '''#!/bin/sh")
old_launcher_end = src.index("OSK_TOGGLE = '''#!/bin/sh")
new_launcher = '''OSK_LAUNCHER = \'\'\'#!/bin/sh
# Local fork: start the pink floating on-screen keyboard (single instance).
# Everything is appended to /tmp/.tiny_osk.log so a user can see why it did not
# start (missing python3-gi, no DISPLAY, GTK import error, ...).
LOG=/tmp/.tiny_osk.log
if [ -z "$DISPLAY" ]; then
  for d in :6 :0 :1 :2; do
    if [ -e /tmp/.X11-unix/X${d#:} ]; then export DISPLAY=$d; break; fi
  done
  echo "[$(date)] DISPLAY was empty, guessed $DISPLAY" >> $LOG
fi
export MOZ_ENABLE_WAYLAND=0
if [ -n "$(pgrep -f tiny_osk.py)" ]; then
  echo "[$(date)] already running, toggling" >> $LOG
  exec /usr/local/bin/tiny-osk-toggle
fi
echo "[$(date)] starting osk, DISPLAY=$DISPLAY" >> $LOG
exec python3 /usr/local/share/tiny-osk/tiny_osk.py "$@" >> $LOG 2>&1
\'\'\'

CARET_LAUNCHER = \'\'\'#!/bin/sh
# Local fork: publish the text-caret position so the Android viewer can put the
# "open keyboard" button next to the caret instead of next to the mouse.
LOG=/tmp/.tiny_osk_caret.log
if [ -z "$DISPLAY" ]; then
  for d in :6 :0 :1 :2; do
    if [ -e /tmp/.X11-unix/X${d#:} ]; then export DISPLAY=$d; break; fi
  done
fi
if [ -n "$(pgrep -f tiny_osk_caret.py)" ]; then
  exit 0
fi
exec python3 /usr/local/share/tiny-osk/tiny_osk_caret.py >> $LOG 2>&1
\'\'\'

'''
src = src[:old_launcher_start] + new_launcher + src[old_launcher_end:]

# ------------------------------------------------------------ caret autostart
anchor = "OSK_APP_ENTRY = '''[Desktop Entry]"
caret_autostart = '''CARET_AUTOSTART = \'\'\'[Desktop Entry]
Type=Application
Name=Tiny caret bridge
Comment=报告文本光标位置，供手机端把键盘按钮放在光标旁边
Exec=/usr/local/bin/tiny-osk-caret
Icon=input-keyboard
Terminal=false
NoDisplay=true
OnlyShowIn=XFCE;
X-GNOME-Autostart-enabled=true
\'\'\'

'''
assert anchor in src
src = src.replace(anchor, caret_autostart + anchor, 1)

# -------------------------------------------------------------- embed new files
old_embed = """    osk = io.open(OSK_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/tiny_osk.py', osk, mode=0o755)"""
new_embed = """    osk = io.open(OSK_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/tiny_osk.py', osk, mode=0o755)
    hk = io.open(HK_LAYOUT_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/hk_layout.py', hk, mode=0o644)
    caret = io.open(CARET_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/tiny_osk_caret.py', caret, mode=0o755)
    reg('usr/local/bin/tiny-osk-caret', CARET_LAUNCHER.encode('utf-8'), mode=0o755)
    reg('home/tiny/.config/autostart/tiny-osk-caret.desktop',
        CARET_AUTOSTART.encode('utf-8'))"""
assert old_embed in src
src = src.replace(old_embed, new_embed, 1)

# ------------------------------------------------------ nothing pinned in docklike
old_docklike = """        'pinned=firefox-esr.desktop;thunar.desktop;org.xfce.mousepad.desktop;\\n'"""
new_docklike = """        # Local fork: the user does not want anything pinned by default.
        'pinned=\\n'"""
assert old_docklike in src
src = src.replace(old_docklike, new_docklike, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched build_rootfs_v2.py ->", len(src), "bytes")
for needle in ("HK_LAYOUT_SRC", "CARET_SRC", "tiny-osk-caret", "pinned=\\n'"):
    print("  ", needle, src.count(needle))
