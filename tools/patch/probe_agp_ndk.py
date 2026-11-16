import zipfile, re, sys
jar = r'Linux-小小容器\04-下载缓存-可删除\agp-9.2.1.jar'
z = zipfile.ZipFile(jar)
names = [n for n in z.namelist() if n.endswith('.properties') or 'Ndk' in n or 'ndk' in n.lower()]
for n in names[:60]:
    print(n)
print('---- classes with NDK version constants ----')
pat = re.compile(rb'2[7-9]\.\d+\.\d{8}')
hits = {}
for n in z.namelist():
    if not n.endswith('.class'):
        continue
    if 'Ndk' not in n and 'ndk' not in n:
        continue
    data = z.read(n)
    for m in pat.findall(data):
        hits.setdefault(m.decode(), []).append(n)
for k, v in sorted(hits.items()):
    print(k, len(v), v[:3])
