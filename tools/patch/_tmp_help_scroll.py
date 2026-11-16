import io, re
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
ZH = ("档位 1 = 手指滑一下滚得最多（最快）；档位 9 = 滚得最少（最慢）。"
      "档位 3 是官方原值。想要一屏只滚一点点，就把档位调大。")
EN = ("Step 1 scrolls the most lines per swipe (fastest); step 9 scrolls the fewest (slowest). "
      "Step 3 is the upstream default. Use a higher step to scroll in small increments.")
for f, txt in ((r"avnc-upstream-fork-deletable\app\src\main\res\values-zh-rCN\strings.xml", ZH),
               (r"avnc-upstream-fork-deletable\app\src\main\res\values\strings.xml", EN)):
    p = R + "\\" + f
    s = io.open(p, encoding="utf-8", newline="").read()
    new, n = re.subn(r'(<string name="msg_scroll_speed_help"[^>]*>)(.*?)(</string>)',
                     lambda m: m.group(1) + txt + m.group(3), s, count=1, flags=re.S)
    assert n == 1, (f, n)
    io.open(p, "w", encoding="utf-8", newline="").write(new)
    print("patched", f.split("\\")[-2], "len", len(new))
