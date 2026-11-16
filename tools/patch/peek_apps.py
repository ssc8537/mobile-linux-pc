import sys, tarfile
sys.path.insert(0, r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\_tools\pyz2")
import zstandard

PATH = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\Linux-小小容器\04-下载缓存-可删除\xfce-zh-20260808-160507.tar.zst"
PREFIXES = [
    "usr/share/applications/",
    "home/tiny/Desktop",
    "home/tiny/.config/autostart",
    "home/tiny/.config/xfce4/panel/",
    "usr/share/xfce4/panel/",
    "home/tiny/.local/share/applications",
]
LIMIT = 400

count = 0
with open(PATH, "rb") as fh:
    dctx = zstandard.ZstdDecompressor()
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode="r|")
        for m in tf:
            n = m.name
            if n.startswith("./"):
                n = n[2:]
            if any(n.startswith(p) for p in PREFIXES):
                print(f"{m.size:>9} {n}")
                count += 1
                if count >= LIMIT:
                    print("... truncated")
                    break
print("TOTAL", count)
