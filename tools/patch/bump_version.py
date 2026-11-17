# -*- coding: utf-8 -*-
"""Byte-level version bump (BOM-safe) for the AVNC fork + its consumer.

The AVNC fork's version has to be bumped in BOTH places before a rebuild,
otherwise Gradle silently serves the cached old AAR and your edits never
reach the APK. This script does both at once.

Usage (from the repository root, or anywhere with --root):
    python tools/patch/bump_version.py 3.2.2-tc4v11
    python tools/patch/bump_version.py 3.2.2-tc4v11 --root "D:\\some\\workspace"

Root discovery order when --root is not given:
    1. $TC_ROOT
    2. walk up from this file until a dir contains `source/avnc` or
       `avnc-upstream-fork-deletable`
"""
import argparse
import os
import re
import sys


def find_root(explicit):
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get("TC_ROOT")
    if env:
        return os.path.abspath(env)
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        for rel in ("source/avnc", "avnc-upstream-fork-deletable"):
            if os.path.isdir(os.path.join(d, rel)):
                return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.getcwd()


def locate(root, *candidates):
    """Return the first existing path among candidates (relative to root)."""
    for rel in candidates:
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            return p
    return None


def bump(path, pattern, replacement):
    with open(path, "rb") as f:
        raw = f.read()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    body = raw[len(bom):] if bom else raw
    hits = re.findall(pattern, body)
    if not hits:
        print("MISS", path)
        return False
    body = re.sub(pattern, replacement.encode(), body)
    with open(path, "wb") as f:
        f.write(bom + body)
    print("OK", os.path.basename(path), "old=", hits[0].decode(), "->", replacement,
          "bom=", bool(bom))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", nargs="?", default="3.2.2-tc4v11")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    new = args.version
    root = find_root(args.root)
    print("ROOT=" + root)

    targets = [
        (
            locate(root, "source/avnc/app/build.gradle",
                   "avnc-upstream-fork-deletable/app/build.gradle"),
            rb"version = ['\"]3\.2\.2[^'\"]*['\"]",
            "version = '%s'" % new,
        ),
        (
            locate(root, "source/app/gradle/libs.versions.toml",
                   "build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container"
                   "/gradle/libs.versions.toml"),
            rb"(?m)^avnc = \"3\.2\.2[^\"]*\"",
            'avnc = "%s"' % new,
        ),
    ]

    ok = 0
    for path, pattern, replacement in targets:
        if not path:
            print("NOT-FOUND (skipped)")
            continue
        if bump(path, pattern, replacement):
            ok += 1

    print("BUMPED=%d/2" % ok)
    return 0 if ok == 2 else 1


if __name__ == "__main__":
    sys.exit(main())
