import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py"
src = io.open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n")
a = "    src = src.replace(\n        anchor_default,\n        anchor_default + '      <property name=\"XF86Launch0\" type=\"empty\"/>\\n', 1)\n"
print("A present:", a in src)
b = "        + '      <!-- Local fork: XF86Launch0 opens/closes the pink floating keyboard -->\\n'\n        + '      <property name=\"XF86Launch0\" type=\"string\" value=\"tiny-osk-toggle\"/>\\n'\n"
print("B present:", b in src)
i = src.index("XF86Launch0")
print(repr(src[i-220:i+120]))
