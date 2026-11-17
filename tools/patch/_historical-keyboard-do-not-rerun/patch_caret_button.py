# -*- coding: utf-8 -*-
"""V5: put the keyboard button next to the TEXT CARET, not next to the mouse.

The in-container bridge (tiny_osk_caret.py) publishes the caret rectangle to
/tmp/.tiny_osk_caret, which is bind-mounted to the host at filesDir/tmp. So the
viewer can simply read that file — no permission, no protocol change.

Button visibility also changes: it is hidden unless a caret/text field is known,
which is exactly what the user asked for ("光标就是那个打字一闪一闪的那个光标").
"""
import io
import os

P = (r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
     r"\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt")
src = io.open(P, encoding="utf-8", newline="").read()
eol = "\r\n" if src.count("\r\n") > src.count("\n") / 2 else "\n"
print("eol=%r crlf=%d lf=%d" % (eol, src.count("\r\n"), src.count("\n") - src.count("\r\n")))

# ------------------------------------------------------------------ 1. new fields
old_field = "    private var oskTriggerPath: String? = null"
assert old_field in src
src = src.replace(
    old_field,
    old_field + "\n"
    "    /** Caret rectangle published by tiny_osk_caret.py inside the container. */\n"
    "    private var oskCaretPath: String? = null\n"
    "    private var oskCaretStamp = 0L\n"
    "    private var oskCaretRect: FloatArray? = null",
    1,
)

# ------------------------------------------------- 2. derive caret path from intent
old_read = '        oskTriggerPath = intent.getStringExtra("tc4.osk_trigger")'
assert old_read in src
src = src.replace(
    old_read,
    old_read + "\n"
    '        val triggerParent = oskTriggerPath?.let { File(it).parentFile }',
    1,
)
# the parent is only usable a couple of lines later; do it inline instead
src = src.replace(
    '        oskTriggerPath = intent.getStringExtra("tc4.osk_trigger")\n'
    '        val triggerParent = oskTriggerPath?.let { File(it).parentFile }',
    '        oskTriggerPath = intent.getStringExtra("tc4.osk_trigger")\n'
    '        oskCaretPath = intent.getStringExtra("tc4.osk_caret")',
    1,
)

# ------------------------------------------------------- 3. caret-driven placement
start = src.index("    private fun positionOskButton() {")
end = src.index("    /**\n     * Ask the remote desktop to show its floating keyboard.")
new_body = '''    /**
     * Read the caret rectangle published by the container bridge.
     *
     * The file holds one line: `visible x y w h` in remote-desktop pixels. It is
     * written by tiny_osk_caret.py every ~180 ms, and /tmp inside the container is
     * bind-mounted to the app's filesDir/tmp, so we just read it from disk.
     */
    private fun readCaretRect(): FloatArray? {
        val path = oskCaretPath ?: return null
        val file = File(path)
        val stamp = try {
            if (!file.exists()) return null
            file.lastModified()
        } catch (e: Exception) {
            return null
        }
        if (stamp == oskCaretStamp) return oskCaretRect
        oskCaretStamp = stamp
        oskCaretRect = try {
            val parts = file.readText().trim().split(' ')
            if (parts.size < 5 || parts[0] != "1") null
            else floatArrayOf(
                    parts[1].toFloat(), parts[2].toFloat(),
                    parts[3].toFloat(), parts[4].toFloat())
        } catch (e: Exception) {
            null
        }
        return oskCaretRect
    }

    /**
     * Park the keyboard button beside the text caret.
     *
     * The caret sits inside the remote framebuffer, so it is mapped through the
     * same frame->view transform the renderer uses. Eight candidate directions are
     * tried and the first that stays fully on screen wins, so the button never gets
     * clipped at an edge. When the desktop reports no caret, the button hides.
     */
    private fun positionOskButton() {
        val btn = oskButton ?: return
        val parentW = binding.frameContainer.width
        val parentH = binding.frameContainer.height
        if (parentW == 0 || parentH == 0)
            return

        if (viewModel.client == null || !viewModel.connected) {
            btn.visibility = android.view.View.GONE
            return
        }

        val caret = readCaretRect()
        if (caret == null) {
            // No caret / no text field focused: stay out of the way entirely.
            btn.visibility = android.view.View.GONE
            return
        }

        // Anchor at the caret's bottom-right corner: that is where typing continues.
        val anchorX = caret[0] + caret[2]
        val anchorY = caret[1] + caret[3]
        val vp = viewModel.frameState.toVP(PointF(anchorX, anchorY))
        if (!vp.x.isFinite() || !vp.y.isFinite() || vp.x < 0 || vp.y < 0 ||
                vp.x > parentW || vp.y > parentH) {
            btn.visibility = android.view.View.GONE
            return
        }

        val size = dp(oskButtonSizeDp)
        val gap = dp(oskButtonGapDp) + size
        val offsets = floatArrayOf(
                gap.toFloat(), 0f,        // right
                0f, gap.toFloat(),        // down
                gap.toFloat(), gap.toFloat(),
                0f, -gap.toFloat(),       // up
                -gap.toFloat(), 0f,       // left
                -gap.toFloat(), gap.toFloat(),
                gap.toFloat(), -gap.toFloat(),
                -gap.toFloat(), -gap.toFloat()
        )

        var left = -1
        var top = -1
        var i = 0
        while (i < offsets.size) {
            val l = (vp.x + offsets[i] - size / 2f).toInt()
            val t = (vp.y + offsets[i + 1] - size / 2f).toInt()
            if (l >= dp(4) && t >= dp(4) && l + size <= parentW - dp(4) && t + size <= parentH - dp(4)) {
                left = l
                top = t
                break
            }
            i += 2
        }
        if (left < 0) {
            left = (vp.x - size / 2f).toInt().coerceIn(0, maxOf(0, parentW - size))
            top = (vp.y - size / 2f).toInt().coerceIn(0, maxOf(0, parentH - size))
        }

        (btn.layoutParams as? FrameLayout.LayoutParams)?.let {
            it.leftMargin = left
            it.topMargin = top
            btn.layoutParams = it
        }
        if (btn.visibility != android.view.View.VISIBLE)
            btn.visibility = android.view.View.VISIBLE
    }

'''
src = src[:start] + new_body + src[end:]

if eol == "\r\n":
    src = src.replace("\r\n", "\n").replace("\n", "\r\n")

io.open(P, "w", encoding="utf-8", newline="").write(src)
print("written %d bytes" % len(src))
for n in ("readCaretRect", "oskCaretPath", "tc4.osk_caret", "caret[0] + caret[2]"):
    print("  ", n, src.count(n))
