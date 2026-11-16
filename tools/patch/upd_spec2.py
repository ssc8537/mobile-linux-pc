import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\spec-changes-v2.md'
s = io.open(p, encoding='utf-8', newline='').read()
old = "- 新增：六个 deb 的全部文件、`usr/local/bin/tiny-osk`、`tiny-osk-toggle`、\n  `usr/local/share/tiny-osk/tiny_osk.py`、autostart 项、`docklike-2.rc`"
new = ("- 新增：六个 deb 的全部文件、`usr/local/bin/tiny-osk`、`tiny-osk-toggle`、\n"
       "  `usr/local/share/tiny-osk/tiny_osk.py`、autostart 项、`docklike-2.rc`\n"
       "- `tiny_osk.py` 源文件在 `tools-probe-scripts-deletable/osk/tiny_osk.py`，改完必须重新跑\n"
       "  `build_rootfs_v2.py` + `zst_tar.py` 才会进镜像。它的配置写在容器的\n"
       "  `~/.config/tiny-osk.conf`（键：`layout` / `placement` / `key_height` / `opacity`）。")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
