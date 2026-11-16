import os, json, urllib.request
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")

url = ("https://api.adoptium.net/v3/assets/latest/21/hotspot"
       "?architecture=x64&image_type=jdk&os=windows&vendor=eclipse")
d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
for a in d:
    pk = a["binary"]["package"]
    print(pk["link"])
    print(pk["checksum"], pk["size"])
    print(a["version"]["semver"])
