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

ROOT = WS
T = ROOT + r'\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container'

def read(p):
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        return f.read()

def write(p, s):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)

# ------------------------------------------------ SettingsViewModel: add the dev-options action
P = T + r'\app\src\main\java\com\fct\tc4\ui\page\SettingsViewModel.kt'
s = read(P)
eol = '\r\n' if '\r\n' in s else '\n'

old = ("            ActionSetting(" + eol +
       "                id = \"battery_unlimited\"," + eol +
       "                titleRes = R.string.tc4_settings_battery_title," + eol +
       "                descriptionRes = R.string.tc4_settings_battery_desc" + eol +
       "            )")
new = old + "," + eol + \
      "            ActionSetting(" + eol + \
      "                id = \"dev_options_phantom\"," + eol + \
      "                titleRes = R.string.tc4_settings_dev_options_title," + eol + \
      "                descriptionRes = R.string.tc4_settings_dev_options_desc" + eol + \
      "            )"
assert old in s, 'battery action not found'
s = s.replace(old, new, 1)
write(P, s)
print('patched SettingsViewModel.kt')

# ------------------------------------------------ SettingsFragment: handle the new action
P = T + r'\app\src\main\java\com\fct\tc4\ui\page\SettingsFragment.kt'
s = read(P)
eol = '\r\n' if '\r\n' in s else '\n'

old = ("            \"battery_unlimited\" -> {" + eol +
       "                startActivity(" + eol +
       "                    Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {" + eol +
       "                        data = Uri.parse(\"package:${requireContext().packageName}\")" + eol +
       "                    }" + eol +
       "                )" + eol +
       "            }")
new = old + eol + \
      "            // Local fork: Android 12+ phantom process killer. The Linux session dies after" + eol + \
      "            // ~10 s unless '停止限制子进程' is enabled in Developer options. Jump straight there." + eol + \
      "            \"dev_options_phantom\" -> {" + eol + \
      "                try {" + eol + \
      "                    startActivity(Intent(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS))" + eol + \
      "                } catch (e: Exception) {" + eol + \
      "                    try {" + eol + \
      "                        startActivity(Intent(Settings.ACTION_SETTINGS))" + eol + \
      "                    } catch (e2: Exception) {" + eol + \
      "                        Snackbar.make(binding.root, R.string.tc4_settings_dev_options_failed, Snackbar.LENGTH_LONG).show()" + eol + \
      "                    }" + eol + \
      "                }" + eol + \
      "            }"
assert old in s, 'battery branch not found'
s = s.replace(old, new, 1)
write(P, s)
print('patched SettingsFragment.kt')

# ------------------------------------------------ strings (zh + default en)
for path, title, desc, failed in [
    (T + r'\app\src\main\res\values-zh-rCN\strings.xml',
     '停止限制子进程',
     '打开开发者选项页面，找到“停止限制子进程”并开启，否则 Linux 系统会在约 10 秒后被系统杀掉',
     '无法打开开发者选项页面，请手动到系统设置中开启'),
    (T + r'\app\src\main\res\values\strings.xml',
     'Disable child process limit',
     'Open Developer options and enable "Disable child process restrictions", otherwise the Linux session gets killed after about 10 seconds',
     'Cannot open Developer options, please open system settings manually'),
]:
    s = read(path)
    eol = '\r\n' if '\r\n' in s else '\n'
    anchor = '    <string name="tc4_settings_battery_desc">'
    i = s.find(anchor)
    assert i >= 0, 'battery desc not found in ' + path
    j = s.find('</string>', i) + len('</string>')
    # preserve whatever newline follows
    add = (eol + '    <string name="tc4_settings_dev_options_title">' + title + '</string>' +
           eol + '    <string name="tc4_settings_dev_options_desc">' + desc + '</string>' +
           eol + '    <string name="tc4_settings_dev_options_failed">' + failed + '</string>')
    s = s[:j] + add + s[j:]
    write(path, s)
    print('patched', path)
