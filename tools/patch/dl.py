import os, sys, urllib.request, time, hashlib

os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")

url = sys.argv[1]
out = sys.argv[2]
os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
r = urllib.request.urlopen(req, timeout=120)
total = int(r.headers.get("Content-Length") or 0)
have = 0
t0 = time.time()
last = 0
with open(out + ".part", "wb") as f:
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        f.write(chunk)
        have += len(chunk)
        if time.time() - last > 5:
            last = time.time()
            pct = (100.0 * have / total) if total else 0
            print(f"{have/1e6:8.1f} MB / {total/1e6:8.1f} MB  {pct:5.1f}%  {have/1e6/max(time.time()-t0,0.001):6.2f} MB/s", flush=True)
if total and have != total:
    print("INCOMPLETE", have, total)
    sys.exit(2)
os.replace(out + ".part", out)
print("DONE", out, round(os.path.getsize(out)/1e6, 1), "MB", flush=True)
