import io, re
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\tiny_dot_yaml.yaml"
s = io.open(p, encoding="utf-8", errors="replace").read()
i = s.find("boot_command")
print(s[i:i+1600])
