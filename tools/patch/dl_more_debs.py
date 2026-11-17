import io, os, re, urllib.request, urllib.parse


def _find_ws():
    env = os.environ.get('TC_ROOT')
    if env:
        return env
    _d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(_d, 'build-env-toolchain')) or os.path.isdir(
            os.path.join(_d, 'source', 'app')
        ):
            return _d
        _p = os.path.dirname(_d)
        if _p == _d:
            return os.path.dirname(os.path.abspath(__file__))
        _d = _p


WS = _find_ws()
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT = WS
PROXY = 'http://127.0.0.1:7897'
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}))

DEBDIR = ROOT + r'\build-env-toolchain\cache-downloads-deletable\debs'
BASE = 'http://ftp.cn.debian.org/debian/pool/main/'

WANT = [
    ('x/xfce4-clipman-plugin', 'xfce4-clipman'),
    ('x/xfce4-clipman-plugin', 'xfce4-clipman-plugin'),
    ('q/qrencode', 'libqrencode4'),
]


def listdir(pkgpath):
    url = BASE + pkgpath + '/'
    req = urllib.request.Request(url, headers={'User-Agent': 'probe'})
    try:
        html = opener.open(req, timeout=40).read().decode('utf-8', 'replace')
    except Exception as e:
        print('ERR', url, e)
        return []
    return re.findall(r'href="([^"]+?arm64\.deb)"', html)


def pick(names, pkg):
    """Newest version, tie-break by plain (no +b) name."""
    cands = [n for n in names if n.startswith(pkg + '_')]
    if not cands:
        return None
    def key(n):
        ver = n[len(pkg) + 1:].replace('%2B', '+').split('_')[0]
        return (ver, n.startswith(pkg + '_') and '+' not in n)
    cands.sort(key=key)
    return cands[-1]


for pkgpath, pkg in WANT:
    names = listdir(pkgpath)
    chosen = pick(names, pkg)
    print(pkg, '->', chosen, '| all:', len(names))
    if not chosen:
        continue
    real = chosen.replace('%2B', '+').replace('%3a', ':')
    dst = os.path.join(DEBDIR, real)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print('   have', real, os.path.getsize(dst))
        continue
    url = BASE + pkgpath + '/' + chosen
    req = urllib.request.Request(url, headers={'User-Agent': 'probe'})
    data = opener.open(req, timeout=120).read()
    io.open(dst, 'wb').write(data)
    print('   got', real, len(data))
