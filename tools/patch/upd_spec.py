import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\spec-changes-v2.md'
s = io.open(p, encoding='utf-8', newline='').read()
old = "我们改了 18 个文件、新增 5 个。**行号一律以 V2 交付时的状态为准。**"
new = "我们改了 18 个文件、新增 5 个。**行号一律以 V3 交付时的状态为准。**\n\n（V3 相对 V2 只多改了一处：`Dispatcher.doOpenRemoteOsk()` 里加了三指开关判断。）"
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
