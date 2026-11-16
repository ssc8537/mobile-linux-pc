import io, os, sys
sys.path.insert(0, r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\pyz2')
import zstandard, tarfile

IMG = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\cache-downloads-deletable\xfce-zh-20260808-160507.tar.zst'
n = 0
with io.open(IMG, 'rb') as f:
    dr = zstandard.ZstdDecompressor()
    with dr.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for ti in tf:
            print(repr(ti.name), ti.type, ti.uid, ti.gid, ti.uname, ti.gname, oct(ti.mode), ti.size)
            n += 1
            if n >= 25:
                break
