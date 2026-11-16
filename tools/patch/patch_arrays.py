import io, os

RES = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'
p = os.path.join(RES, 'values', 'arrays.xml')
s = io.open(p, 'r', encoding='utf-8', newline='').read()

old_e = ('    <string-array name="tap3_action_entries">\r\n'
         '        <item>@string/pref_gesture_action_none</item>\r\n'
         '        <item>@string/pref_gesture_action_right_click</item>\r\n'
         '        <item>@string/pref_gesture_action_middle_click</item>\r\n'
         '    </string-array>\r\n'
         '    <string-array name="tap3_action_values">\r\n'
         '        <item>none</item>\r\n'
         '        <item>right-click</item>\r\n'
         '        <item>middle-click</item>\r\n'
         '    </string-array>\r\n')
new_e = ('    <string-array name="tap3_action_entries">\r\n'
         '        <item>@string/pref_gesture_action_none</item>\r\n'
         '        <item>@string/pref_gesture_action_right_click</item>\r\n'
         '        <item>@string/pref_gesture_action_middle_click</item>\r\n'
         '        <item>@string/osk_open_keyboard</item>\r\n'
         '    </string-array>\r\n'
         '    <string-array name="tap3_action_values">\r\n'
         '        <item>none</item>\r\n'
         '        <item>right-click</item>\r\n'
         '        <item>middle-click</item>\r\n'
         '        <item>open-osk</item>\r\n'
         '    </string-array>\r\n')

assert old_e in s, 'tap3 arrays not found'
s = s.replace(old_e, new_e)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched arrays.xml')
