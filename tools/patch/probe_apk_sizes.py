import os, urllib.request
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
base = "https://github.com/Cateners/tiny_container/releases/download/v4.2.2/"
for n in ["tiny-container.apk", "tiny-container-xfce-zh.apk", "tiny-container-xfce-en.apk",
          "tiny-container-gxde-zh.apk", "tiny-container-gxde-en.apk", "jniLibs.zip"]:
    u = base + n
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}), timeout=60)
        print(round(int(r.headers.get("Content-Length", 0))/1e6, 1), "MB", n)
    except Exception as e:
        print("ERR", repr(e)[:100], n)
