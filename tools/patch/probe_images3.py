import re, sys, urllib.request, os

proxy = os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:7897"
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return op.open(req, timeout=90).read().decode("utf-8", "ignore")


for tag in ["260808", "260627"]:
    url = f"https://github.com/tiny-computer/images/releases/expanded_assets/{tag}"
    try:
        html = fetch(url)
    except Exception as e:
        print("FAIL", tag, e)
        continue
    print("=== tag", tag, "len", len(html))
    # asset names appear as /download/<tag>/<file>
    names = re.findall(r'/images/releases/download/[^"\']+', html)
    for n in dict.fromkeys(names):
        print("   ", n)
    sizes = re.findall(r'([\d.]+)\s*(MB|GB|KB)', html)
    print("   sizes:", sizes[:40])
