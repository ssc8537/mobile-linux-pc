import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\util\AppPreferences.kt'
raw = io.open(p, encoding='utf-8', newline='').read()
s = raw.replace('\r\n', '\n')
old = """        /** Show the floating on-screen-keyboard button ring around the cursor. */
        val oskButtonRing; get() = prefs.getBoolean("osk_button_ring", true)"""
new = """        /**
         * Show one small keyboard button next to the remote pointer.
         *
         * The button is placed in whichever of the eight surrounding directions has
         * room on screen, so it follows the cursor instead of sitting in a fixed corner.
         */
        val oskPointerButton; get() = prefs.getBoolean("osk_pointer_button", true)"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n'))
print('ok')
