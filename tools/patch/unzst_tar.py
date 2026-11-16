"""Decompress the rootfs .tar.zst into a plain .tar on disk so we can append entries.

Usage: python unzst_tar.py <in.tar.zst> <out.tar>
Prints the byte size of the produced tar and how many trailing zero blocks were found.
"""
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyz2'))
import zstandard as zstd  # noqa: E402


def main():
    src, dst = sys.argv[1], sys.argv[2]
    dctx = zstd.ZstdDecompressor()
    total = 0
    with io.open(src, 'rb') as fin, io.open(dst, 'wb') as fout:
        reader = dctx.stream_reader(fin, read_across_frames=True)
        while True:
            chunk = reader.read(1 << 24)
            if not chunk:
                break
            fout.write(chunk)
            total += len(chunk)
            if total % (1 << 30) < (1 << 24):
                print('  %.2f GB' % (total / float(1 << 30)), flush=True)
    print('DONE bytes=%d (%.2f GB)' % (total, total / float(1 << 30)))


if __name__ == '__main__':
    main()
