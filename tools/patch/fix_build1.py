import io

BASE = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc'

# ---------------------------------------------------- ColorPreference: sharedPreferences
P = BASE + r'\ui\prefs\ColorPreference.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()
assert 'private fun currentColor(): Int = preferences.getInt(key, 0)' in s
s = s.replace('private fun currentColor(): Int = preferences.getInt(key, 0)',
              'private fun currentColor(): Int = sharedPreferences.getInt(key, 0)')
s = s.replace('preferences.edit().putInt(key, Color.rgb(r, g, b)).apply()',
              'sharedPreferences.edit().putInt(key, Color.rgb(r, g, b)).apply()')
s = s.replace('preferences.edit().putInt(key, 0).apply()',
              'sharedPreferences.edit().putInt(key, 0).apply()')
assert 'preferences' not in s.replace('sharedPreferences', '')
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched ColorPreference.kt')

# ---------------------------------------------------- VncActivity: no data binding for new views
P = BASE + r'\ui\vnc\VncActivity.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

s = s.replace('import com.gaurav.avnc.databinding.ViewZoomHintBinding\r\n', '')

old = ('        val hintBinding = ViewZoomHintBinding.inflate(layoutInflater, binding.frameContainer, false)\r\n'
       '        binding.frameContainer.addView(hintBinding.root)\r\n'
       '        zoomHintView = hintBinding.root\r\n'
       '\r\n'
       '        hintBinding.root.alpha = 0f\r\n'
       '        hintBinding.root.animate().alpha(1f).setDuration(150).withEndAction {\r\n'
       '            hintBinding.root.animate().alpha(0f).setStartDelay(1400).setDuration(400)\r\n'
       '                    .withEndAction {\r\n'
       '                        binding.frameContainer.removeView(hintBinding.root)\r\n'
       '                        if (zoomHintView === hintBinding.root)\r\n'
       '                            zoomHintView = null\r\n'
       '                    }\r\n'
       '        }\r\n')
new = ('        val hintView = layoutInflater.inflate(R.layout.view_zoom_hint, binding.frameContainer, false)\r\n'
       '        binding.frameContainer.addView(hintView)\r\n'
       '        zoomHintView = hintView\r\n'
       '\r\n'
       '        hintView.alpha = 0f\r\n'
       '        hintView.animate().alpha(1f).setDuration(150).withEndAction {\r\n'
       '            hintView.animate().alpha(0f).setStartDelay(1400).setDuration(400)\r\n'
       '                    .withEndAction {\r\n'
       '                        binding.frameContainer.removeView(hintView)\r\n'
       '                        if (zoomHintView === hintView)\r\n'
       '                            zoomHintView = null\r\n'
       '                    }\r\n'
       '        }\r\n')
assert old in s, 'zoom hint block not found'
s = s.replace(old, new, 1)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched VncActivity.kt')
