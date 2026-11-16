import os, sys, time, json, urllib.request, threading, hashlib

PROXY = "http://127.0.0.1:7897"


def opener(use_proxy):
    if use_proxy:
        h = [urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})]
    else:
        h = [urllib.request.ProxyHandler({})]
    return urllib.request.build_opener(*h)


def head(url, use_proxy):
    op = opener(use_proxy)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    r = op.open(req, timeout=60)
    return r.headers


def download(url, out, use_proxy=False, workers=8):
    h = head(url, use_proxy)
    size = int(h.get("Content-Length") or 0)
    ranges = (h.get("Accept-Ranges") or "").lower() == "bytes"
    print(f"size={size/1e6:.1f}MB ranges={ranges} proxy={use_proxy}", flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    tmp = out + ".part"

    if not ranges or size < 8 << 20 or workers <= 1:
        op = opener(use_proxy)
        r = op.open(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120)
        got = 0
        t0 = time.time()
        last = 0.0
        with open(tmp, "wb") as f:
            while True:
                c = r.read(1 << 20)
                if not c:
                    break
                f.write(c)
                got += len(c)
                if time.time() - last > 10:
                    last = time.time()
                    print(f"  {got/1e6:7.1f}/{size/1e6:7.1f} MB {100*got/max(size,1):5.1f}% {got/1e6/(time.time()-t0):5.2f} MB/s", flush=True)
    else:
        chunk = (size + workers - 1) // workers
        parts = []
        for i in range(workers):
            a = i * chunk
            b = min(size, (i + 1) * chunk) - 1
            if a > b:
                break
            parts.append((i, a, b))
        done = [0] * len(parts)
        errs = []

        def work(idx, a, b):
            p = f"{tmp}.{idx}"
            for attempt in range(4):
                try:
                    have = os.path.getsize(p) if os.path.exists(p) else 0
                    start = a + have
                    if start > b:
                        done[idx] = b - a + 1
                        return
                    op = opener(use_proxy)
                    req = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0", "Range": f"bytes={start}-{b}"})
                    r = op.open(req, timeout=120)
                    with open(p, "ab") as f:
                        while True:
                            c = r.read(1 << 20)
                            if not c:
                                break
                            f.write(c)
                            done[idx] += len(c)
                    if os.path.getsize(p) >= b - a + 1:
                        return
                except Exception as e:
                    errs.append(repr(e)[:100])
                    time.sleep(2)
            raise RuntimeError(f"chunk {idx} failed")

        ths = [threading.Thread(target=work, args=(i, a, b), daemon=True) for (i, a, b) in parts]
        t0 = time.time()
        for t in ths:
            t.start()
        last = 0.0
        while any(t.is_alive() for t in ths):
            time.sleep(1)
            if time.time() - last > 10:
                last = time.time()
                g = sum(done)
                print(f"  {g/1e6:7.1f}/{size/1e6:7.1f} MB {100*g/max(size,1):5.1f}% {g/1e6/(time.time()-t0):5.2f} MB/s", flush=True)
        for t in ths:
            t.join()
        if sum(done) != size:
            print("CHUNK SUM MISMATCH", sum(done), size, errs[:3], file=sys.stderr)
            sys.exit(3)
        with open(tmp, "wb") as f:
            for idx, a, b in parts:
                p = f"{tmp}.{idx}"
                with open(p, "rb") as pf:
                    f.write(pf.read())
                os.remove(p)

    got = os.path.getsize(tmp)
    if size and got != size:
        print("INCOMPLETE", got, size, file=sys.stderr)
        sys.exit(2)
    os.replace(tmp, out)
    print("DONE", out, round(got / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    url, out = sys.argv[1], sys.argv[2]
    use_proxy = len(sys.argv) > 3 and sys.argv[3] == "proxy"
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    download(url, out, use_proxy, workers)
