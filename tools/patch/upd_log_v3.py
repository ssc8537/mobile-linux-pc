import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\log-version-history.md'
s = io.open(p, encoding='utf-8', newline='').read()
old = "  2. `Dispatcher.doOpenRemoteOsk()` 增加 `if (!viewModel.pref.input.oskThreeFingerTap) return`，\n     让「三指轻点」开关真正生效。AVNC 分支版本号 `3.2.2-tc4v2` → `3.2.2-tc4v3`。"
new = ("  2. `Dispatcher.doOpenRemoteOsk()` 增加 `if (!viewModel.pref.input.oskThreeFingerTap) return`，\n"
       "     让「三指轻点」开关真正生效。AVNC 分支版本号 `3.2.2-tc4v2` → `3.2.2-tc4v3`。\n"
       "  3. 镜像里补了剪贴板历史的 Windows 化：`Super+V` → `xfce4-popup-clipman`、\n"
       "     `Super+Shift+V` → `xfce4-clipman-history`，并新增\n"
       "     `home/tiny/.config/autostart/tiny-clipman.desktop`（deb 自带的 autostart 是\n"
       "     `Hidden=true`，不会自动启动，必须自己补一条）。")
assert old in s, 'anchor missing'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
