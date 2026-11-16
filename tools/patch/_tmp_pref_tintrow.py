import io, re
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\avnc-upstream-fork-deletable\app\src\main\res\xml\pref_input.xml"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

# remove the standalone enable switch row (it now lives on the colour row itself)
m = re.search(r'\n[ \t]*<com\.gaurav\.avnc\.ui\.prefs\.SwitchPreferenceEx\n'
              r'(?:[^\n]*\n)*?[^\n]*app:key="cursor_tint_enabled"[^\n]*\n'
              r'(?:[^\n]*\n)*?[^\n]*/>[ \t]*\n', t)
assert m, "standalone cursor_tint_enabled row not found"
t = t[:m.start()] + "\n" + t[m.end():]

# drop the dependency attribute from the colour row
before = t.count('app:dependency="cursor_tint_enabled"')
t = t.replace('\n        app:dependency="cursor_tint_enabled"', '')
t = t.replace('app:dependency="cursor_tint_enabled"\n', '')
after = t.count('app:dependency="cursor_tint_enabled"')
print("dependency removed:", before, "->", after)

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("pref_input patched eol=%r" % eol)
