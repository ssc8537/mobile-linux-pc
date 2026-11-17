import urllib.request, time, os, sys

url = sys.argv[1]
use_proxy = len(sys.argv) > 2 and sys.argv[2] == "proxy"
handlers = []
if use_proxy:
    handlers.append(urllib.request.ProxyHandler({"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
else:
    handlers.append(urllib.request.ProxyHandler({}))
op = urllib.request.build_opener(*handlers)
try:
    r = op.open(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60)
    t0 = time.time()
    got = 0
    while time.time() - t0 < 6:
        b = r.read(1 << 16)
        if not b:
            break
        got += len(b)
    print(f"{'proxy' if use_proxy else 'direct'} {got/1e6/ (time.time()-t0):.2f} MB/s  {url[:70]}")
except Exception as e:
    print("ERR", repr(e)[:110])
