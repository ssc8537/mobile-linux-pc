import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

old = """        <SwitchPreference
            android:defaultValue="true"
            app:helpMessage="@string/msg_zoom_mis_touch_guard_help"
            app:key="zoom_mis_touch_guard"
            app:title="@string/pref_zoom_mis_touch_guard" />"""
new = """        <com.gaurav.avnc.ui.prefs.SwitchPreferenceEx
            android:defaultValue="true"
            app:helpMessage="@string/msg_zoom_mis_touch_guard_help"
            app:key="zoom_mis_touch_guard"
            app:title="@string/pref_zoom_mis_touch_guard"
            app:widgetLayout="@layout/help_btn" />"""
assert old in t
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("zoom row now has help button; plain SwitchPreference left:", t.count("<SwitchPreference\n"))

# bump to tc4v8
for f in (r"avnc-upstream-fork-deletable\app\build.gradle",
          r"build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\gradle\libs.versions.toml"):
    q = R + "\\" + f
    b = open(q, "rb").read()
    x = b.decode("utf-8-sig")
    assert x.count("3.2.2-tc4v7") == 1, (f, x.count("3.2.2-tc4v7"))
    x = x.replace("3.2.2-tc4v7", "3.2.2-tc4v8")
    out = x.encode("utf-8")
    if b.startswith(b"\xef\xbb\xbf"):
        out = b"\xef\xbb\xbf" + out
    open(q, "wb").write(out)
    print("bumped", f.split("\\")[-1])
