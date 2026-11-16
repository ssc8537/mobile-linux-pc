# -*- coding: utf-8 -*-
"""Byte-level version bump (BOM-safe) for the AVNC fork + host build copy."""
import re
import sys

NEW = sys.argv[1] if len(sys.argv) > 1 else "3.2.2-tc4v9"

FILES = [
    (r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable"
     r"\app\build.gradle",
     rb"version = ['\"]3\.2\.2[^'\"]*['\"]",
     "version = '%s'" % NEW),
    (r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain"
     r"\ws-gradle-build-copy-deletable\tiny_container\gradle\libs.versions.toml",
     rb"(?m)^avnc = \"3\.2\.2[^\"]*\"",
     'avnc = "%s"' % NEW),
]

for path, pattern, replacement in FILES:
    with open(path, "rb") as f:
        raw = f.read()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    body = raw[len(bom):] if bom else raw
    hits = re.findall(pattern, body)
    if not hits:
        print("MISS", path)
        continue
    body = re.sub(pattern, replacement.encode(), body)
    with open(path, "wb") as f:
        f.write(bom + body)
    print("OK", path.split("\\")[-1], "old=", hits[0].decode(), "->", NEW,
          "bom=", bool(bom))
