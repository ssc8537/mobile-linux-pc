import json, urllib.request, sys, os

proxy = os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:7897"


def get(url, use_proxy=True):
    op = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy}) if use_proxy
        else urllib.request.ProxyHandler({})
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return op.open(req, timeout=60)


for use_proxy in (False, True):
    for url in [
        "https://github.com/tiny-computer/images/releases",
        "https://api.github.com/repos/tiny-computer/images/releases",
    ]:
        try:
            r = get(url, use_proxy)
            data = r.read()
            print("OK", use_proxy, url, len(data))
            if "api.github" in url:
                j = json.loads(data)
                for rel in j[:4]:
                    print(" tag", rel["tag_name"])
                    for a in rel["assets"]:
                        print("   ", a["name"], round(a["size"] / 1e6, 1), "MB")
            else:
                import re
                names = set(re.findall(r'/releases/download/[^"\']+', data.decode("utf-8", "ignore")))
                for n in sorted(names)[:40]:
                    print("  asset-link", n)
            break
        except Exception as e:
            print("FAIL", use_proxy, url, e)
