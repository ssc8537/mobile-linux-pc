import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\page\ContainerMainViewModel.kt"
s = io.open(p, encoding="utf-8", newline="").read()
old = 'OskBridge.summon = {\n            Global.sendCommand("tiny-osk-toggle")\n        }'
new = 'OskBridge.summon = {\n            Global.sendCommand("/usr/local/bin/tiny-osk-toggle")\n        }'
assert old in s, "bridge body not found"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("OskBridge uses absolute path")
