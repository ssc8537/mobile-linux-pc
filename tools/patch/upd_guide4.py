import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md'
s = io.open(p, encoding='utf-8', newline='').read()
s = s.replace('761,268,661', '761,288,905')
s = s.replace('913041ADCB3A683978330A305DFDB79084AB0F0B8AB90354A1CFA34D8D2935D6',
              '3EEE8A5CCD85C635BF636152D87D1F64F1DED0F607A45602867A4ABD74455AD4')
old = '- **新增软件**：任务管理器（Ctrl+Shift+Esc，和原来绑定的快捷键终于对上了）、\n  截图工具（Print 键）、剪贴板管理器（自动记录复制历史）。'
new = ('- **新增软件**：任务管理器（Ctrl+Shift+Esc，和原来绑定的快捷键终于对上了）、\n'
       '  截图工具（Print 键）、剪贴板管理器（开机自启，自动记录复制历史）。\n'
       '- **剪贴板历史像 Windows**：`Super+V` 弹出历史列表（= Windows 的 Win+V），\n'
       '  `Super+Shift+V` 打开完整管理窗口。')
assert old in s, 'clip anchor missing'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('guide updated')
