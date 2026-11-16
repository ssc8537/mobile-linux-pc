import io, os, sys, tarfile
import zstandard as zstd

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
IMG = ROOT + r'\build-env-toolchain\cache-downloads-deletable\xfce-zh-20260808-160507.tar.zst'

f = io.open(IMG, 'rb')
r = zstd.ZstdDecompressor().stream_reader(f, read_across_frames=True)
tf = tarfile.open(fileobj=r, mode='r|')
out = []
count = 0
types = {}
for ti in tf:
    count += 1
    types[ti.type] = types.get(ti.type, 0) + 1
    if count <= 6:
        out.append('name=%r type=%r size=%d mode=%o uid=%d gid=%d uname=%r gname=%r fmt=%s link=%r'
                   % (ti.name, ti.type, ti.size, ti.mode, ti.uid, ti.gid,
                      ti.uname, ti.gname, 'GNU' if ti.pax_headers is None else ti.pax_headers, ti.linkname))
    if count >= 3000:
        break
out.append('total members scanned: %d' % count)
out.append('type histogram (0=reg 1=link 2=sym 5=dir): %r' % (types,))
io.open(ROOT + r'\tools-probe-scripts-deletable\tarformat.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
