import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md'
s = io.open(p, encoding='utf-8', newline='').read()
old = "  - \"三指轻点\"开关现在真正生效：关掉后三指轻点不再请求键盘\n    （AVNC fork 版本号 `3.2.2-tc4v2` → `3.2.2-tc4v3`）。"
new = ("  - \"三指轻点\"开关现在真正生效：关掉后三指轻点不再请求键盘\n"
       "    （AVNC fork 版本号 `3.2.2-tc4v2` → `3.2.2-tc4v3`）。\n"
       "  - 剪贴板历史对齐 Windows：`Super+V` → `xfce4-popup-clipman`，\n"
       "    `Super+Shift+V` → `xfce4-clipman-history`；并新增用户级自启动\n"
       "    `~/.config/autostart/tiny-clipman.desktop`（deb 自带的那条是 `Hidden=true`，\n"
       "    不会自动跑，所以必须自己加一条）。")
assert old in s, 'anchor missing'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
