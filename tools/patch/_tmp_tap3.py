import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")
old = '''        <ListPreference
            app:defaultValue="none"
            app:entries="@array/tap3_action_entries"'''
new = '''        <ListPreference
            app:defaultValue="open-osk"
            app:entries="@array/tap3_action_entries"'''
assert old in t, "tap3 anchor not found"
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("tap3 default -> open-osk OK")
