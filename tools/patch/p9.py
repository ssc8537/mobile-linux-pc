import io, re
BASE = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'
for rel in [r'\values\strings.xml', r'\values-zh-rCN\strings.xml']:
    p = BASE + rel
    raw = io.open(p, encoding='utf-8', newline='').read()
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    s2 = re.sub(r'<string name="value_suffix_percent">[^<]*</string>',
                '<string name="value_suffix_percent" formatted="false">%</string>', s)
    assert s2 != s, rel
    io.open(p, 'w', encoding='utf-8', newline='').write(s2.replace('\n', '\r\n') if crlf else s2)
    print('percent fixed', rel)
