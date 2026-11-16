import io
base = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\res'
zh_anchor = """    <string name="tc4_signal9_title">"""
zh_new = """    <string name="tc4_reimport_title">需要重新导入系统镜像</string>
    <string name="tc4_reimport_message">这个版本装了新的 Linux 系统镜像（新增了 Windows 风格任务栏、悬浮键盘、任务管理器等）。检测到你手机里还是旧镜像的容器，必须重新导入才能用上新功能。\n\n重新导入会清空现有容器里的个人数据。重要文件请先放到「公共」文件夹或导出容器。</string>
    <string name="tc4_reimport_confirm">重新导入（会清空容器数据）</string>
    <string name="tc4_reimport_later">这次先不导入</string>
"""
p = base + r'\values-zh-rCN\strings.xml'
s = io.open(p, encoding='utf-8', newline='').read()
assert zh_anchor in s and 'tc4_reimport_title' not in s
eol = '\r\n' if '\r\n' in s[:2000] else '\n'
s = s.replace(zh_anchor, zh_new.replace('\n', eol) + zh_anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('zh ok', repr(eol))

en_new = """    <string name="tc4_reimport_title">System image needs re-import</string>
    <string name="tc4_reimport_message">This build ships a new Linux system image (Windows-style taskbar, floating keyboard, task manager and more). Your phone still has a container made from the old image, so the new features cannot work.\n\nRe-importing erases personal data inside the current container. Move important files to the Public folder or export the container first.</string>
    <string name="tc4_reimport_confirm">Re-import (erases container data)</string>
    <string name="tc4_reimport_later">Not now</string>
"""
p2 = base + r'\values\strings.xml'
s2 = io.open(p2, encoding='utf-8', newline='').read()
# find the english signal9 title anchor
import re
m = re.search(r'[ \t]*<string name="tc4_signal9_title">', s2)
assert m, 'en anchor missing'
eol2 = '\r\n' if '\r\n' in s2[:2000] else '\n'
anchor2 = m.group(0)
s2 = s2.replace(anchor2, en_new.replace('\n', eol2) + anchor2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(s2)
print('en ok', repr(eol2))
