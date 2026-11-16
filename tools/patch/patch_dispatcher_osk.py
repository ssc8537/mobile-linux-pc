import io

BASE = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\input'

# ---------------------------------------------------------------- Dispatcher
P = BASE + r'\Dispatcher.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

old = '    fun onScale(scaleFactor: Float, fx: Float, fy: Float) = doScale(scaleFactor, fx, fy)\r\n'
new = ('    fun onScale(scaleFactor: Float, fx: Float, fy: Float) = doScale(scaleFactor, fx, fy)\r\n'
       '\r\n'
       '    /**\r\n'
       '     * Local fork: called by [TouchHandler] when a pinch was swallowed by the\r\n'
       '     * zoom mis-touch guard, so the activity can show its hint.\r\n'
       '     */\r\n'
       '    fun onZoomMisTouchHint() = activity.showZoomMisTouchHint()\r\n'
       '\r\n'
       '    /**\r\n'
       '     * Local fork: move the remote pointer by a fixed step, without acceleration.\r\n'
       '     * Used by the pointer ring overlay.\r\n'
       '     */\r\n'
       '    fun nudgePointer(dx: Float, dy: Float) = relativeMode.doMovePointer(dx, dy, false)\r\n')
assert old in s, 'onScale not found in Dispatcher'
s = s.replace(old, new, 1)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched Dispatcher.kt')

# ---------------------------------------------------------------- InputHandler
P = BASE + r'\InputHandler.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

old = '    fun onTouchEvent(event: MotionEvent): Boolean {\r\n'
new = ('    /**\r\n'
       '     * Local fork: move the remote pointer by a fixed step (pointer ring overlay).\r\n'
       '     */\r\n'
       '    fun nudgePointer(dx: Float, dy: Float) {\r\n'
       '        dispatcher?.nudgePointer(dx, dy)\r\n'
       '    }\r\n'
       '\r\n'
       '    /**\r\n'
       '     * Local fork: send a bare keysym to the remote side.\r\n'
       '     */\r\n'
       '    fun sendKeySym(keySym: Int, isDown: Boolean) {\r\n'
       '        dispatcher?.onXKey(keySym, 0, isDown)\r\n'
       '    }\r\n'
       '\r\n'
       '    fun onTouchEvent(event: MotionEvent): Boolean {\r\n')
assert old in s, 'onTouchEvent not found in InputHandler'
s = s.replace(old, new, 1)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched InputHandler.kt')
