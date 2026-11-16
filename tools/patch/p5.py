import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res\values\attrs.xml'
raw = io.open(p, encoding='utf-8', newline='').read()
crlf = raw.count('\r\n')
s = raw.replace('\r\n', '\n')
old = """        <attr name="helpMessage" format="string|reference" />
    </declare-styleable>"""
assert old in s
new = """        <attr name="helpMessage" format="string|reference" />
    </declare-styleable>

    <!-- Local fork: seekbar preference that shows a human readable label -->
    <declare-styleable name="ValueLabelPreference">
        <attr name="valuePrefix" format="string" />
        <attr name="valueSuffix" format="string" />
    </declare-styleable>"""
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('attrs ok, crlf=', crlf)
