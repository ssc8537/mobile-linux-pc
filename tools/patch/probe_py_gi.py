import sys, tarfile, re
import zstandard as zstd

IMG = sys.argv[1]
targets = ("python3-gi", "python3-cairo", "python3-dbus", "gir1.2-gtk-3.0",
           "python3-gi-cairo", "libxtst6", "libxkbfile1", "libcanberra0",
           "libhunspell", "libdconf1", "dconf-cli", "gir1.2-atspi-2.0",
           "gir1.2-xkl-1.0", "python3-xlib", "python3", "libgtk-3-0")
status = None
wanted_paths = ("usr/lib/python3/dist-packages/cairo",
                "usr/lib/python3/dist-packages/dbus",
                "usr/lib/python3/dist-packages/gi",
                "usr/lib/python3/dist-packages/Xlib")
found_paths = {}

with open(IMG, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as r:
        tf = tarfile.open(fileobj=r, mode='r|')
        for m in tf:
            n = m.name
            if n.endswith("var/lib/dpkg/status"):
                status = tf.extractfile(m).read().decode('utf-8', 'replace')
            for w in wanted_paths:
                if n.rstrip('/') == w or n.startswith(w + '/'):
                    found_paths[w] = found_paths.get(w, 0) + 1

print("== dist-packages dirs ==")
for w in wanted_paths:
    print(f"  {w:50s} {found_paths.get(w, 'MISSING')}")

print("== dpkg entries ==")
if not status:
    print("  status file not found")
else:
    for block in status.split("\n\n"):
        mm = re.search(r"^Package: (.+)$", block, re.M)
        if not mm:
            continue
        pkg = mm.group(1).strip()
        if pkg in targets:
            ver = re.search(r"^Version: (.+)$", block, re.M)
            dep = re.search(r"^Depends: (.+)$", block, re.M)
            print(f"  {pkg} {ver.group(1) if ver else '?'}")
            if dep:
                print(f"      Depends: {dep.group(1)}")
    present = set()
    for block in status.split("\n\n"):
        mm = re.search(r"^Package: (.+)$", block, re.M)
        if mm:
            present.add(mm.group(1).strip())
    print("== missing targets ==")
    for t in targets:
        if t not in present:
            print(f"  MISSING {t}")
