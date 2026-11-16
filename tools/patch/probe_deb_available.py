import sys, re, urllib.request

BASE = 'http://ftp.cn.debian.org/debian/pool/main/'
PKGS = [
    ('o', 'onboard'),
    ('x', 'xvkbd'),
    ('x', 'xfce4-taskmanager'),
    ('x', 'xfce4-clipman-plugin'),
    ('x', 'xfce4-screenshooter'),
    ('p', 'picom'),
    ('x', 'xdotool'),
    ('w', 'wmctrl'),
]
for letter, name in PKGS:
    url = '%s%s/%s/' % (BASE, letter, name)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'probe/1.0'})
        html = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    except Exception as e:
        print('##', name, 'ERR', e)
        continue
    names = sorted(set(re.findall(r'href="([^"]+_arm64\.deb)"', html)))
    print('##', name, '->', len(names), 'arm64 debs')
    for n in names[-6:]:
        print('   ', n)
