import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
subs = [("761,866,427", "761,866,599"),
        ("7E86BB0BEAB5A3345035AE19DE1CD1BB0DF227BEDD23DC7EA344275A9C6DA184",
         "B1C57CCCB6A35C932E9C1C4F1323F269C81EB2BF7C2F0F4970A72781191D8CFD")]
for f in (r"build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md",
          r"build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md"):
    p = R + "\\" + f
    s = io.open(p, encoding="utf-8", newline="").read()
    for a, b in subs:
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("updated", f.split("\\")[-1], len(s))
