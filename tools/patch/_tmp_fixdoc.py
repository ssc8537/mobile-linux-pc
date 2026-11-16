import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\docs-project-notes-keep-forever\build-make-apk.md"
s = io.open(p, encoding="utf-8", newline="").read()
bad = "`v4-d222bfa6580997c3` 或 5 带 BOM。用下面这行写，避免 PowerShell 加 BOM："
good = "`v4-d222bfa6580997c3`。用下面这行写，避免 PowerShell 5.1 的 `Set-Content -Encoding UTF8` 加 BOM："
assert bad in s
s = s.replace(bad, good, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("fixed")
