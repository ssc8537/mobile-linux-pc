import urllib.request, os, re

os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")

u = "https://dl.google.com/android/repository/repository2-3.xml"
d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "ignore")

paths = re.findall(r'<remotePackage path="([^"]+)"', d)
for p in paths:
    if re.search(r"platforms;android-3[5-9]|build-tools;3[5-9]|ndk;2[7-9]|ndk;3[0-9]|cmake;3\.|platform-tools$|cmdline-tools", p):
        print(p)
print("---- total packages:", len(paths))
