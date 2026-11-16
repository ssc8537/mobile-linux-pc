import sys, tarfile
import zstandard

path = sys.argv[1]
dctx = zstandard.ZstdDecompressor()

interesting_prefixes = (
    'home/tiny/.mozilla',
    'home/tiny/.config/mozilla',
    'usr/lib/firefox-esr',
    'usr/bin/firefox',
    'opt/tiny/export.sh',
    'home/tiny/.config/',
    'etc/machine-id',
    'var/lib/apt/lists',
    'var/cache/apt',
)
samples = {}
counts = {'firefox_dir': 0, 'mozilla_dir': 0, 'config_entries': 0}
uidgid = {}
n = 0
with open(path, 'rb') as fh:
    with dctx.stream_reader(fh) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tf:
            for m in tf:
                n += 1
                name = m.name.lstrip('./')
                if name.startswith('home/tiny/.mozilla'):
                    counts['mozilla_dir'] += 1
                if name.startswith('usr/lib/firefox-esr'):
                    counts['firefox_dir'] += 1
                if name.startswith('home/tiny/.config/'):
                    counts['config_entries'] += 1
                key = (m.uid, m.gid)
                uidgid[key] = uidgid.get(key, 0) + 1
                for p in interesting_prefixes:
                    if name == p or name.startswith(p):
                        if p not in samples:
                            samples[p] = (name, m.uid, m.gid, oct(m.mode), m.type.decode('latin1'), m.size)
                        break
print("total entries scanned:", n)
print("--- counts ---")
for k, v in counts.items():
    print(k, v)
print("--- uid/gid distribution ---")
for k, v in sorted(uidgid.items(), key=lambda x: -x[1])[:5]:
    print(k, v)
print("--- first matching entry per prefix ---")
for p, s in samples.items():
    print(p, "->", s)
