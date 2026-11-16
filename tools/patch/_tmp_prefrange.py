import io, re
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml"
s = io.open(p, encoding="utf-8").read()
for key in ("mouse_acceleration_strength", "slow_pointer_speed", "scroll_speed", "cursor_size"):
    i = s.index('app:key="%s"' % key)
    a = s.rindex("<", 0, i)
    b = s.index("/>", i) + 2
    blk = re.sub(r"\s+", " ", s[a:b])
    print(key, "::", blk)
