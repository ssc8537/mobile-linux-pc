import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt'
raw = io.open(p, encoding='utf-8', newline='').read()
s = raw.replace('\r\n', '\n')

start = s.index('    /************************************************************************************\n     * Local fork: on-screen keyboard helpers.')
endmark = '''    /**
     * Ask the remote desktop to show its floating keyboard.'''
end = s.index(endmark)
old_block = s[start:end]
assert 'oskRing' in old_block and 'toggleOskRing' in old_block

new_block = '''    /************************************************************************************
     * Local fork: on-screen keyboard helpers.
     *
     * The keyboard itself lives inside the Linux container, so the only job here is to
     * hand the request over: we send a dedicated keysym that the in-container keyboard
     * helper grabs globally. XF86XK_Launch0 is unused by every common desktop
     * application, so it collides with nothing.
     *
     * A single small keyboard button is drawn next to the remote pointer (whichever of
     * the eight surrounding directions still fits on screen). The button therefore
     * travels with the cursor instead of hiding in a fixed corner.
     ************************************************************************************/
    private val oskButtonSizeDp = 40
    private val oskButtonGapDp = 14

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private val oskFollowTick = object : Runnable {
        override fun run() {
            positionOskButton()
            binding.frameContainer.postDelayed(this, 100)
        }
    }

    private fun setupOskOverlay() {
        val btn = ImageButton(this)
        btn.setImageResource(R.drawable.ic_keyboard)
        btn.setBackgroundResource(R.drawable.bg_circular_button)
        btn.imageTintList = android.content.res.ColorStateList.valueOf(0xFFFFFFFF.toInt())
        btn.alpha = 0.6f
        btn.contentDescription = getString(R.string.osk_open_keyboard)
        btn.visibility = android.view.View.GONE
        btn.setOnClickListener { openRemoteKeyboard() }

        val size = dp(oskButtonSizeDp)
        val lp = FrameLayout.LayoutParams(size, size)
        lp.gravity = Gravity.TOP or Gravity.START
        binding.frameContainer.addView(btn, lp)

        oskButton = btn
        applyOskPrefs()
    }

    /** Re-read the preferences; called on start so switching them needs no restart. */
    fun applyOskPrefs() {
        val enabled = viewModel.pref.input.oskPointerButton
        if (!enabled)
            oskButton?.visibility = android.view.View.GONE
        binding.frameContainer.removeCallbacks(oskFollowTick)
        if (enabled)
            binding.frameContainer.post(oskFollowTick)
    }

    /**
     * Park the keyboard button in one of the eight directions around the pointer.
     * Directions are tried in order of preference and the first one that stays fully
     * on screen wins, so the button never gets clipped at a screen edge.
     */
    private fun positionOskButton() {
        val btn = oskButton ?: return
        val parentW = binding.frameContainer.width
        val parentH = binding.frameContainer.height
        if (parentW == 0 || parentH == 0)
            return

        val client = viewModel.client
        if (client == null || viewModel.state.value != VncViewModel.State.Connected) {
            btn.visibility = android.view.View.GONE
            return
        }

        val vp = viewModel.frameState.toVP(PointF(client.pointerX.toFloat(), client.pointerY.toFloat()))
        if (!vp.x.isFinite() || !vp.y.isFinite() || vp.x < 0 || vp.y < 0 ||
                vp.x > parentW || vp.y > parentH) {
            btn.visibility = android.view.View.GONE
            return
        }

        val size = dp(oskButtonSizeDp)
        val gap = dp(oskButtonGapDp) + size
        val offsets = floatArrayOf(
                gap.toFloat(), 0f,        // right
                -gap.toFloat(), 0f,       // left
                0f, gap.toFloat(),        // down
                0f, -gap.toFloat(),       // up
                gap.toFloat(), gap.toFloat(),
                gap.toFloat(), -gap.toFloat(),
                -gap.toFloat(), gap.toFloat(),
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
            // Pointer sits in a corner: clamp instead of hiding.
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
s = s[:start] + new_block + s[end:]

# stop the ticker with the activity
s = s.replace('''    override fun onStart() {
        super.onStart()
        applyOskPrefs()''', '''    override fun onStart() {
        super.onStart()
        applyOskPrefs()''', 1)

# field rename: oskFab / oskRing -> oskButton
s = s.replace('    private var oskFab: ImageButton? = null\n', '    private var oskButton: ImageButton? = null\n', 1)
s = s.replace('    private var oskRing: View? = null\n', '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('VncActivity OSK block replaced')
