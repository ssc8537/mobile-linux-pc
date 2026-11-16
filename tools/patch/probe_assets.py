import os, re, urllib.request
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")

for tag in ["v4.2.3-alpha1", "v4.2.2"]:
    u = f"https://github.com/Cateners/tiny_container/releases/expanded_assets/{tag}"
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "ignore")
        print("==", tag, len(d))
        for m in re.finditer(r'href="(/Cateners/tiny_container/releases/download/[^"]+)"', d):
            print("  ", m.group(1))
    except Exception as e:
        print("ERR", tag, repr(e)[:100])
