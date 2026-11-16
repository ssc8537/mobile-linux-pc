import io, sys

path = sys.argv[1]
src = io.open(path, 'r', encoding='utf-8', newline='').read()
assert '\r\n' in src

old_block = src[src.index('class PointerAcceleration'):]

new_block = '''class PointerAcceleration(private val viewModel: VncViewModel) {
    private val displayMetrics = viewModel.frameViewRef.get()!!.context.resources.displayMetrics
    private val xdpi = displayMetrics.xdpi
    private val ydpi = displayMetrics.ydpi
    private val tracker by lazy { VelocityTracker.obtain() }

    fun addMovement(event: MotionEvent) {
        tracker.addMovement(event)
    }

    fun clear() {
        tracker.clear()
    }

    fun compute() {
        tracker.computeCurrentVelocity(1000 /*per second*/)
    }

    fun updateDx(dx: Float): Float {
        return dx * calculateAccelerationFactor(tracker.xVelocity, xdpi)
    }

    fun updateDy(dy: Float): Float {
        return dy * calculateAccelerationFactor(tracker.yVelocity, ydpi)
    }

    private fun minFactor(): Float = viewModel.pref.input.slowPointerSpeed / 100f

    private fun maxFactor(): Float = strengthToMaxFactor(viewModel.pref.input.mouseAccelerationStrength)

    private fun calculateAccelerationFactor(vPixelPerSec: Float, dpi: Float): Float {
        if (vPixelPerSec == 0f)
            return 1f

        val vMmPerSec = pixelToMM(vPixelPerSec.absoluteValue, dpi)
        val zoomScale = viewModel.frameState.zoomScale

        if (viewModel.videoDisabled)
            return NoVideoTouchpadProfile.calculateAccelerationFactor(vMmPerSec, minFactor(), maxFactor())
        else
            return TouchpadProfile.calculateAccelerationFactor(vMmPerSec, zoomScale, minFactor(), maxFactor())
    }

    private fun pixelToMM(pixels: Float, dpi: Float): Float {
        return (pixels * 25.4f /*mm per inch*/) / dpi.coerceAtLeast(1f)
    }


    /***********************************************************************************
     * Acceleration Profiles
     ***********************************************************************************/

    companion object {
        /**
         * Maps the user facing strength (1..8) to the profile's max factor.
         * Strength 6 -> 3.5f, which is upstream's MAX_FACTOR, so the default
         * setting preserves upstream behaviour.
         */
        fun strengthToMaxFactor(strength: Int): Float = 0.5f + (strength.coerceIn(1, 8) - 1) * 0.6f
    }

    /**
     * This profile implements a three-layered acceleration factor:
     *
     *   |                -
     * ^ |              --
     * | |  _________---
     * f | /
     *   |/
     *   |  T1      T2
     *   +-------------------------
     *             v ->
     *
     * Local fork: [minFactor] (slow-movement floor) and [maxFactor] (fast-movement
     * ceiling) are configurable. Both default to the upstream constants.
     */
    object NoVideoTouchpadProfile {
        const val MIN_FACTOR = 0.3f
        const val MAX_FACTOR = 3.5f
        private const val BASELINE_FACTOR = 1f
        private const val THRESHOLD1 = 10f
        private const val THRESHOLD2 = 80f

        fun calculateAccelerationFactor(velocity: Float,
                                        minFactor: Float = MIN_FACTOR,
                                        maxFactor: Float = MAX_FACTOR): Float {
            val min = minFactor.coerceIn(0.05f, BASELINE_FACTOR)
            val max = maxFactor.coerceIn(BASELINE_FACTOR, 8f)
            val initialSlope = (BASELINE_FACTOR - min) / THRESHOLD1

            val f = when {
                // For very slow movement, acceleration factor increases linearly (y = mx + c).
                // In this phase, it decelerates the pointer, allowing precise control
                velocity < THRESHOLD1 -> initialSlope * velocity + min

                // For normal velocity, constant acceleration factor is used to allow normal
                // 1-to-1 pointer movement
                velocity < THRESHOLD2 -> BASELINE_FACTOR

                // When velocity starts increasing above T2, acceleration factor starts increasing
                // quadratically to move the pointer faster and faster.
                // Following equation is basically y = x^2, with a multiplier to reduce the y value.
                else -> 0.0005f * ((velocity * velocity) / THRESHOLD2) + BASELINE_FACTOR
            }
            return f.coerceIn(min, max)
        }
    }

    /**
     * This profile works similar to [NoVideoTouchpadProfile], but it dampens
     * the acceleration factor as zoom level increases.
     *
     * This dampening allows more precise pointer control on higher zoom levels.
     */
    object TouchpadProfile {
        fun calculateAccelerationFactor(velocity: Float,
                                        zoomScale: Float,
                                        minFactor: Float = NoVideoTouchpadProfile.MIN_FACTOR,
                                        maxFactor: Float = NoVideoTouchpadProfile.MAX_FACTOR): Float {
            val f = NoVideoTouchpadProfile.calculateAccelerationFactor(velocity, minFactor, maxFactor)
            if (zoomScale <= 1)
                return f

            // There are two main features of this dampening:
            // - Proportional to zoomScale: More dampening happens as zoom increases
            // - Proportional to acceleration factor: higher factors are affected more than the lower factors
            //
            // It can be represented as a "dynamic line", whose slope increases with the zoom level.
            val dampenerSlope = (zoomScale - 1) * .07f            // Maps [1-5] zoom to [0-.28] slope
            val dampener = (dampenerSlope * f).coerceIn(0f, 1f)   // At zoomScale = 5 & f = 3.5, dampener => 1
            val result = f - dampener

            return result.coerceAtLeast(minFactor)
        }
    }
}
'''.replace('\n', '\r\n')

src = src.replace(old_block, new_block)
io.open(path, 'w', encoding='utf-8', newline='').write(src)
print('rewritten', path)
