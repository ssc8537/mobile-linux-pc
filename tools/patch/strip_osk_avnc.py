# -*- coding: utf-8 -*-
"""Remove every trace of the on-screen keyboard work (user order m03615).

Keeps: zoom mis-touch guard, pointer tuning, cursor colour/size, restored
official preference categories.
"""
import io
import os
import re

R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
AVNC = os.path.join(R, "avnc-upstream-fork-deletable", "app", "src", "main")
HOST = os.path.join(R, "build-env-toolchain", "ws-gradle-build-copy-deletable",
                    "tiny_container", "app", "src", "main", "java", "com", "fct", "tc4")

log = []


def read(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def patch(path, edits, label, must_remain=None):
    raw = read(path)
    crlf = "\r\n" in raw
    src = raw.replace("\r\n", "\n")
    for old, new in edits:
        if old not in src:
            raise SystemExit("MISS in %s:\n---\n%s\n---" % (label, old[:400]))
        src = src.replace(old, new, 1)
    if must_remain:
        for token in must_remain:
            if token not in src:
                raise SystemExit("%s: destroyed %r" % (label, token))
    out = src.replace("\n", "\r\n") if crlf else src
    write(path, out)
    log.append("%s: OK (%d bytes, eol=%s)" % (label, len(out.encode("utf-8")), "crlf" if crlf else "lf"))


# ---------------------------------------------------------------- VncActivity
vnc = os.path.join(AVNC, "java", "com", "gaurav", "avnc", "ui", "vnc", "VncActivity.kt")
raw = read(vnc)
src = raw.replace("\r\n", "\n")

start = src.index("    /************************************************************************************\n"
                  "     * Local fork: on-screen keyboard helpers.")
end = src.index("    fun showKeyboard() {")
block = src[start:end]
for token in ("openRemoteKeyboard", "positionOskButton", "readCaretRect", "setupOskOverlay"):
    if token not in block:
        raise SystemExit("VncActivity: block missing %s" % token)
src = src[:start] + src[end:]

src = src.replace("""    private var oskButton: ImageButton? = null
    private var oskTriggerPath: String? = null
    /** Caret rectangle published by tiny_osk_caret.py inside the container. */
    private var oskCaretPath: String? = null
    private var oskCaretStamp = 0L
    private var oskCaretRect: FloatArray? = null
""", "")
src = src.replace("""        oskTriggerPath = intent.getStringExtra("tc4.osk_trigger")
        oskCaretPath = intent.getStringExtra("tc4.osk_caret")
""", "")
src = src.replace("""        setupNoVideoOverlay()
        setupOskOverlay()
""", """        setupNoVideoOverlay()
""")
src = src.replace("""        binding.frameView.onResume()
        applyOskPrefs()
""", """        binding.frameView.onResume()
""")
src = src.replace("""        super.onStop()
        binding.frameContainer.removeCallbacks(oskFollowTick)
        virtualKeys.releaseMetaKeys()
""", """        super.onStop()
        virtualKeys.releaseMetaKeys()
""")
src = src.replace("import com.gaurav.avnc.util.OskBridge\n", "")
src = src.replace("import android.graphics.PointF\n", "")

out = src.replace("\n", "\r\n") if "\r\n" in raw else src
write(vnc, out)
log.append("VncActivity.kt: OK (%d bytes)" % len(out.encode("utf-8")))
left = [l.strip() for l in out.splitlines() if "osk" in l.lower()]
if left:
    raise SystemExit("VncActivity still mentions osk: %s" % left)

# keep/drop imports based on remaining usage in the class body
raw = read(vnc)
for imp, sym in (("import android.view.Gravity\n", "Gravity"),
                 ("import android.widget.ImageButton\n", "ImageButton"),
                 ("import android.widget.FrameLayout\n", "FrameLayout")):
    if imp not in raw:
        continue
    body = raw.replace(imp, "")
    body_no_imports = "\n".join(l for l in body.splitlines() if not l.startswith("import "))
    if re.search(r"\b%s\b" % sym, body_no_imports):
        log.append("VncActivity: keep import %s (still used)" % sym)
    else:
        write(vnc, body)
        log.append("VncActivity: drop import %s" % sym)

# ---------------------------------------------------------------- Dispatcher
patch(os.path.join(AVNC, "java", "com", "gaurav", "avnc", "ui", "vnc", "input", "Dispatcher.kt"),
      [('                "open-keyboard" -> { _ -> doOpenKeyboard() }\n'
        '                "open-osk" -> { _ -> doOpenRemoteOsk() }\n',
        '                "open-keyboard" -> { _ -> doOpenKeyboard() }\n'),
       ("""
    /**
     * Local fork: move the remote pointer by a fixed step, without acceleration.
     * Used by the pointer ring overlay.
     */
    fun nudgePointer(dx: Float, dy: Float) = relativeMode.doMovePointer(dx, dy, false)
""", ""),
       ("""
    /** Local fork: ask the remote desktop to show its floating keyboard. */
    private fun doOpenRemoteOsk() {
        // Local fork: the three-finger tap is optional, gated by its own switch.
        if (!viewModel.pref.input.oskThreeFingerTap)
            return
        activity.openRemoteKeyboard()
    }
""", "")],
      "Dispatcher.kt", must_remain=["doOpenKeyboard", "onZoomMisTouchHint"])

# ---------------------------------------------------------------- InputHandler
patch(os.path.join(AVNC, "java", "com", "gaurav", "avnc", "ui", "vnc", "input", "InputHandler.kt"),
      [("""
    /**
     * Local fork: move the remote pointer by a fixed step (pointer ring overlay).
     */
    fun nudgePointer(dx: Float, dy: Float) {
        dispatcher?.nudgePointer(dx, dy)
    }

    /**
     * Local fork: send a bare keysym to the remote side.
     */
    fun sendKeySym(keySym: Int, isDown: Boolean) {
        dispatcher?.onXKey(keySym, 0, isDown)
    }
""", "")],
      "InputHandler.kt", must_remain=["fun onVkKeyEvent", "fun onTouchEvent"])

# ---------------------------------------------------------------- AppPreferences
prefs = os.path.join(AVNC, "java", "com", "gaurav", "avnc", "util", "AppPreferences.kt")
patch(prefs,
      [('val tap3; get() = prefs.getString("gesture_tap3", "open-osk")!!',
        'val tap3; get() = prefs.getString("gesture_tap3", "none")!!'),
       ('    val oskPointerButton; get() = prefs.getBoolean("osk_pointer_button", true)\n', ""),
       ('    val oskThreeFingerTap; get() = prefs.getBoolean("osk_three_finger_tap", true)\n', "")],
      "AppPreferences.kt", must_remain=["mouseAcceleration", "cursorTintEnabled", "zoomMisTouchGuard"])

# ---------------------------------------------------------------- arrays.xml
patch(os.path.join(AVNC, "res", "values", "arrays.xml"),
      [("""        <item>@string/pref_gesture_action_middle_click</item>
        <item>@string/osk_open_keyboard</item>
""", """        <item>@string/pref_gesture_action_middle_click</item>
"""),
       ("""        <item>middle-click</item>
        <item>open-osk</item>
""", """        <item>middle-click</item>
""")],
      "arrays.xml", must_remain=["tap3_action_values"])

# ---------------------------------------------------------------- styles.xml
patch(os.path.join(AVNC, "res", "values", "styles.xml"),
      [("""
    <!-- Local fork: small round buttons of the pointer ring -->
    <style name="OskRingButton" parent="ImageButton">
        <item name="android:layout_width">44dp</item>
        <item name="android:layout_height">44dp</item>
        <item name="android:layout_margin">1dp</item>
        <item name="android:padding">9dp</item>
        <item name="android:background">@drawable/bg_circular_button</item>
        <item name="tint">#FFFFFFFF</item>
    </style>
""", "")],
      "styles.xml", must_remain=['<style name="ImageButton">'])

# ---------------------------------------------------------------- strings
OSK_NAMES = [
    "pref_osk_heading", "pref_osk_pointer_button", "msg_osk_pointer_button_help",
    "pref_osk_button_ring", "msg_osk_button_ring_help",
    "pref_osk_three_finger_tap", "msg_osk_three_finger_tap_help",
    "osk_nudge_up_left", "osk_nudge_up", "osk_nudge_up_right", "osk_nudge_left",
    "osk_nudge_right", "osk_nudge_down_left", "osk_nudge_down", "osk_nudge_down_right",
    "osk_request_sent", "osk_open_keyboard", "osk_close_keyboard",
]
for rel in (os.path.join("values", "strings.xml"), os.path.join("values-zh-rCN", "strings.xml")):
    p = os.path.join(AVNC, "res", rel)
    raw = read(p)
    crlf = "\r\n" in raw
    src = raw.replace("\r\n", "\n")
    n = 0
    for name in OSK_NAMES:
        pat = re.compile(r'[ \t]*<string name="%s">.*?</string>\n' % re.escape(name), re.S)
        src, c = pat.subn("", src)
        n += c
    for token in ("pref_zoom_mis_touch_guard", "msg_zoom_mis_touch_confirm", "pref_cursor_size"):
        if token not in src:
            raise SystemExit("%s: destroyed %s" % (rel, token))
    out = src.replace("\n", "\r\n") if crlf else src
    write(p, out)
    log.append("%s: removed %d osk strings" % (rel, n))

# ---------------------------------------------------------------- pref_input.xml
pref_xml = os.path.join(AVNC, "res", "xml", "pref_input.xml")
raw = read(pref_xml)
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
bstart = src.index("    <!-- Local fork: floating keyboard triggers -->")
bend = src.index("    </PreferenceCategory>\n", bstart) + len("    </PreferenceCategory>\n")
block = src[bstart:bend]
if "osk_pointer_button" not in block or "zoom_mis_touch_guard" not in block:
    raise SystemExit("pref_input: unexpected category content")
src = src[:bstart] + src[bend:]
keep = """
        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="true"
            app:helpMessage="@string/msg_zoom_mis_touch_guard_help"
            app:key="zoom_mis_touch_guard"
            app:title="@string/pref_zoom_mis_touch_guard"
            app:widgetLayout="@layout/help_btn" />
"""
anchor = """            app:title="@string/pref_scroll_speed"
            app:valuePrefix="@string/value_prefix_scroll" />
"""
if anchor not in src:
    raise SystemExit("pref_input: scroll_speed anchor missing")
src = src.replace(anchor, anchor + keep, 1)
src = re.sub(r"\n{3,}", "\n\n", src)
out = src.replace("\n", "\r\n") if crlf else src
write(pref_xml, out)
log.append("pref_input.xml: keyboard category removed, zoom guard re-homed")

# ---------------------------------------------------------------- OskBridge
bridge = os.path.join(AVNC, "java", "com", "gaurav", "avnc", "util", "OskBridge.kt")
if os.path.exists(bridge):
    os.remove(bridge)
    log.append("OskBridge.kt: DELETED")

# ---------------------------------------------------------------- host: ViewModel
vm = os.path.join(HOST, "ui", "page", "ContainerMainViewModel.kt")
raw = read(vm)
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
src = src.replace("import com.gaurav.avnc.util.OskBridge\n", "")
pat = re.compile(r"\n[ \t]*(?://[^\n]*\n[ \t]*)*OskBridge\.summon = \{(?:[^\n]*\n)*?[ \t]*\}\n")
src, c = pat.subn("\n", src)
src, c2 = re.subn(r"\n[ \t]*OskBridge\.summon = null\n", "\n", src)
if "OskBridge" in src:
    raise SystemExit("ContainerMainViewModel: OskBridge residue %s" % c)
src = re.sub(r"\n{3,}", "\n\n", src)
out = src.replace("\n", "\r\n") if crlf else src
write(vm, out)
log.append("ContainerMainViewModel.kt: summon hook removed (hook=%d, clear=%d)" % (c, c2))

# ---------------------------------------------------------------- host: Fragment
frag = os.path.join(HOST, "ui", "page", "ContainerMainFragment.kt")
raw = read(frag)
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
old = """                            // 把容器内的键盘触发文件路径交给 VNC 界面：点小键盘按钮时
                            // 由安卓侧直接写这个文件，容器里的悬浮键盘每秒轮询一次即可弹出。
                            // 走文件而不是按键，是因为容器 X keymap 不一定有 XF86 键位。
                            runCatching {
                                // 容器里的 /tmp 通过 proot 绑到了 filesDir/tmp
                                // （和上面 VNC 的 UnixSocket 用的是同一个目录）。
                                val tmpDir = java.io.File(requireContext().filesDir, "tmp")
                                tmpDir.mkdirs()
                                val trigger = java.io.File(tmpDir, ".tiny_osk_toggle")
                                intent.putExtra("tc4.osk_trigger", trigger.absolutePath)
                                // 容器里的光标位置由 tiny_osk_caret.py 写进同一个 /tmp，
                                // 安卓侧读它来决定“键盘按钮”贴在文本光标旁边。
                                val caret = java.io.File(tmpDir, ".tiny_osk_caret")
                                intent.putExtra("tc4.osk_caret", caret.absolutePath)
                            }
"""
if old not in src:
    raise SystemExit("ContainerMainFragment: osk block not found verbatim")
src = src.replace(old, "")
out = src.replace("\n", "\r\n") if crlf else src
write(frag, out)
log.append("ContainerMainFragment.kt: osk intent extras removed")
if "osk" in out.lower():
    raise SystemExit("ContainerMainFragment still mentions osk")

for line in log:
    print(line)
