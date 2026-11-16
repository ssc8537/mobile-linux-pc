import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\input\PointerModes.kt"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

old = """    /**
     * For how much dx/dy, one scroll event will be sent.
     *
     * Local fork: this used to be a hardcoded 20F. It is now derived from the
     * 'scroll_speed' preference (1..5); 3 (the default) evaluates to the original 20F.
     * A larger value means more finger travel per wheel click, i.e. slower scrolling.
     */
    private val deltaPerScroll: Float
        get() = 12F + (viewModel.pref.input.scrollSpeed - 1) * 4F
"""
new = """    /**
     * For how much dx/dy, one scroll event will be sent.
     *
     * Local fork: this used to be a hardcoded 20F. It is now derived from the
     * 'scroll_speed' preference (1..9), where 3 (the default) still evaluates to the
     * original 20F so an untouched install behaves exactly like upstream.
     *
     * A larger value means more finger travel per wheel click, i.e. slower scrolling.
     * Steps above 3 grow faster than the ones below, because the whole point of the
     * preference is to let the user scroll in truly small increments.
     *   1 -> 12px (faster than upstream)   6 -> 47px
     *   2 -> 16px                          7 -> 56px
     *   3 -> 20px (upstream default)       8 -> 65px
     *   4 -> 29px                          9 -> 74px (3.7x slower than upstream)
     *   5 -> 38px
     */
    private val deltaPerScroll: Float
        get() = if (viewModel.pref.input.scrollSpeed <= 3)
            8F + viewModel.pref.input.scrollSpeed * 4F
        else
            20F + (viewModel.pref.input.scrollSpeed - 3) * 9F
"""
assert old in t, "scroll block not found"
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("PointerModes patched, eol=%r bytes=%d" % (eol, len(t)))
