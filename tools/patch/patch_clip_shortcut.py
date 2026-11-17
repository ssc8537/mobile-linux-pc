import io
import os

def _find_ws():
    env = os.environ.get('TC_ROOT')
    if env:
        return env
    _d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(_d, 'build-env-toolchain')) or os.path.isdir(
            os.path.join(_d, 'source', 'app')
        ):
            return _d
        _p = os.path.dirname(_d)
        if _p == _d:
            return os.path.dirname(os.path.abspath(__file__))
        _d = _p


WS = _find_ws()
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

p = os.path.join(WS, 'tools-probe-scripts-deletable', 'build_rootfs_v2.py')
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
