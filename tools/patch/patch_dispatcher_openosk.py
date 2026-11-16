import io

P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\input\Dispatcher.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

old = ('                "open-keyboard" -> { _ -> doOpenKeyboard() }\r\n')
new = ('                "open-keyboard" -> { _ -> doOpenKeyboard() }\r\n'
       '                "open-osk" -> { _ -> doOpenRemoteOsk() }\r\n')
assert old in s, 'selectPointAction open-keyboard case not found'
s = s.replace(old, new, 1)

old = '    private fun doOpenKeyboard() = activity.showKeyboard()\r\n'
new = ('    private fun doOpenKeyboard() = activity.showKeyboard()\r\n'
       '\r\n'
       '    /** Local fork: ask the remote desktop to show its floating keyboard. */\r\n'
       '    private fun doOpenRemoteOsk() = activity.openRemoteKeyboard()\r\n')
assert old in s
s = s.replace(old, new, 1)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched Dispatcher.kt open-osk action')
