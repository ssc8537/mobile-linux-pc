import io
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

p = os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main', 'java', 'com', 'gaurav', 'avnc', 'ui', 'vnc', 'input', 'TouchHandler.kt')
s = io.open(p, 'r', encoding='utf-8', newline='').read()
orig = s

# import SystemClock
old = 'import android.os.Build\r\n'
new = 'import android.os.Build\r\nimport android.os.SystemClock\r\n'
assert old in s
s = s.replace(old, new, 1)

# replace scale callbacks
old = ('    override fun onScaleBegin(detector: ScaleGestureDetector) = true\r\n'
       '    override fun onScaleEnd(detector: ScaleGestureDetector) {}\r\n'
       '    override fun onScale(detector: ScaleGestureDetector): Boolean {\r\n'
       '        if (swipeVsScale.shouldScale())\r\n'
       '            dispatcher.onScale(detector.scaleFactor, detector.focusX, detector.focusY)\r\n'
       '        return true\r\n'
       '    }\r\n')
new = ('    /****************************************************************************************\r\n'
       '     * Local fork: zoom mis-touch guard\r\n'
       '     *\r\n'
       '     * A single pinch is very easy to trigger by accident while tapping or scrolling,\r\n'
       '     * which zooms the whole desktop. When the guard is enabled we swallow the first\r\n'
       '     * pinch, show a hint, and only act if another pinch starts within\r\n'
       '     * [ZOOM_CONFIRM_WINDOW_MS] milliseconds.\r\n'
       '     */\r\n'
       '    private var zoomConfirmed = false\r\n'
       '    private var zoomHintShown = false\r\n'
       '    private var lastZoomAttemptTime = 0L\r\n'
       '\r\n'
       '    override fun onScaleBegin(detector: ScaleGestureDetector): Boolean {\r\n'
       '        if (!pref.input.zoomMisTouchGuard) {\r\n'
       '            zoomConfirmed = true\r\n'
       '            return true\r\n'
       '        }\r\n'
       '\r\n'
       '        val now = SystemClock.uptimeMillis()\r\n'
       '        if (lastZoomAttemptTime != 0L && now - lastZoomAttemptTime <= ZOOM_CONFIRM_WINDOW_MS) {\r\n'
       '            // Second attempt within the confirmation window: this one is intentional\r\n'
       '            zoomConfirmed = true\r\n'
       '            lastZoomAttemptTime = 0L\r\n'
       '        } else {\r\n'
       '            zoomConfirmed = false\r\n'
       '            zoomHintShown = false\r\n'
       '            lastZoomAttemptTime = now\r\n'
       '        }\r\n'
       '        return true\r\n'
       '    }\r\n'
       '\r\n'
       '    override fun onScaleEnd(detector: ScaleGestureDetector) {\r\n'
       '        zoomConfirmed = false\r\n'
       '    }\r\n'
       '\r\n'
       '    override fun onScale(detector: ScaleGestureDetector): Boolean {\r\n'
       '        if (!swipeVsScale.shouldScale())\r\n'
       '            return true\r\n'
       '\r\n'
       '        if (!zoomConfirmed) {\r\n'
       '            if (!zoomHintShown) {\r\n'
       '                zoomHintShown = true\r\n'
       '                dispatcher.onZoomMisTouchHint()\r\n'
       '            }\r\n'
       '            return true\r\n'
       '        }\r\n'
       '\r\n'
       '        dispatcher.onScale(detector.scaleFactor, detector.focusX, detector.focusY)\r\n'
       '        return true\r\n'
       '    }\r\n'
       '\r\n'
       '    companion object {\r\n'
       '        /** Time window within which a repeated pinch is accepted as intentional. */\r\n'
       '        private const val ZOOM_CONFIRM_WINDOW_MS = 1200L\r\n'
       '    }\r\n')
assert old in s, 'scale callback block not found'
s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched TouchHandler.kt', 'changed' if s != orig else 'UNCHANGED')
