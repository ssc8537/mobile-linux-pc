import hashlib, io, os
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
C = os.path.join(R, "build-env-toolchain", "cache-downloads-deletable")
p = os.path.join(C, "rootfs-v5.tar.zst")
h = hashlib.sha256()
with open(p, "rb") as f:
    for chunk in iter(lambda: f.read(4 << 20), b""):
        h.update(chunk)
print("size", os.path.getsize(p))
print("sha256", h.hexdigest().upper())
