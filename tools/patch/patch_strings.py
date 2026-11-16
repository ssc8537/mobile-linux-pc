import io, os

RES = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'
V = os.path.join(RES, 'values')
ZH = os.path.join(RES, 'values-zh-rCN')

def rd(p):
    return io.open(p, 'r', encoding='utf-8', newline='').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', p)

EN = '''    <!-- Local fork: pointer tuning -->
    <string name="pref_mouse_acceleration">Mouse acceleration</string>
    <string name="pref_mouse_acceleration_summary">Move the pointer faster as you swipe faster</string>
    <string name="msg_mouse_acceleration_help">When enabled, a fast swipe moves the pointer further than a slow swipe of the same length. This lets you cross the whole screen with a short flick, while still allowing precise control at low speed.\\n\\nTurn it off for a 1:1 relationship between finger travel and pointer travel.</string>
    <string name="pref_mouse_acceleration_strength">Acceleration strength</string>
    <string name="msg_mouse_acceleration_strength_help">How much the pointer is boosted at high speed. 6 is the original upstream behaviour. Higher values make quick flicks travel further.</string>
    <string name="pref_slow_pointer_speed">Slow movement speed</string>
    <string name="msg_slow_pointer_speed_help">Percentage of finger travel applied to the pointer while moving slowly. Lower it to gain finer control when doing precise work, raise it if the pointer feels sluggish.</string>
    <string name="pref_scroll_speed">Scroll speed</string>
    <string name="msg_scroll_speed_help">How much finger travel is needed for one wheel click. Lower values scroll further per swipe.</string>
    <string name="pref_cursor_heading">Cursor</string>
    <string name="pref_cursor_size">Cursor size</string>
    <string name="msg_cursor_size_help">Scales the rendered remote cursor. 1.0x is the original size; the default is 1.5x for easier visibility on phones.</string>
    <string name="pref_cursor_tint">Cursor colour</string>
    <string name="msg_cursor_tint_help">Tints the white parts of the remote cursor. The original cursor colours are preserved when a tint is applied on top.</string>
    <string name="pref_zoom_mis_touch_guard">Confirm before zooming</string>
    <string name="msg_zoom_mis_touch_guard_help">A single pinch shows a hint instead of zooming. Perform the pinch again within a short time to actually zoom. This prevents accidental zoom-in while tapping or scrolling.</string>
    <string name="msg_zoom_mis_touch_confirm">Pinch again to zoom</string>
    <string name="pref_osk_heading">Floating keyboard</string>
    <string name="pref_osk_button_ring">Cursor corner buttons</string>
    <string name="msg_osk_button_ring_help">Shows a ring of small buttons around the pointer. Tap the keyboard button to open the floating keyboard on the remote desktop.</string>
    <string name="pref_osk_three_finger_tap">Three finger tap</string>
    <string name="msg_osk_three_finger_tap_help">Tap with three fingers anywhere to open (or close) the floating keyboard on the remote desktop.</string>
    <string name="osk_open_keyboard">Open floating keyboard</string>
    <string name="osk_close_keyboard">Close floating keyboard</string>
'''

ZH_TXT = '''    <!-- 本地分支：指针调节 -->
    <string name="pref_mouse_acceleration">鼠标加速</string>
    <string name="pref_mouse_acceleration_summary">手指滑得越快，指针移动得越远</string>
    <string name="msg_mouse_acceleration_help">开启后，同样的滑动距离，快速滑动会比慢速滑动移动得更远。这样轻轻一划就能穿过整个屏幕，同时慢速移动时仍可精确控制。\\n\\n关闭后，手指移动距离与指针移动距离保持 1:1。</string>
    <string name="pref_mouse_acceleration_strength">加速强度</string>
    <string name="msg_mouse_acceleration_strength_help">高速移动时指针的加成倍数。6 是原作者的默认手感，数值越大，快速滑动时指针跑得越远。</string>
    <string name="pref_slow_pointer_speed">慢速移动速度</string>
    <string name="msg_slow_pointer_speed_help">慢速移动时指针占手指移动距离的百分比。调小可以在做精细操作时更稳，调大可以让指针不那么拖沓。</string>
    <string name="pref_scroll_speed">滚轮速度</string>
    <string name="msg_scroll_speed_help">滑动多远触发一次滚轮。数值越小，一次滑动滚得越远。</string>
    <string name="pref_cursor_heading">鼠标指针</string>
    <string name="pref_cursor_size">指针大小</string>
    <string name="msg_cursor_size_help">缩放远端绘制的鼠标指针。1.0 倍为原始大小，默认 1.5 倍，在手机上更容易看清。</string>
    <string name="pref_cursor_tint">指针颜色</string>
    <string name="msg_cursor_tint_help">给指针的白色部分着色，原本就是彩色的部分会保留。</string>
    <string name="pref_zoom_mis_touch_guard">缩放前确认</string>
    <string name="msg_zoom_mis_touch_guard_help">第一次双指缩放只显示提示、不真正缩放。短时间内再缩放一次才会生效，避免点击或滑动时误触放大。</string>
    <string name="msg_zoom_mis_touch_confirm">再次缩放以确认</string>
    <string name="pref_osk_heading">悬浮键盘</string>
    <string name="pref_osk_button_ring">指针角落按钮</string>
    <string name="msg_osk_button_ring_help">在指针周围显示一圈小按钮，点击键盘按钮即可在远端桌面打开悬浮键盘。</string>
    <string name="pref_osk_three_finger_tap">三指轻点</string>
    <string name="msg_osk_three_finger_tap_help">在任意位置三指轻点，即可打开（或关闭）远端桌面上的悬浮键盘。</string>
    <string name="osk_open_keyboard">打开悬浮键盘</string>
    <string name="osk_close_keyboard">关闭悬浮键盘</string>
'''

p = os.path.join(V, 'strings.xml')
s = rd(p)
anchor = '    <string name="desc_help_btn">Help</string>\r\n'
assert anchor in s, 'en anchor missing'
if 'pref_mouse_acceleration' not in s:
    s = s.replace(anchor, anchor + EN.replace('\n', '\r\n'))
    wr(p, s)
else:
    print('en strings already present')

p = os.path.join(ZH, 'strings.xml')
s = rd(p)
anchor = '    <string name="desc_help_btn">帮助</string>\r\n'
assert anchor in s, 'zh anchor missing'
if 'pref_mouse_acceleration' not in s:
    s = s.replace(anchor, anchor + ZH_TXT.replace('\n', '\r\n'))
    wr(p, s)
else:
    print('zh strings already present')
print('DONE')
