import io, re
import os

def _find_ws():
    env = os.environ.get('TC_ROOT')
    if env:
        return env
    _d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(_d, 'build-env-toolchain')) or os.path.isdir(
            os.path.join(_d, 'source', 'app')
        ):
            return _d
        _p = os.path.dirname(_d)
        if _p == _d:
            return os.path.dirname(os.path.abspath(__file__))
        _d = _p


WS = _find_ws()
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main')
def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()
def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
def eol_of(s):
    return '\r\n' if s.count('\r\n') > s.count('\n') / 2 else '\n'

# ---------- AppPreferences ----------
p = ROOT + r'\java\com\gaurav\avnc\util\AppPreferences.kt'
s = rd(p)
old = """        val scrollSpeed: Int
            get() = prefs.getInt("scroll_speed", 3).coerceIn(1, 5)"""
assert old in s, 'scrollSpeed block missing'
new = """        val scrollSpeed: Int
            get() = prefs.getInt("scroll_speed", 3).coerceIn(1, 9)"""
s = s.replace(old, new, 1)

# cursor tint enable switch
old2 = """        /** Remote cursor tint (ARGB). 0 == no tint (draw cursor as sent by server). */
        val cursorTint: Int
            get() = prefs.getInt("cursor_tint", 0)"""
assert old2 in s, 'cursorTint block missing'
new2 = """        /** Master switch for the cursor colour below. Off == draw the cursor untouched. */
        val cursorTintEnabled; get() = prefs.getBoolean("cursor_tint_enabled", false)

        /** Remote cursor tint (ARGB). 0 == no tint (draw cursor as sent by server). */
        val cursorTint: Int
            get() = prefs.getInt("cursor_tint", 0)"""
s = s.replace(old2, new2, 1)

# fix zoom guard key mismatch (was zoom_mistouch_guard, XML uses zoom_mis_touch_guard)
old3 = 'prefs.getBoolean("zoom_mistouch_guard", true)'
assert old3 in s
s = s.replace(old3, 'prefs.getBoolean("zoom_mis_touch_guard", true)', 1)

# pointer button pref replaces the 3x3 ring pref
old4 = """        /** Shows a 3x3 button ring around the pointer. */
        val oskButtonRing; get() = prefs.getBoolean("osk_button_ring", true)"""
if old4 in s:
    s = s.replace(old4, """        /** Shows a single small keyboard button next to the pointer. */
        val oskPointerButton; get() = prefs.getBoolean("osk_pointer_button", true)""", 1)
else:
    m = re.search(r'[ \t]*val oskButtonRing[^\r\n]*', s)
    assert m, 'oskButtonRing missing'
    s = s.replace(m.group(0), """        /** Shows a single small keyboard button next to the pointer. */
        val oskPointerButton; get() = prefs.getBoolean("osk_pointer_button", true)""", 1)
wr(p, s)
print('AppPreferences ok')

# ---------- PointerModes: slower scroll range ----------
p = ROOT + r'\java\com\gaurav\avnc\ui\vnc\input\PointerModes.kt'
s = rd(p)
old = """    private val deltaPerScroll: Float
        get() = 12F + (viewModel.pref.input.scrollSpeed - 1) * 4F"""
assert old in s, 'deltaPerScroll missing'
new = """    private val deltaPerScroll: Float
        get() = 8F + (viewModel.pref.input.scrollSpeed - 1) * 6F"""
s = s.replace(old, new, 1)
wr(p, s)
print('PointerModes ok')

# ---------- Renderer: honour the tint switch ----------
p = ROOT + r'\java\com\gaurav\avnc\ui\vnc\gl\Renderer.kt'
s = rd(p)
m = re.search(r'[ \t]*val tint = viewModel\.pref\.input\.cursorTint[^\r\n]*\r?\n', s)
assert m, 'tint line missing'
print('--- tint context ---')
print(s[max(0, m.start()-400):m.end()+500])
