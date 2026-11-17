import io, os


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

RES = os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main', 'res')

def rd(p):
    return io.open(p, 'r', encoding='utf-8', newline='').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', p)

for rel, line in (('values/strings.xml', '    <string name="color_picker_reset">Use original colour</string>\r\n'),
                  ('values-zh-rCN/strings.xml', '    <string name="color_picker_reset">恢复原色</string>\r\n')):
    p = os.path.join(RES, rel.replace('/', os.sep))
    s = rd(p)
    if 'color_picker_reset' in s:
        print('already present in', rel)
        continue
    anchor = s.index('<string name="pref_cursor_tint">')
    s = s[:anchor] + line + s[anchor:]
    wr(p, s)
print('DONE')
