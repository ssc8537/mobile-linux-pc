import io
for p in [r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\spec-changes-v2.md']:
    s = io.open(p, encoding='utf-8', newline='').read()
    old = "- `opt/tiny/export.sh` —— 删掉 `apt clean` 与两条 `rm -rvf`（保留 `cd /` 与 tar）"
    new = ("- `opt/tiny/export.sh` —— 删掉 `apt clean` 与两条 `rm -rvf`（保留 `cd /` 与 tar）\n"
           "- 剪贴板历史快捷键：`<Super>v` → `xfce4-popup-clipman`，\n"
           "  `<Super><Shift>v` → `xfce4-clipman-history`（在同一个 shortcuts xml 里）")
    assert old in s
    s = s.replace(old, new, 1)
    old2 = "  `usr/local/share/tiny-osk/tiny_osk.py`、autostart 项、`docklike-2.rc`"
    new2 = ("  `usr/local/share/tiny-osk/tiny_osk.py`、autostart 项（含\n"
            "  `tiny-clipman.desktop`）、`docklike-2.rc`")
    assert old2 in s
    s = s.replace(old2, new2, 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('ok')
