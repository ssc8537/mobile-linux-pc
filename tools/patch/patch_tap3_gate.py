import io
import re
import sys

p = sys.argv[1]
src = io.open(p, 'r', encoding='utf-8', newline='').read()

pat = re.compile(r'([ \t]*)private fun doOpenRemoteOsk\(\) = activity\.openRemoteKeyboard\(\)')
m = pat.search(src)
assert m, 'anchor missing'

indent = m.group(1)
eol = '\r\n' if '\r\n' in src else '\n'
block = eol.join([
    indent + 'private fun doOpenRemoteOsk() {',
    indent + '    // Local fork: the three-finger tap is optional, gated by its own switch.',
    indent + '    if (!viewModel.pref.input.oskThreeFingerTap)',
    indent + '        return',
    indent + '    activity.openRemoteKeyboard()',
    indent + '}',
])

src = src[:m.start()] + block + src[m.end():]
io.open(p, 'w', encoding='utf-8', newline='').write(src)
print('dispatch patched, eol=%r' % eol)
