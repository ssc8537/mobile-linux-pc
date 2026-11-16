import io, re
BASE = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'

def ins(path, anchor_re, block, before=True):
    raw = io.open(path, encoding='utf-8', newline='').read()
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    m = re.search(anchor_re, s, re.M)
    assert m, 'anchor missing in ' + path
    b = block if before else m.group(0) + block
    if before:
        s = s[:m.start()] + b + s[m.start():]
    else:
        s = s[:m.end()] + b + s[m.end():]
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)

en = """    <!-- Local fork: value labels -->
    <string name="value_prefix_accel">Accel </string>
    <string name="value_suffix_multiplier">x</string>
    <string name="value_suffix_percent">%%</string>
    <string name="value_prefix_scroll">Step </string>
"""
zh = """    <!-- Local fork: value labels -->
    <string name="value_prefix_accel">加速 </string>
    <string name="value_suffix_multiplier"> 倍</string>
    <string name="value_suffix_percent">%%</string>
    <string name="value_prefix_scroll">档位 </string>
"""
ins(BASE + r'\values\strings.xml', r'^[ \t]*<string name="pref_mouse_acceleration">', en)
ins(BASE + r'\values-zh-rCN\strings.xml', r'^[ \t]*<string name="pref_mouse_acceleration">', zh)

en2 = """    <string name="pref_cursor_tint_enabled">Colour the cursor</string>
    <string name="msg_cursor_tint_enabled_help">Turn this on to use the colour below. When off, the cursor is drawn exactly as the server sends it.</string>
"""
zh2 = """    <string name="pref_cursor_tint_enabled">启用指针颜色</string>
    <string name="msg_cursor_tint_enabled_help">打开后才会使用下面的颜色。关闭时指针完全按服务器发来的样子显示。</string>
"""
ins(BASE + r'\values\strings.xml', r'^[ \t]*<string name="pref_cursor_tint">', en2)
ins(BASE + r'\values-zh-rCN\strings.xml', r'^[ \t]*<string name="pref_cursor_tint">', zh2)

en3 = """    <string name="pref_osk_pointer_button">Keyboard button near cursor</string>
    <string name="msg_osk_pointer_button_help">Puts one small keyboard button right next to the mouse pointer. It moves with the cursor and jumps to whichever side still fits on screen. Tap it to open the floating keyboard inside Linux.</string>
"""
zh3 = """    <string name="pref_osk_pointer_button">光标旁的键盘按钮</string>
    <string name="msg_osk_pointer_button_help">在鼠标指针旁边显示一个小键盘按钮。它会跟着光标移动，并自动选一个不会超出屏幕的方向。点它就呼出 Linux 里的悬浮键盘。</string>
"""
ins(BASE + r'\values\strings.xml', r'^[ \t]*<string name="pref_osk_button_ring">', en3)
ins(BASE + r'\values-zh-rCN\strings.xml', r'^[ \t]*<string name="pref_osk_button_ring">', zh3)
print('strings ok')
