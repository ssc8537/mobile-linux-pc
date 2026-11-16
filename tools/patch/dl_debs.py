import sys, os, urllib.request, json

BASE = "http://ftp.cn.debian.org/debian/pool/main/"
DEBS = [
    ("x", "xfce4-taskmanager", "xfce4-taskmanager_1.5.8-1_arm64.deb"),
    ("x", "xfce4-clipman-plugin", "xfce4-clipman-plugin_1.6.6-1%2Bb2_arm64.deb"),
    ("x", "xfce4-screenshooter", "xfce4-screenshooter_1.11.3-1_arm64.deb"),
    ("p", "pycairo", "python3-cairo_1.28.0-1_arm64.deb"),
    ("p", "pygobject", "python3-gi-cairo_3.50.0-4%2Bb1_arm64.deb"),
]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "build-env-toolchain", "cache-downloads-deletable", "debs")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

for letter, pkg, fname in DEBS:
    dst = os.path.join(OUT, fname.replace("%2B", "+"))
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print(f"  have {os.path.basename(dst)} {os.path.getsize(dst)}")
        continue
    url = f"{BASE}{letter}/{pkg}/{fname}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        with open(dst, "wb") as f:
            f.write(data)
        print(f"  ok   {os.path.basename(dst)} {len(data)}")
    except Exception as e:
        print(f"  FAIL {url}: {e}")
