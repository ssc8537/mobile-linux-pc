import sys, zipfile, os

aar = sys.argv[1]
out = sys.argv[2]
with zipfile.ZipFile(aar) as z:
    names = [n for n in z.namelist() if n.startswith('jni/')]
    for n in names:
        print(n, z.getinfo(n).file_size)
    # extract each ABI's libnative-vnc.so into out/<abi>/libnative-vnc.so
    for n in names:
        if not n.endswith('.so'):
            continue
        abi = n.split('/')[1]
        d = os.path.join(out, abi)
        os.makedirs(d, exist_ok=True)
        with z.open(n) as src, open(os.path.join(d, os.path.basename(n)), 'wb') as dst:
            dst.write(src.read())
        print("extracted", n)
