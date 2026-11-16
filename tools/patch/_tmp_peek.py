import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk\tiny_osk.py"
s = io.open(p, encoding="utf-8", newline="").read()
t = s.replace("\r\n", "\n")
lines = t.split("\n")
for i in range(172, 208):
    print(i+1, repr(lines[i]))
