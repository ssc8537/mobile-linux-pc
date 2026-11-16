import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py"
s = io.open(p, encoding="utf-8", newline="").read()
old = '''OSK_LAUNCHER = \'\'\'#!/bin/sh
# Local fork: start the pink floating on-screen keyboard (single instance).
if [ -n "$(pgrep -f tiny_osk.py)" ]; then
  exec /usr/local/bin/tiny-osk-toggle
fi
exec python3 /usr/local/share/tiny-osk/tiny_osk.py "$@"
\'\'\''''
new = '''OSK_LAUNCHER = \'\'\'#!/bin/sh
# Local fork: start the pink floating on-screen keyboard (single instance).
# Everything is appended to /tmp/.tiny_osk.log so a user can see why it did not
# start (missing python3-gi, no DISPLAY, GTK import error, ...).
LOG=/tmp/.tiny_osk.log
if [ -n "$(pgrep -f tiny_osk.py)" ]; then
  echo "[$(date)] already running, toggling" >> $LOG
  exec /usr/local/bin/tiny-osk-toggle
fi
echo "[$(date)] starting osk, DISPLAY=$DISPLAY" >> $LOG
export MOZ_ENABLE_WAYLAND=0
if [ -z "$DISPLAY" ]; then
  for d in :6 :0 :1 :2; do
    if [ -e /tmp/.X11-unix/X${d#:} ]; then export DISPLAY=$d; break; fi
  done
  echo "[$(date)] DISPLAY was empty, guessed $DISPLAY" >> $LOG
fi
exec python3 /usr/local/share/tiny-osk/tiny_osk.py "$@" >> $LOG 2>&1
\'\'\''''
assert old in s, "launcher block not found"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("launcher logging added")
