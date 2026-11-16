import io, os, hashlib
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
D = os.path.join(R, "build-env-toolchain", "cache-downloads-deletable")
for name in ("rootfs-v7.tar.zst", "rootfs-patch-v7.tar.zst"):
    p = os.path.join(D, name)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(name, os.path.getsize(p), h)
