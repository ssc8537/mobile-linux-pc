import io, re, os
ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main'

def stat(p):
    b = open(p,'rb').read()
    return b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')

for rel in [r'\java\com\gaurav\avnc\util\AppPreferences.kt',
            r'\java\com\gaurav\avnc\ui\vnc\input\PointerModes.kt',
            r'\java\com\gaurav\avnc\ui\vnc\gl\Renderer.kt',
            r'\java\com\gaurav\avnc\ui\vnc\VncActivity.kt',
            r'\java\com\gaurav\avnc\ui\vnc\input\Dispatcher.kt']:
    print(rel, stat(ROOT+rel))
