import urllib.request, ssl, os, sys

os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")

urls = [
    "https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/9.2.1/gradle-9.2.1.pom",
    "https://jitpack.io/com/github/tiny-computer/avnc/030e6c032e/avnc-030e6c032e.pom",
    "https://jitpack.io/com/github/tiny-computer/termux-x11/21159a1405/termux-x11-21159a1405.pom",
    "https://jitpack.io/com/github/tiny-computer/terminal-lib/e7a15b7877/terminal-lib-e7a15b7877.pom",
    "https://services.gradle.org/distributions/gradle-9.4.1-bin.zip",
    "https://dl.google.com/android/repository/repository2-3.xml",
    "https://api.adoptium.net/v3/info/available_releases",
    "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip",
]

for u in urls:
    try:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=40)
        print(r.status, r.headers.get("Content-Length"), u)
    except Exception as e:
        print("ERR", repr(e)[:120], u)
