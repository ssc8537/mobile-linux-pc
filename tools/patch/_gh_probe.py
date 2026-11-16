import json, os, ssl, time, urllib.request, urllib.error, subprocess

PROXY = "http://127.0.0.1:7897"
proc = subprocess.run(["git", "credential", "fill"], input=b"protocol=https\nhost=github.com\n\n",
                      capture_output=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
tok = user = None
for line in proc.stdout.decode().splitlines():
    if line.startswith("password="): tok = line[9:]
    if line.startswith("username="): user = line[10:]
print("user:", user, "toklen:", len(tok or ""), "prefix:", (tok or "")[:4])
open(r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\_tok.txt", "w").write(tok or "")

def req(method, path, body=None, tries=6):
    url = "https://api.github.com" + path
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": "token " + tok, "Accept": "application/vnd.github+json",
                "User-Agent": "dsh-agent", "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28"})
            with urllib.request.urlopen(r, timeout=90) as resp:
                raw = resp.read().decode()
                return resp.status, (json.loads(raw) if raw.strip() else {}), dict(resp.headers)
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            return e.code, {"error": raw[:400]}, dict(e.headers)
        except Exception as e:
            last = e
            time.sleep(2 + i)
    return -1, {"error": repr(last)}, {}

st, me, hdrs = req("GET", "/user")
print("GET /user ->", st, me.get("login") if st == 200 else me)
print("scopes:", hdrs.get("x-oauth-scopes"))
st, repo, _ = req("GET", "/repos/ssc8537/mobile-linux-pc")
if st == 200:
    print("repo:", repo["full_name"], "private=", repo["private"], "default=", repo["default_branch"],
          "size_kb=", repo["size"], "perms=", repo.get("permissions"))
else:
    print("repo err:", st, repo)
st, br, _ = req("GET", "/repos/ssc8537/mobile-linux-pc/branches")
print("branches:", st, [b["name"] for b in br] if isinstance(br, list) else br)
st, rl, _ = req("GET", "/repos/ssc8537/mobile-linux-pc/releases")
print("releases:", st, [(x["tag_name"], [a["name"] for a in x["assets"]]) for x in rl] if isinstance(rl, list) else rl)
