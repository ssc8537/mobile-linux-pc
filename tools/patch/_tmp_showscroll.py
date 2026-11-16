import io, re
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
for f in (r"avnc-upstream-fork-deletable\app\src\main\res\values-zh-rCN\strings.xml",
          r"avnc-upstream-fork-deletable\app\src\main\res\values\strings.xml"):
    s = io.open(R + "\\" + f, encoding="utf-8").read()
    for k in ("pref_scroll_speed", "msg_scroll_speed_help"):
        m = re.search(r'<string name="%s"[^>]*>(.*?)</string>' % k, s, re.S)
        print(f.split("\\")[-2], k, "=>", m.group(1) if m else "MISSING")
