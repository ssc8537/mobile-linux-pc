import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md'
s = io.open(p, encoding='utf-8', newline='').read()
old = '6. 设置 AVNC → 输入，往下滑确认新增的滑块都在，且鼠标加速默认是勾选的。'
assert old in s, 'anchor missing'
new = '\n'.join([
 '6. 设置 AVNC → 输入，往下滑确认新增的滑块都在，且鼠标加速默认是勾选的。',
 '7. 悬浮键盘上点「设置」→ 把「按键高度」调到 56 → 保存，键盘按键应该立刻变大；',
 '   退出图形界面再进，设置还在（写在 `~/.config/tiny-osk.conf`）。',
 '8. 设置 AVNC → 输入 → 把「三指轻点呼出键盘」关掉，三指轻点就不该再弹键盘了。',
])
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
