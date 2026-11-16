import io, os, tarfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
D = os.path.join(R, "build-env-toolchain", "cache-downloads-deletable")

def names(p):
    out = set()
    with tarfile.open(p, "r:", encoding="utf-8") as tf:
        for m in tf:
            out.add(m.name)
    return out

v6 = names(os.path.join(D, "rootfs-v6.tar"))
v7 = names(os.path.join(D, "rootfs-v7.tar"))
gone = sorted(n for n in v6 - v7)
print("in v6 but not v7:", len(gone))
for n in gone:
    print("  ", n)
