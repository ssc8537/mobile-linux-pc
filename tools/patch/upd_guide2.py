import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md'
s = io.open(p, encoding='utf-8', newline='').read()
old = '  - 触发方式三种：指针旁九宫格中间按钮、三指轻点、按 F9'
assert old in s, 'anchor missing'
new = '\n'.join([
 old,
 '  - **键盘自带设置**（本版新增）：顶部工具栏点「设置」，弹出「悬浮键盘设置」对话框，',
 '    可改默认布局（全键盘 / 精简键盘）、默认位置（悬浮 / 停靠）、按键高度（32~64 px）、',
 '    不透明度（60~100%）。保存后写入 `~/.config/tiny-osk.conf`，下次开机沿用。',
])
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
