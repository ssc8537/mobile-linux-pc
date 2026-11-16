import io, os

RES = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'
p = os.path.join(RES, 'xml', 'pref_input.xml')
s = io.open(p, 'r', encoding='utf-8', newline='').read()

anchor = ('        <SwitchPreference\r\n'
          '            android:defaultValue="false"\r\n'
          '            app:key="invert_vertical_scrolling"\r\n'
          '            app:title="@string/pref_invert_vertical_scrolling" />\r\n')

assert anchor in s, 'anchor missing'

added = anchor + '''
        <!-- Local fork: pointer tuning -->
        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="true"
            app:helpMessage="@string/msg_mouse_acceleration_help"
            app:key="mouse_acceleration"
            app:summary="@string/pref_mouse_acceleration_summary"
            app:title="@string/pref_mouse_acceleration"
            app:widgetLayout="@layout/help_btn" />

        <SeekBarPreference
            android:max="8"
            app:defaultValue="6"
            app:dependency="mouse_acceleration"
            app:key="mouse_acceleration_strength"
            app:min="1"
            app:title="@string/pref_mouse_acceleration_strength" />

        <SeekBarPreference
            android:max="100"
            app:defaultValue="30"
            app:key="slow_pointer_speed"
            app:min="10"
            app:title="@string/pref_slow_pointer_speed" />

        <SeekBarPreference
            android:max="5"
            app:defaultValue="3"
            app:key="scroll_speed"
            app:min="1"
            app:title="@string/pref_scroll_speed" />
'''.replace('\n', '\r\n')

s = s.replace(anchor, added)

# New categories: Cursor + Floating keyboard, appended before </PreferenceScreen>
tail = '</PreferenceScreen>'
extra = '''
    <!-- Local fork: cursor appearance -->
    <PreferenceCategory
        app:icon="@drawable/ic_mouse"
        app:title="@string/pref_cursor_heading">

        <SeekBarPreference
            android:max="300"
            app:defaultValue="150"
            app:key="cursor_size"
            app:min="50"
            app:title="@string/pref_cursor_size" />

        <com.gaurav.avnc.ui.prefs.ColorPreference
            app:defaultValue="0"
            app:helpMessage="@string/msg_cursor_tint_help"
            app:key="cursor_tint"
            app:title="@string/pref_cursor_tint" />
    </PreferenceCategory>

    <!-- Local fork: floating keyboard triggers -->
    <PreferenceCategory
        app:icon="@drawable/ic_keyboard_mini"
        app:title="@string/pref_osk_heading">

        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="true"
            app:helpMessage="@string/msg_osk_button_ring_help"
            app:key="osk_button_ring"
            app:title="@string/pref_osk_button_ring"
            app:widgetLayout="@layout/help_btn" />

        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="true"
            app:helpMessage="@string/msg_osk_three_finger_tap_help"
            app:key="osk_three_finger_tap"
            app:title="@string/pref_osk_three_finger_tap"
            app:widgetLayout="@layout/help_btn" />

        <SwitchPreference
            android:defaultValue="true"
            app:helpMessage="@string/msg_zoom_mis_touch_guard_help"
            app:key="zoom_mis_touch_guard"
            app:title="@string/pref_zoom_mis_touch_guard" />
    </PreferenceCategory>
'''.replace('\n', '\r\n')

assert tail in s
s = s.replace(tail, extra + '\r\n' + tail)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched pref_input.xml')
