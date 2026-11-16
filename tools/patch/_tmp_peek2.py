import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk\tiny_osk.py"
s = io.open(p, encoding="utf-8", newline="").read()
lines = s.replace("\r\n","\n").split("\n")
for i in range(176, 205):
    print(i+1, lines[i])
print("---- total", len(lines))
