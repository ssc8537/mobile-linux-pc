import sys, tarfile, io
sys.path.insert(0, r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\_tools\pyz2")
import zstandard

PATH = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\Linux-小小容器\04-下载缓存-可删除\xfce-zh-20260808-160507.tar.zst"

wanted_prefixes = [
    "opt/tiny/",
    "home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/",
    "home/tiny/.config/xfce4/panel/",
    "home/tiny/Desktop/",
    "home/tiny/.config/autostart/",
]

names = []
sizes = {}
with open(PATH, "rb") as fh:
    dctx = zstandard.ZstdDecompressor()
    with dctx.stream_reader(fh) as r:
        tf = tarfile.open(fileobj=r, mode="r|")
        for m in tf:
            n = m.name
            if n.startswith("./"):
                n = n[2:]
            for p in wanted_prefixes:
                if n.startswith(p):
                    names.append((n, m.size, m.type))
                    break

for n, s, t in names:
    print(f"{s:>10} {t} {n}")
print("TOTAL", len(names))
