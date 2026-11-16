# -*- coding: utf-8 -*-
"""Strip every OSK/caret/Hacker's-Keyboard artefact from the rootfs builder."""
import io
import re

F = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py"
raw = io.open(F, "r", encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
log = []


def cut(start_marker, end_marker, label):
    global src
    a = src.index(start_marker)
    b = src.index(end_marker, a)
    src = src[:a] + src[b:]
    log.append("%s: removed %d chars" % (label, b - a))


# 1) docstring mention
src = src.replace(
    "clipman + screenshooter + libqrencode4 + the pink floating OSK, keeping every original",
    "clipman + screenshooter + libqrencode4, keeping every original")

# 2) source constants
src = src.replace(
    "OSK_SRC = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'osk', 'tiny_osk.py')\n"
    "HK_LAYOUT_SRC = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'osk', 'hk_layout.py')\n"
    "CARET_SRC = os.path.join(ROOT, 'tools-probe-scripts-deletable', 'osk', 'tiny_osk_caret.py')\n",
    "")
log.append("OSK_SRC/HK_LAYOUT_SRC/CARET_SRC: removed")

# 3) XF86Launch0 shortcut + its comment
src = src.replace(
    "    src = src.replace(\n"
    "        anchor_default,\n"
    "        anchor_default + '      <property name=\"XF86Launch0\" type=\"empty\"/>\\n', 1)\n",
    "")
src = src.replace(
    "        + '      <!-- Local fork: XF86Launch0 opens/closes the pink floating keyboard -->\\n'\n"
    "        + '      <property name=\"XF86Launch0\" type=\"string\" value=\"tiny-osk-toggle\"/>\\n'\n",
    "")
log.append("XF86Launch0 shortcut: removed")
if 'value="tiny-osk-toggle"' in src:
    raise SystemExit("XF86Launch0 shortcut binding still present")

# 4) shell script constants: OSK_LAUNCHER .. CARET_LAUNCHER .. OSK_TOGGLE
cut("OSK_LAUNCHER = '''#!/bin/sh", "CLIPMAN_AUTOSTART = (", "OSK_LAUNCHER/CARET_LAUNCHER/OSK_TOGGLE")

# 5) desktop entries: OSK_AUTOSTART .. OSK_APP_ENTRY (they sit between CLIPMAN_AUTOSTART and build_extras)
cut("OSK_AUTOSTART = '''[Desktop Entry]", "\n\ndef build_extras():", "OSK_AUTOSTART/CARET_AUTOSTART/OSK_APP_ENTRY")

# 6) build_extras registrations
old_block = """    # --- pink floating OSK -----------------------------------------------------
    osk = io.open(OSK_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/tiny_osk.py', osk, mode=0o755)
    hk = io.open(HK_LAYOUT_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/hk_layout.py', hk, mode=0o644)
    caret = io.open(CARET_SRC, 'rb').read()
    reg('usr/local/share/tiny-osk/tiny_osk_caret.py', caret, mode=0o755)
    reg('usr/local/bin/tiny-osk-caret', CARET_LAUNCHER.encode('utf-8'), mode=0o755)
    reg('home/tiny/.config/autostart/tiny-osk-caret.desktop',
        CARET_AUTOSTART.encode('utf-8'))
    reg('usr/local/bin/tiny-osk', OSK_LAUNCHER.encode('utf-8'), mode=0o755)
    reg('usr/local/bin/tiny-osk-toggle', OSK_TOGGLE.encode('utf-8'), mode=0o755)
    reg('home/tiny/.config/autostart/tiny-osk.desktop', OSK_AUTOSTART.encode('utf-8'))
    reg('usr/share/applications/tiny-osk.desktop', OSK_APP_ENTRY.encode('utf-8'))
"""
if old_block not in src:
    raise SystemExit("build_extras OSK registration block not found verbatim")
src = src.replace(old_block, "")
log.append("build_extras: OSC registrations removed")

for token in ("OSK_LAUNCHER", "OSK_TOGGLE", "CARET_LAUNCHER", "CARET_AUTOSTART",
              "OSK_AUTOSTART", "OSK_APP_ENTRY", "hk_layout", "tiny_osk"):
    if token in src:
        survivors = [l for l in src.splitlines() if token in l]
        raise SystemExit("%s still present: %s" % (token, survivors[:3]))

out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
log.append("written %d bytes" % len(out.encode("utf-8")))
for l in log:
    print(l)
