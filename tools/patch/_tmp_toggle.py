import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py"
s = io.open(p, encoding="utf-8", newline="").read()
old = '''OSK_TOGGLE = \'\'\'#!/bin/sh
# Local fork: toggle the floating keyboard without touching the X keymap.
: > /tmp/.tiny_osk_toggle
\'\'\''''
new = '''OSK_TOGGLE = \'\'\'#!/bin/sh
# Local fork: toggle the floating keyboard without touching the X keymap.
# If the keyboard process is not running yet (autostart failed, or the user
# closed it), start it first instead of writing a trigger nobody reads.
LOG=/tmp/.tiny_osk.log
echo "[$(date)] toggle requested" >> $LOG
if ! pgrep -f tiny_osk.py >/dev/null 2>&1; then
  echo "[$(date)] not running, launching" >> $LOG
  nohup /usr/local/bin/tiny-osk >/dev/null 2>&1 &
  sleep 1
fi
: > /tmp/.tiny_osk_toggle
\'\'\''''
assert old in s, "toggle block not found"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("toggle fallback added")
