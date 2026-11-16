import io

P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

# ------------------------------------------------------------------ imports
old = 'import android.view.KeyEvent\r\n'
new = ('import android.view.Gravity\r\n'
       'import android.view.KeyEvent\r\n')
assert old in s
s = s.replace(old, new, 1)

old = 'import android.widget.Toast\r\n'
new = ('import android.widget.FrameLayout\r\n'
       'import android.widget.ImageButton\r\n'
       'import android.widget.Toast\r\n')
assert old in s
s = s.replace(old, new, 1)

old = 'import com.gaurav.avnc.databinding.ViewerHelpBinding\r\n'
new = ('import com.gaurav.avnc.databinding.ViewZoomHintBinding\r\n'
       'import com.gaurav.avnc.databinding.ViewerHelpBinding\r\n')
assert old in s
s = s.replace(old, new, 1)

old = 'import java.lang.ref.WeakReference\r\n'
new = ('import java.lang.ref.WeakReference\r\n'
       'import android.graphics.PointF\r\n')
assert old in s
s = s.replace(old, new, 1)

# ------------------------------------------------------------------ fields
old = '    private val layoutManager by lazy { LayoutManager(this) }\r\n'
new = ('    private val layoutManager by lazy { LayoutManager(this) }\r\n'
       '\r\n'
       '    // Local fork: overlays for the on-screen keyboard helpers and zoom guard\r\n'
       '    private var zoomHintView: android.view.View? = null\r\n'
       '    private var oskFab: ImageButton? = null\r\n'
       '    private var oskRing: android.view.View? = null\r\n')
assert old in s
s = s.replace(old, new, 1)

# ------------------------------------------------------------------ onCreate hook
old = ('        setupLayout()\r\n'
       '        setupNoVideoOverlay()\r\n')
new = ('        setupLayout()\r\n'
       '        setupNoVideoOverlay()\r\n'
       '        setupOskOverlay()\r\n')
assert old in s
s = s.replace(old, new, 1)

# ------------------------------------------------------------------ inset the new code before showKeyboard()
anchor = '    fun showKeyboard() {\r\n'
assert anchor in s

BLOCK = r'''    /************************************************************************************
     * Local fork: zoom mis-touch guard.
     *
     * A single accidental pinch is very easy to do while tapping or scrolling, and it
     * zooms the whole desktop. TouchHandler asks us to show a short hint the first time,
     * and only honours a second pinch within its confirmation window.
     ************************************************************************************/
    fun showZoomMisTouchHint() {
        if (isFinishing || isDestroyed)
            return

        zoomHintView?.let { binding.frameContainer.removeView(it) }

        val hintBinding = ViewZoomHintBinding.inflate(layoutInflater, binding.frameContainer, false)
        binding.frameContainer.addView(hintBinding.root)
        zoomHintView = hintBinding.root

        hintBinding.root.alpha = 0f
        hintBinding.root.animate().alpha(1f).setDuration(150).withEndAction {
            hintBinding.root.animate().alpha(0f).setStartDelay(1400).setDuration(400)
                    .withEndAction {
                        binding.frameContainer.removeView(hintBinding.root)
                        if (zoomHintView === hintBinding.root)
                            zoomHintView = null
                    }
        }
    }


    /************************************************************************************
     * Local fork: on-screen keyboard helpers.
     *
     * Two independent helpers, each with its own preference switch:
     *
     * - A small floating keyboard button (right edge). Tapping it pops up a 3x3 ring
     *   around the remote pointer. The eight outer cells nudge the pointer by a fixed
     *   step, the centre cell opens the keyboard on the remote desktop. The ring is the
     *   answer to "the pointer is always somewhere else than my finger".
     *
     * - A three-finger tap (wired in the gesture preferences) opens the keyboard directly.
     ************************************************************************************/
    private val oskRingButtonSizeDp = 44
    private val oskRingMarginDp = 2

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private fun setupOskOverlay() {
        val fab = ImageButton(this)
        fab.setImageResource(R.drawable.ic_keyboard)
        fab.setBackgroundResource(R.drawable.bg_circular_button)
        fab.imageTintList = android.content.res.ColorStateList.valueOf(0xFFFFFFFF.toInt())
        fab.alpha = 0.75f
        fab.contentDescription = getString(R.string.osk_open_keyboard)
        fab.setOnClickListener { toggleOskRing() }

        val size = dp(oskRingButtonSizeDp)
        val lp = FrameLayout.LayoutParams(size, size)
        lp.gravity = Gravity.END or Gravity.CENTER_VERTICAL
        lp.marginEnd = dp(6)
        binding.frameContainer.addView(fab, lp)

        oskFab = fab
        applyOskPrefs()
    }

    /** Re-read the preferences; called on start so switching them needs no restart. */
    fun applyOskPrefs() {
        val ringEnabled = viewModel.pref.input.oskButtonRing
        oskFab?.visibility = if (ringEnabled) android.view.View.VISIBLE else android.view.View.GONE
        if (!ringEnabled)
            hideOskRing()
    }

    private fun toggleOskRing() {
        if (oskRing != null) {
            hideOskRing()
            return
        }
        showOskRing()
    }

    private fun showOskRing() {
        hideOskRing()

        val ring = layoutInflater.inflate(R.layout.view_osk_ring, binding.frameContainer, false)
        binding.frameContainer.addView(ring)
        oskRing = ring

        // Wire the centre cell: open the keyboard on the remote desktop
        ring.findViewById<ImageButton>(R.id.osk_open).setOnClickListener {
            hideOskRing()
            openRemoteKeyboard()
        }

        // Wire the eight nudge cells
        val step = dp(28).toFloat()
        val nudges = mapOf(
                R.id.nudge_up_left to (PointF(-step, -step)),
                R.id.nudge_up to (PointF(0f, -step)),
                R.id.nudge_up_right to (PointF(step, -step)),
                R.id.nudge_left to (PointF(-step, 0f)),
                R.id.nudge_right to (PointF(step, 0f)),
                R.id.nudge_down_left to (PointF(-step, step)),
                R.id.nudge_down to (PointF(0f, step)),
                R.id.nudge_down_right to (PointF(step, step))
        )
        nudges.forEach { (id, delta) ->
            ring.findViewById<ImageButton>(id).setOnClickListener {
                inputHandler.nudgePointer(delta.x, delta.y)
            }
        }

        // Position the ring around the remote pointer, clamped on screen
        ring.post {
            val parentW = binding.frameContainer.width
            val parentH = binding.frameContainer.height
            if (parentW == 0 || parentH == 0)
                return@post

            var centerX = parentW - dp(oskRingButtonSizeDp) * 2
            var centerY = parentH / 2

            val client = viewModel.client
            if (client != null) {
                val vp = viewModel.frameState.toVP(PointF(client.pointerX.toFloat(), client.pointerY.toFloat()))
                if (vp.x.isFinite() && vp.y.isFinite()) {
                    centerX = vp.x.toInt()
                    centerY = vp.y.toInt()
                }
            }

            val ringW = ring.width
            val ringH = ring.height
            val left = (centerX - ringW / 2).coerceIn(0, maxOf(0, parentW - ringW))
            val top = (centerY - ringH / 2).coerceIn(0, maxOf(0, parentH - ringH))

            (ring.layoutParams as? FrameLayout.LayoutParams)?.let {
                it.gravity = Gravity.TOP or Gravity.START
                it.leftMargin = left
                it.topMargin = top
                ring.layoutParams = it
            }
        }

        // Fade in
        ring.alpha = 0f
        ring.animate().alpha(1f).setDuration(120).start()
    }

    private fun hideOskRing() {
        oskRing?.let { binding.frameContainer.removeView(it) }
        oskRing = null
    }

    /**
     * Ask the remote desktop to show its floating keyboard.
     *
     * The keyboard lives inside the container, so we cannot call it directly. Instead we
     * send a dedicated keysym that the keyboard helper grabs globally. XF86XK_Launch0 is
     * unused by every common desktop application, so it collides with nothing.
     */
    fun openRemoteKeyboard() {
        val keySym = 0x1008FF40 // XF86XK_Launch0
        inputHandler.sendKeySym(keySym, true)
        inputHandler.sendKeySym(keySym, false)
        Toast.makeText(this, R.string.osk_request_sent, Toast.LENGTH_SHORT).show()
    }

'''

s = s.replace(anchor, BLOCK + anchor, 1)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched VncActivity.kt')
