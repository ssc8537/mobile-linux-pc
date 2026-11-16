"""Inspect the raw tar header magic + long-name mechanism of the original image."""
import io
import sys

path = sys.argv[1]
f = io.open(path, 'rb')
seen = []
pos = 0
blocks = 0
magics = {}
while blocks < 4000:
    f.seek(pos)
    hdr = f.read(512)
    if len(hdr) < 512 or hdr == b'\0' * 512:
        break
    name = hdr[0:100].split(b'\0')[0].decode('utf-8', 'replace')
    magic = hdr[257:265]
    size_field = hdr[124:136].split(b'\0')[0].strip()
    try:
        size = int(size_field, 8) if size_field else 0
    except ValueError:
        size = 0
    magics[magic] = magics.get(magic, 0) + 1
    if blocks < 12 or name.startswith('././@') or name.startswith('PaxHeaders'):
        seen.append('blk=%d name=%r magic=%r size=%d' % (blocks, name, magic, size))
    pos += 512 + ((size + 511) // 512) * 512
    blocks += 1
print('\n'.join(seen))
print('magic histogram: %r' % ({k.decode('latin-1'): v for k, v in magics.items()},))
print('blocks scanned: %d' % blocks)
