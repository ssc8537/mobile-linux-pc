import io, re
BASE = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main'

def load(p):
    raw = io.open(p, encoding='utf-8', newline='').read()
    crlf = raw.count('\r\n')
    lf = raw.count('\n') - crlf
    return raw, crlf, lf

def readlf(p):
    raw, c, l = load(p)
    s = raw.replace('\r\n', '\n')
    return s, ('crlf' if c > l else 'lf')

def write(p, s, style):
    if style == 'crlf':
        s = s.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)

def patch(rel, pairs):
    p = BASE + rel
    s, style = readlf(p)
    for old, new in pairs:
        assert old in s, 'MISSING in %s: %r' % (rel, old[:80])
        s = s.replace(old, new, 1)
    write(p, s, style)
    print('patched', rel, style)

patch(r'\java\com\gaurav\avnc\util\AppPreferences.kt', [
("""        val scrollSpeed: Int
            get() = prefs.getInt("scroll_speed", 3).coerceIn(1, 5)""",
"""        val scrollSpeed: Int
            get() = prefs.getInt("scroll_speed", 3).coerceIn(1, 9)"""),
("""        /** Remote cursor tint (ARGB). 0 == no tint (draw cursor as sent by server). */
        val cursorTint: Int
            get() = prefs.getInt("cursor_tint", 0)""",
"""        /** Master switch for the cursor colour below. Off == draw the cursor untouched. */
        val cursorTintEnabled; get() = prefs.getBoolean("cursor_tint_enabled", false)

        /** Remote cursor tint (ARGB). 0 == no tint (draw cursor as sent by server). */
        val cursorTint: Int
            get() = prefs.getInt("cursor_tint", 0)"""),
('prefs.getBoolean("zoom_mistouch_guard", true)',
 'prefs.getBoolean("zoom_mis_touch_guard", true)'),
])
