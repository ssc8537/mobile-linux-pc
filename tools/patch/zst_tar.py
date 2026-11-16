"""Compress a plain tar into .tar.zst with multithreaded zstd.

Usage: python zst_tar.py <in.tar> <out.tar.zst> [level] [threads]
"""
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyz2'))
import zstandard as zstd  # noqa: E402


def main():
    src, dst = sys.argv[1], sys.argv[2]
    level = int(sys.argv[3]) if len(sys.argv) > 3 else 19
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    total_in = 0
    cctx = zstd.ZstdCompressor(level=level, threads=threads, write_checksum=True)
    with io.open(src, 'rb') as fin, io.open(dst, 'wb') as fout:
        # stream via compressobj equivalent: use a writer that copies the frame
        writer = cctx.stream_writer(fout, closefd=False)
        while True:
            chunk = fin.read(1 << 24)
            if not chunk:
                break
            writer.write(chunk)
            total_in += len(chunk)
            if total_in % (1 << 30) < (1 << 24):
                print('  fed %.2f GB' % (total_in / float(1 << 30)), flush=True)
        writer.flush()
        writer.close()
    print('DONE in=%d out=%d ratio=%.3f' % (total_in, os.path.getsize(dst),
                                            os.path.getsize(dst) / float(total_in)))


if __name__ == '__main__':
    main()
