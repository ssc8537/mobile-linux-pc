import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md'
s = io.open(p, encoding='utf-8', newline='').read()
lines = s.split('\n')
for i, ln in enumerate(lines):
    if 'XTEST' in ln or 'F9' in ln:
        print(i, repr(ln))
