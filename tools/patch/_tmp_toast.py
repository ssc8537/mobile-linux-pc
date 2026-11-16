import io, os
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt"
with io.open(p, "r", encoding="utf-8", newline="") as f:
    s = f.read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")
old = """        if (viewModel.pref.ui.showToolbarAndBookmark) {
            Toast.makeText(this, R.string.osk_request_sent, Toast.LENGTH_SHORT).show()
        }"""
new = """        Toast.makeText(this, R.string.osk_request_sent, Toast.LENGTH_SHORT).show()"""
assert old in t, "toast block not found"
t = t.replace(old, new, 1)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("toast simplified")
