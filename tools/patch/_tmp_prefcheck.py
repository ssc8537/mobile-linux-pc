import zipfile, re
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
data = z.read("res/xml/pref_input.xml")
txt = data.decode("utf-16-le", "ignore")
plain = re.sub(r"[^\x20-\x7e]", "", txt)
for needle in ["cursor_tint_enabled", "cursor_tint", "mouse_acceleration_strength",
               "zoom_mis_touch_guard", "osk_pointer_button", "slow_pointer_speed",
               "scroll_speed", "ValueLabelPreference", "SwitchPreferenceEx", "ColorPreference"]:
    print("%-28s %s" % (needle, needle in plain))
print("len(res/xml/pref_input.xml) =", len(data))
