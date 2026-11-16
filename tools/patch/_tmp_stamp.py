import hashlib, os
C = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\cache-downloads-deletable"
A = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\assets"
p = os.path.join(C, "rootfs-v5.tar.zst")
h = hashlib.sha256()
with open(p, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h.update(chunk)
digest = h.hexdigest()
stamp = "v4-" + digest[:16]
with open(os.path.join(A, "rootfs.stamp"), "w", encoding="utf-8", newline="\n") as f:
    f.write(stamp + "\n")
print("rootfs size", os.path.getsize(p))
print("sha256", digest.upper())
print("stamp", stamp)
print("patch size", os.path.getsize(os.path.join(A, "rootfs.patch.tar.zst")))
