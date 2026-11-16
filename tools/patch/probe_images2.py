import re, sys, urllib.request, os

proxy = os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:7897"
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return op.open(req, timeout=90).read().decode("utf-8", "ignore")


html = fetch("https://github.com/tiny-computer/images/releases")
# capture tag names and asset names
tags = re.findall(r'/tiny-computer/images/releases/tag/([^"\'?&<]+)', html)
print("TAGS:", sorted(set(tags)))

assets = re.findall(r'/tiny-computer/images/releases/download/([^"\'?&<]+)', html)
print("ASSETS:")
for a in sorted(set(assets)):
    print("  ", a)

# expand assets per tag in source order, keeping line structure
lines = html.split("\n")
cur = None
for ln in lines:
    m = re.search(r'/releases/tag/([^"\'?&<]+)', ln)
    if m:
        cur = m.group(1)
    m2 = re.search(r'/releases/download/([^"\'?&<]+)', ln)
    if m2 and cur:
        print("MAP", cur, "->", m2.group(1))
