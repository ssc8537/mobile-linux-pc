import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\build_rootfs_v2.py'
s = io.open(p, encoding='utf-8', newline='').read()
old = """        + '      <property name="XF86Launch0" type="string" value="tiny-osk-toggle"/>\\n', 1)
    return src.encode('utf-8')"""
new = """        + '      <property name="XF86Launch0" type="string" value="tiny-osk-toggle"/>\\n'
        + '      <!-- Local fork: Super+V pops the clipboard history, like Windows Win+V -->\\n'
        + '      <property name="&lt;Super&gt;v" type="string" value="xfce4-popup-clipman"/>\\n'
        + '      <!-- Local fork: Super+Shift+V pops the full clipboard manager window -->\\n'
        + '      <property name="&lt;Super&gt;&lt;Shift&gt;v" type="string" value="xfce4-clipman-history"/>\\n', 1)
    return src.encode('utf-8')"""
assert old in s, 'anchor missing'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('build_rootfs_v2.py patched')
