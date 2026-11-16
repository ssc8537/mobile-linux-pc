import io, re

P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

# 1) drop the binding import (line may end with CRLF or LF)
before = s
s = re.sub(r'import com\.gaurav\.avnc\.databinding\.ViewZoomHintBinding\r?\n', '', s)
print('import removed:', before != s)

# 2) replace the hintBinding block using a regex that tolerates either EOL
pat = re.compile(
    r'( *)val hintBinding = ViewZoomHintBinding\.inflate\(layoutInflater, binding\.frameContainer, false\)\r?\n'
    r' *binding\.frameContainer\.addView\(hintBinding\.root\)\r?\n'
    r' *zoomHintView = hintBinding\.root\r?\n'
    r'(?:\r?\n)*'
    r' *hintBinding\.root\.alpha = 0f\r?\n'
    r' *hintBinding\.root\.animate\(\)\.alpha\(1f\)\.setDuration\(150\)\.withEndAction \{\r?\n'
    r' *hintBinding\.root\.animate\(\)\.alpha\(0f\)\.setStartDelay\(1400\)\.setDuration\(400\)\r?\n'
    r' *\.withEndAction \{\r?\n'
    r' *binding\.frameContainer\.removeView\(hintBinding\.root\)\r?\n'
    r' *if \(zoomHintView === hintBinding\.root\)\r?\n'
    r' *zoomHintView = null\r?\n'
    r' *\}\r?\n'
    r' *\}'
)

def repl(m):
    ind = m.group(1)
    L = [
        'val hintView = layoutInflater.inflate(R.layout.view_zoom_hint, binding.frameContainer, false)',
        'binding.frameContainer.addView(hintView)',
        'zoomHintView = hintView',
        '',
        'hintView.alpha = 0f',
        'hintView.animate().alpha(1f).setDuration(150).withEndAction {',
        '    hintView.animate().alpha(0f).setStartDelay(1400).setDuration(400)',
        '            .withEndAction {',
        '                binding.frameContainer.removeView(hintView)',
        '                if (zoomHintView === hintView)',
        '                    zoomHintView = null',
        '            }',
        '}',
    ]
    # detect the EOL style used inside the matched text
    eol = '\r\n' if '\r\n' in m.group(0) else '\n'
    return eol.join(ind + x if x else '' for x in L)

s2, n = pat.subn(repl, s)
print('hint block replaced:', n)
assert n == 1, 'hint block not replaced'
io.open(P, 'w', encoding='utf-8', newline='').write(s2)
print('OK')
