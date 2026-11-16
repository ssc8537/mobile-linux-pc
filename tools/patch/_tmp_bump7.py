R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
for f in (r"avnc-upstream-fork-deletable\app\build.gradle",
          r"build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\gradle\libs.versions.toml"):
    p = R + "\\" + f
    b = open(p, "rb").read()
    s = b.decode("utf-8-sig")
    n = s.count("3.2.2-tc4v6")
    assert n == 1, (f, n)
    s = s.replace("3.2.2-tc4v6", "3.2.2-tc4v7")
    out = s.encode("utf-8")
    if b.startswith(b"\xef\xbb\xbf"):
        out = b"\xef\xbb\xbf" + out
    open(p, "wb").write(out)
    print("bumped", f.split("\\")[-1])
