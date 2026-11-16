import zipfile, sys, os
src, dst = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
z.extractall(dst)
print("extract ok ->", dst)
for root, dirs, files in os.walk(dst):
    for f in files[:3]:
        pass
print("file count:", sum(len(f) for _, _, f in os.walk(dst)))
