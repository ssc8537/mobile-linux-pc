import io, os
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = os.path.join(R, r"build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md")
s = io.open(p, encoding="utf-8", newline="").read()
anchor = "- 上游基准：Cateners/tiny_container v4.2.3（versionCode 4，versionName 4.2.3）"
assert anchor in s
add = ("- 本版实现的功能（一句话）：**自由缩放** —— 进入 Linux 桌面时不再默认锁定缩放，\n"
       "  单指/双指缩放随时可自由使用，只有你自己点工具栏的锁形按钮才会锁定；\n"
       "  退到后台、重新进入图形界面，依旧是自由缩放。除此之外与官方 v4.2.3 完全一致。\n")
if "本版实现的功能（一句话）" not in s:
    s = s.replace(anchor, add + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("added V1 feature summary")
else:
    print("already present")
