import os, urllib.request, zipfile, io

os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
u = "https://jitpack.io/com/github/tiny-computer/avnc/030e6c032e/avnc-030e6c032e.aar"
d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
os.makedirs("_refs/avnc-aar", exist_ok=True)
open("_refs/avnc-aar/avnc-030e6c032e.aar", "wb").write(d)
z = zipfile.ZipFile(io.BytesIO(d))
print("aar entries:", len(z.namelist()))
print([n for n in z.namelist() if n.endswith("classes.jar")])
cj = zipfile.ZipFile(io.BytesIO(z.read("classes.jar")))
names = [n for n in cj.namelist() if "ServerProfile" in n]
print("ServerProfile classes:", names)
for n in names:
    b = cj.read(n)
    for probe in (b"fZoomLocked", b"setFZoomLocked", b"getFZoomLocked", b"FLAG_ZOOM_LOCKED"):
        print("  ", n, probe, probe in b)
