import sys, tarfile, re
import zstandard as zstd

IMG = sys.argv[1]
KEYS = ("terminal/accels.scm", "xfce4-terminal", "xfce4-screenshooter",
        "xfce4-taskmanager", "xfce4-clipman", "xfce4-dict", "orage",
        "xfce4-power-manager", "light-locker", "xscreensaver",
        "autostart", "xfce4-session.rc", "xfwm4.xml",
        "libXtst", "libxdo", "xdotool", "onboard")

hits = {}
autostart_entries = []
session_rc = None

with open(IMG, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n = m.name
            for k in KEYS:
                if k in n:
                    hits.setdefault(k, []).append((n, m.size))
            if "/.config/autostart/" in n:
                autostart_entries.append((n, m.size))
            if n.endswith("xfce4-session/xfce4-session.rc"):
                fh = tf.extractfile(m)
                if fh:
                    session_rc = fh.read().decode('utf-8', 'replace')

print("== key path hits ==")
for k in KEYS:
    v = hits.get(k, [])
    if not v:
        print(f"  {k:28s} MISSING")
    else:
        for n, s in v[:6]:
            print(f"  {k:28s} {s:>9} {n}")

print("== autostart entries ==")
if not autostart_entries:
    print("  (none)")
for n, s in autostart_entries[:20]:
    print(f"  {s:>8} {n}")

print("== xfce4-session.rc ==")
print(session_rc if session_rc else "  (not found)")
