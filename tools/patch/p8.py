import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\gl\Renderer.kt'
raw = io.open(p, encoding='utf-8', newline='').read()
s = raw.replace('\r\n', '\n')
old = """            val tint = viewModel.pref.input.cursorTint
            if (tint == 0)
                program.setTint(0f, 0f, 0f, false)
            else"""
assert old in s, 'tint block missing'
new = """            val tint = viewModel.pref.input.cursorTint
            if (tint == 0 || !viewModel.pref.input.cursorTintEnabled)
                program.setTint(0f, 0f, 0f, false)
            else"""
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if '\r\n' in raw else s)
print('Renderer ok')
