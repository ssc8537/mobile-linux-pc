import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

start = t.index("        <!-- Local fork: pointer tuning -->")
end = t.index("    </PreferenceCategory>", t.index('app:key="cursor_tint"'))
block = """        <!-- Local fork: pointer tuning -->

        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="true"
            app:helpMessage="@string/msg_mouse_acceleration_help"
            app:key="mouse_acceleration"
            app:title="@string/pref_mouse_acceleration"
            app:widgetLayout="@layout/help_btn" />

        <com.gaurav.avnc.ui.prefs.ValueLabelPreference
            android:max="8"
            app:defaultValue="6"
            app:dependency="mouse_acceleration"
            app:key="mouse_acceleration_strength"
            app:min="1"
            app:title="@string/pref_mouse_acceleration_strength"
            app:valuePrefix="@string/value_prefix_accel"
            app:valueSuffix="@string/value_suffix_multiplier" />

        <com.gaurav.avnc.ui.prefs.ValueLabelPreference
            android:max="100"
            app:defaultValue="30"
            app:key="slow_pointer_speed"
            app:min="10"
            app:title="@string/pref_slow_pointer_speed"
            app:valueSuffix="@string/value_suffix_percent" />

        <com.gaurav.avnc.ui.prefs.ValueLabelPreference
            android:max="9"
            app:defaultValue="3"
            app:key="scroll_speed"
            app:min="1"
            app:title="@string/pref_scroll_speed"
            app:valuePrefix="@string/value_prefix_scroll" />
    </PreferenceCategory>

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
"""
t = t[:start] + block + t[end:]

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("restored, eol=%r" % eol)
