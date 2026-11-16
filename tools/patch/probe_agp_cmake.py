import zipfile, re
jar = r'Linux-小小容器\04-下载缓存-可删除\agp-9.2.1.jar'
z = zipfile.ZipFile(jar)
pat = re.compile(rb'3\.(?:1[0-9]|2[0-9]|3[0-9])\.\d{1,2}(?:\.\d{4,8})?')
hits = {}
for n in z.namelist():
    if not n.endswith('.class'):
        continue
    ln = n.lower()
    if 'cmake' not in ln:
        continue
    for m in pat.findall(z.read(n)):
        hits.setdefault(m.decode(), set()).add(n)
for k in sorted(hits):
    print(k, len(hits[k]))
