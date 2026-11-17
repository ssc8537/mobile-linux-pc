import io, re, os

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

ROOT = os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main')

def stat(p):
    b = open(p,'rb').read()
    return b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')

for rel in [r'\java\com\gaurav\avnc\util\AppPreferences.kt',
            r'\java\com\gaurav\avnc\ui\vnc\input\PointerModes.kt',
            r'\java\com\gaurav\avnc\ui\vnc\gl\Renderer.kt',
            r'\java\com\gaurav\avnc\ui\vnc\VncActivity.kt',
            r'\java\com\gaurav\avnc\ui\vnc\input\Dispatcher.kt']:
    print(rel, stat(ROOT+rel))
