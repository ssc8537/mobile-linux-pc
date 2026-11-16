import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk\tiny_osk.py"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

pairs = [
    ("    k('P', 'p'), k('[', 'bracketleft'), k(']', 'bracketright'),",
     "    k('P', 'p'), k('[{', 'bracketleft'), k(']}', 'bracketright'),"),
    ("    k('\\\\', 'backslash', 1.2),",
     "    k('\\\\|', 'backslash', 1.2),"),
    ("    k('L', 'l'), k(';', 'semicolon'), k(\"'\", 'apostrophe'),",
     "    k('L', 'l'), k(';:', 'semicolon'), k(\"'\\\"\", 'apostrophe'),"),
    ("    k('V', 'v'), k('B', 'b'), k('N', 'n'), k('M', 'm'), k(',', 'comma'),",
     "    k('V', 'v'), k('B', 'b'), k('N', 'n'), k('M', 'm'), k(',<', 'comma'),"),
    ("    k('.', 'period'), k('/', 'slash'), k('Shift', 'Shift_L', 1.8, 'mod'),",
     "    k('.>', 'period'), k('/?', 'slash'), k('Shift', 'Shift_L', 1.8, 'mod'),"),
    ("    k('0', 'KP_0', 1.4), k('Ins', 'KP_Insert'), k('Del', 'KP_Delete'),",
     "    k('0/Ins', 'KP_0', 1.4), k('.', 'KP_Decimal'), k('Del', 'KP_Delete'),"),
    ("    k('`~', 'grave'), k('1!', '1'), k('2@', '2'), k('3#', '3'), k('4$', '4'),",
     "    k('`~', 'grave'), k('1!', '1'), k('2@', '2'), k('3#', '3'), k('4$', '4'),"),
]
for old, new in pairs:
    if old not in t:
        print("MISS:", repr(old))
        continue
    t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("done")
