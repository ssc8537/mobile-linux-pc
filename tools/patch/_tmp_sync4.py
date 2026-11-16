import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
subs = [("761,866,599", "761,866,675"),
        ("B1C57CCCB6A35C932E9C1C4F1323F269C81EB2BF7C2F0F4970A72781191D8CFD",
         "4D3395C4EABC545657F6F0CC58303AD50A7F4D0A7A3E8AFEC40798AC7224A161"),
        ("`deltaPerScroll = 8 + (档位-1)*6`", "`deltaPerScroll` 档位 3=20px 保持不变、9=74px"),
        ("`deltaPerScroll = 8 + (档位-1)*6`（档位 3 = 20 = 上游，档位 1 = 8）",
         "`deltaPerScroll`（档位 3 = 20px = 上游；档位 9 = 74px，比上游慢 3.7 倍）")]
for f in (r"build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md",
          r"build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md",
          r"docs-project-notes-keep-forever\log-version-history.md"):
    p = R + "\\" + f
    s = io.open(p, encoding="utf-8", newline="").read()
    for a, b in subs:
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("synced", f.split("\\")[-1], len(s))
