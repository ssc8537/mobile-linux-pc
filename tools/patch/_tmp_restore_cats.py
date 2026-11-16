import io, os

P = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml"

with open(P, 'rb') as f:
    raw = f.read()
eol = '\r\n' if b'\r\n' in raw else '\n'
src = raw.decode('utf-8').replace('\r\n', '\n')

if 'app:key="mouse_passthrough"' in src:
    print('already restored, nothing to do')
    raise SystemExit(0)

anchor = '    <!-- Local fork: floating keyboard triggers -->'
assert anchor in src, 'anchor missing'

restored = '''    <PreferenceCategory
        app:icon="@drawable/ic_mouse"
        app:title="@string/pref_mouse">

        <SwitchPreference
            app:defaultValue="true"
            app:key="mouse_passthrough"
            app:summaryOff="@string/pref_mouse_passthrough_summary_off"
            app:summaryOn="@string/pref_mouse_passthrough_summary_on"
            app:title="@string/pref_mouse_passthrough" />

        <SwitchPreference
            app:defaultValue="true"
            app:dependency="mouse_passthrough"
            app:key="capture_pointer"
            app:title="@string/pref_capture_pointer" />

        <SwitchPreference
            app:defaultValue="true"
            app:key="hide_local_cursor"
            app:title="@string/pref_hide_local_cursor" />

        <SwitchPreference
            app:defaultValue="false"
            app:key="hide_remote_cursor"
            app:title="@string/title_hide_remote_cursor" />

        <ListPreference
            app:defaultValue="right-click"
            app:entries="@array/mouse_back_action_entries"
            app:entryValues="@array/mouse_back_action_values"
            app:key="mouse_back"
            app:title="@string/pref_mouse_back"
            app:useSimpleSummaryProvider="true" />
    </PreferenceCategory>

    <PreferenceCategory
        app:icon="@drawable/ic_keyboard_mini"
        app:title="@string/pref_vk">

        <SwitchPreference
            app:defaultValue="false"
            app:key="vk_open_with_keyboard"
            app:title="@string/pref_vk_open_with_keyboard" />

        <SwitchPreference
            app:defaultValue="false"
            app:key="vk_use_super_with_single_tap"
            app:title="@string/pref_vk_use_super_with_single_tap" />

        <ListPreference
            android:entries="@array/vk_row_count_values"
            android:entryValues="@array/vk_row_count_values"
            app:defaultValue="2"
            app:key="vk_row_count"
            app:title="@string/pref_vk_row_count"
            app:useSimpleSummaryProvider="true" />

        <Preference
            app:fragment="com.gaurav.avnc.ui.prefs.VirtualKeysEditor"
            app:title="@string/pref_customize_virtual_keys" />
    </PreferenceCategory>

    <PreferenceCategory
        app:icon="@drawable/ic_keyboard"
        app:title="@string/pref_km">

        <SwitchPreference
            app:defaultValue="false"
            app:key="km_right_alt_to_super"
            app:title="@string/pref_km_right_alt_to_super" />

        <SwitchPreference
            app:defaultValue="false"
            app:key="km_language_switch_to_super"
            app:title="@string/pref_km_language_switch_to_super" />

        <SwitchPreference
            app:defaultValue="false"
            app:key="km_back_to_escape"
            app:summary="@string/pref_km_back_to_escape_summary"
            app:title="@string/pref_km_back_to_escape" />
    </PreferenceCategory>

'''

src = src.replace(anchor, restored + anchor, 1)

need = ['mouse_passthrough', 'capture_pointer', 'hide_local_cursor', 'hide_remote_cursor',
        'mouse_back', 'vk_open_with_keyboard', 'vk_use_super_with_single_tap', 'vk_row_count',
        'km_right_alt_to_super', 'km_language_switch_to_super', 'km_back_to_escape']
missing = [k for k in need if 'app:key="%s"' % k not in src]
assert not missing, 'missing keys: %s' % missing

out = src.replace('\n', eol)
with open(P, 'wb') as f:
    f.write(out.encode('utf-8'))
print('restored OK, eol=%r, keys=%d' % (eol, src.count('app:key=')))
