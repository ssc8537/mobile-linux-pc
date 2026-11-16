import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
for p, old, new in [
    (R + r"\avnc-upstream-fork-deletable\app\build.gradle", "version = '3.2.2-tc4v4'", "version = '3.2.2-tc4v5'"),
    (R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\gradle\libs.versions.toml", 'avnc = "3.2.2-tc4v4"', 'avnc = "3.2.2-tc4v5"'),
]:
    b = open(p, "rb").read()
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    s = b.decode("utf-8")
    assert old in s, (p, old)
    s = s.replace(old, new, 1)
    open(p, "wb").write(s.encode("utf-8"))
    print("bumped", p.split("\\")[-1], "->", new)
