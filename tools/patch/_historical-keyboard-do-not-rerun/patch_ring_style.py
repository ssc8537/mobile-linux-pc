import io, os

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\res'

def rd(p):
    return io.open(p, 'r', encoding='utf-8', newline='').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', os.path.relpath(p, ROOT))

# ---------------------------------------------------------------- style
p = os.path.join(ROOT, 'values', 'styles.xml')
s = rd(p)
if 'OskRingButton' not in s:
    old = ('    <style name="ImageButton.Toggle">\r\n')
    new = ('    <!-- Local fork: small round buttons of the pointer ring -->\r\n'
           '    <style name="OskRingButton" parent="ImageButton">\r\n'
           '        <item name="android:layout_width">44dp</item>\r\n'
           '        <item name="android:layout_height">44dp</item>\r\n'
           '        <item name="android:layout_margin">1dp</item>\r\n'
           '        <item name="android:padding">9dp</item>\r\n'
           '        <item name="android:background">@drawable/bg_circular_button</item>\r\n'
           '        <item name="tint">#FFFFFFFF</item>\r\n'
           '    </style>\r\n\r\n'
           '    <style name="ImageButton.Toggle">\r\n')
    assert old in s
    s = s.replace(old, new, 1)
    wr(p, s)
else:
    print('style already present')

# ---------------------------------------------------------------- strings
RING = [
    ('osk_nudge_up_left',         'Nudge pointer up-left',    '指针左上移'),
    ('osk_nudge_up',              'Nudge pointer up',         '指针上移'),
    ('osk_nudge_up_right',        'Nudge pointer up-right',   '指针右上移'),
    ('osk_nudge_left',            'Nudge pointer left',       '指针左移'),
    ('osk_nudge_right',           'Nudge pointer right',      '指针右移'),
    ('osk_nudge_down_left',       'Nudge pointer down-left',  '指针左下移'),
    ('osk_nudge_down',            'Nudge pointer down',       '指针下移'),
    ('osk_nudge_down_right',      'Nudge pointer down-right', '指针右下移'),
]

for rel, idx in (('values/strings.xml', 1), ('values-zh-rCN/strings.xml', 2)):
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    s = rd(p)
    added = []
    for row in RING:
        key, en, zh = row[0], row[1], row[2]
        if key in s:
            continue
        text = (en if idx == 1 else zh)
        added.append('    <string name="%s">%s</string>\r\n' % (key, text))
    if not added:
        print('ring strings already present in', rel)
        continue
    anchor = s.index('<string name="osk_open_keyboard">')
    s = s[:anchor] + ''.join(added) + s[anchor:]
    wr(p, s)
print('DONE')
