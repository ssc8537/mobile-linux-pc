import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml'
raw = io.open(p, encoding='utf-8', newline='').read()
s = raw.replace('\r\n', '\n')
def rep(old, new, tag):
    global s
    assert old in s, tag
    s = s.replace(old, new, 1)

rep("""        <SeekBarPreference
            android:max="8"
            app:defaultValue="6"
            app:dependency="mouse_acceleration"
            app:key="mouse_acceleration_strength"
            app:min="1"
            app:title="@string/pref_mouse_acceleration_strength" />""",
"""        <com.gaurav.avnc.ui.prefs.ValueLabelPreference
            android:max="8"
            app:defaultValue="6"
            app:dependency="mouse_acceleration"
            app:key="mouse_acceleration_strength"
            app:min="1"
            app:title="@string/pref_mouse_acceleration_strength"
            app:valuePrefix="@string/value_prefix_accel"
            app:valueSuffix="@string/value_suffix_multiplier" />""", 'strength')

rep("""        <SeekBarPreference
            android:max="100"
            app:defaultValue="30"
            app:key="slow_pointer_speed"
            app:min="10"
            app:title="@string/pref_slow_pointer_speed" />""",
"""        <com.gaurav.avnc.ui.prefs.ValueLabelPreference
            android:max="100"
            app:defaultValue="30"
            app:key="slow_pointer_speed"
            app:min="10"
            app:title="@string/pref_slow_pointer_speed"
            app:valueSuffix="@string/value_suffix_percent" />""", 'slow')

rep("""        <SeekBarPreference
            android:max="5"
            app:defaultValue="3"
            app:key="scroll_speed"
            app:min="1"
            app:title="@string/pref_scroll_speed" />""",
"""        <com.gaurav.avnc.ui.prefs.ValueLabelPreference
            android:max="9"
            app:defaultValue="3"
            app:key="scroll_speed"
            app:min="1"
            app:title="@string/pref_scroll_speed"
            app:valuePrefix="@string/value_prefix_scroll" />""", 'scroll')

rep("""        <com.gaurav.avnc.ui.prefs.ColorPreference""",
"""        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="false"
            app:helpMessage="@string/msg_cursor_tint_enabled_help"
            app:key="cursor_tint_enabled"
            app:title="@string/pref_cursor_tint_enabled"
            app:widgetLayout="@layout/help_btn" />

        <com.gaurav.avnc.ui.prefs.ColorPreference""", 'color')

rep("""            app:defaultValue="0"
            app:helpMessage="@string/msg_cursor_tint_help"
            app:key="cursor_tint\"""",
"""            app:defaultValue="0"
            app:dependency="cursor_tint_enabled"
            app:helpMessage="@string/msg_cursor_tint_help"
            app:key="cursor_tint\"""", 'color dep')

rep("""            app:helpMessage="@string/msg_osk_button_ring_help"
            app:key="osk_button_ring"
            app:title="@string/pref_osk_button_ring\"""",
"""            app:helpMessage="@string/msg_osk_pointer_button_help"
            app:key="osk_pointer_button"
            app:title="@string/pref_osk_pointer_button\"""", 'osk pref')

io.open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if '\r\n' in raw else s)
print('pref_input ok')
