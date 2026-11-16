import os, re, urllib.request, json
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")

u = "https://github.com/Cateners/tiny_container/releases"
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
d = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
print("page len", len(d))
# find release tags and asset names
for m in re.finditer(r'/Cateners/tiny_container/releases/(?:tag|download)/([^"\s]+)', d):
    print(m.group(0))
