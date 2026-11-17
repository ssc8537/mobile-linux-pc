import io, sys, os

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

for p in [os.path.join(WS, 'build-env-toolchain', 'ws-gradle-build-copy-deletable', 'tiny_container', 'app', 'src', 'main', 'java', 'com', 'fct', 'tc4', 'ui', 'main', 'MainActivity.kt'),
          os.path.join(WS, 'build-env-toolchain', 'ws-gradle-build-copy-deletable', 'tiny_container', 'app', 'src', 'main', 'java', 'com', 'fct', 'tc4', 'ui', 'misc', 'Global.kt'),
          os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main', 'java', 'com', 'gaurav', 'avnc', 'ui', 'vnc', 'VncActivity.kt'),
          os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main', 'res', 'xml', 'pref_input.xml'),
          os.path.join(WS, 'avnc-upstream-fork-deletable', 'app', 'src', 'main', 'java', 'com', 'gaurav', 'avnc', 'ui', 'vnc', 'gl', 'Shaders.kt')]:
    b = open(p,'rb').read()
    print(os.path.basename(p), 'CRLF', b.count(b'\r\n'), 'LF-only', b.count(b'\n')-b.count(b'\r\n'))
