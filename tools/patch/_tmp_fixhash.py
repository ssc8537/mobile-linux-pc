import io, os
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
OLD_SIZE, OLD_SHA = "761,866,675", "4D3395C4EABC545657F6F0CC58303AD50A7F4D0A7A3E8AFEC40798AC7224A161"
NEW_SIZE, NEW_SHA = "761,867,363", "95DDD15EB9F6709EC49985B7EF69B44788B1932387DCFE1078880D13960E4527"
for rel in (r"build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md",
            r"build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md",
            r"docs-project-notes-keep-forever\log-version-history.md"):
    p = os.path.join(R, rel)
    s = io.open(p, encoding="utf-8", newline="").read()
    n = s.count(OLD_SHA) + s.count(OLD_SIZE)
    s = s.replace(OLD_SHA, NEW_SHA).replace(OLD_SIZE, NEW_SIZE)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("%-45s replaced=%d" % (rel.split("\\")[-1], n))
