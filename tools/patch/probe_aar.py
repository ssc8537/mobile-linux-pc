import os, urllib.request
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")

urls = [
    "https://jitpack.io/com/github/tiny-computer/avnc/030e6c032e/avnc-030e6c032e.aar",
    "https://jitpack.io/com/github/tiny-computer/termux-x11/21159a1405/termux-x11-21159a1405.aar",
    "https://jitpack.io/com/github/tiny-computer/terminal-lib/e7a15b7877/terminal-lib-e7a15b7877.aar",
    "https://jitpack.io/com/github/zhpanvip/viewpagerindicator/1.2.3/viewpagerindicator-1.2.3.aar",
    "https://jitpack.io/com/github/Dimezis/BlurView/version-3.2.0/BlurView-version-3.2.0.aar",
    "https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/9.2.1/gradle-9.2.1.jar",
]
for u in urls:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}), timeout=60)
        n = r.headers.get("Content-Length")
        print(r.status, round(int(n)/1e6, 2) if n else "?", u)
    except Exception as e:
        print("ERR", repr(e)[:140], u)
