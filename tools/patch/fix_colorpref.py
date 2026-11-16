import io

P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\prefs\ColorPreference.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()
eol = '\r\n' if '\r\n' in s else '\n'

s = s.replace('sharedPreferences.getInt(key, 0)',
              'prefs().getInt(key, 0)')
s = s.replace('sharedPreferences.edit().putInt(key, Color.rgb(r, g, b)).apply()',
              'prefs().edit().putInt(key, Color.rgb(r, g, b)).apply()')
s = s.replace('sharedPreferences.edit().putInt(key, 0).apply()',
              'prefs().edit().putInt(key, 0).apply()')
assert 'sharedPreferences' not in s

helper = ("    private fun prefs() = PreferenceManager.getDefaultSharedPreferences(context)" + eol + eol)
anchor = '    private fun currentColor(): Int'
assert anchor in s
s = s.replace(anchor, helper + anchor, 1)

# ensure the import exists
if 'import androidx.preference.PreferenceManager' not in s:
    s = s.replace('import androidx.preference.Preference' + eol,
                  'import androidx.preference.Preference' + eol +
                  'import androidx.preference.PreferenceManager' + eol, 1)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
