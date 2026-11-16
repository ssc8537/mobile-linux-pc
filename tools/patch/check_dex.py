import sys, zipfile, re

apk = sys.argv[1]
z = zipfile.ZipFile(apk)
names = [n for n in z.namelist() if re.match(r'classes\d*\.dex$', n)]
print("dex files:", names)
needles = [b'setFZoomLocked', b'getFZoomLocked', b'FLAG_ZOOM_LOCKED']
for n in names:
    data = z.read(n)
    hits = [nd.decode() for nd in needles if nd in data]
    if hits:
        print(n, "->", hits)
# also check assets presence
for info in z.infolist():
    if info.filename.startswith('assets/') and info.file_size > 1000000:
        print("ASSET", info.filename, round(info.file_size / 1e6, 1), "MB")
