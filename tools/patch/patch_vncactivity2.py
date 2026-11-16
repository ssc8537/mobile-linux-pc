import io, os

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'

def rd(p):
    return io.open(p, 'r', encoding='utf-8', newline='').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', os.path.relpath(p, ROOT))

for rel, text in (('values/strings.xml', 'Keyboard request sent to the desktop'),
                  ('values-zh-rCN/strings.xml', '已向桌面发送键盘请求')):
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    s = rd(p)
    if 'osk_request_sent' in s:
        print('already present', rel)
        continue
    anchor = s.index('<string name="osk_open_keyboard">')
    s = s[:anchor] + '    <string name="osk_request_sent">%s</string>\r\n' % text + s[anchor:]
    wr(p, s)

# --------------------------------------------------------------- VncActivity onStart
P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt'
s = rd(P)
old = ('    override fun onStart() {\r\n'
       '        super.onStart()\r\n'
       '        binding.frameView.onResume()\r\n')
new = ('    override fun onStart() {\r\n'
       '        super.onStart()\r\n'
       '        binding.frameView.onResume()\r\n'
       '        applyOskPrefs()\r\n')
assert old in s, 'onStart block not found'
s = s.replace(old, new, 1)
wr(P, s)
print('DONE')
