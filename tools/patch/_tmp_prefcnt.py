import zipfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
s = z.read("res/bb.xml").decode("utf-8", "ignore")
for k in ("SwitchPreferenceEx", "ValueLabelPreference", "ColorPreference",
          "mouse_acceleration", "slow_pointer_speed", "scroll_speed"):
    print("%-24s %d" % (k, s.count(k)))
