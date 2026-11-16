import io
F = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\spec-rootfs-map.md"
raw = io.open(F, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
orig = src

# 1) path table rows
src = src.replace(
"| `home/tiny/.config/autostart/` | 自启项（V2 新增 `tiny-osk.desktop`） |\n"
"| `/usr/local/bin/tiny-osk` | 悬浮键盘启动器 |\n"
"| `/usr/local/share/tiny-osk/tiny_osk.py` | 悬浮键盘本体 |\n",
"| `home/tiny/.config/autostart/` | 自启项（现有 `tiny-clipman.desktop`；自定义键盘的项在 V6 已移除） |\n")

# 2) shortcut line
src = src.replace(
"- V2 新增：`XF86Launch0` → `tiny-osk-toggle`（两处都要加）\n",
"- V3 曾加过 `XF86Launch0` → `tiny-osk-toggle`，**V6 已删除**（键盘整体移除）。\n"
"  现在自定义的只有：`<Super>v` → `xfce4-popup-clipman`、`<Super><Shift>v` → `xfce4-clipman-history`。\n")

# 3) replace the two keyboard sections with a short "已移除" note
start = src.find("## 悬浮键盘怎么工作（改它之前必读）")
end = src.find("## 镜像升级机制（V4 新增，务必理解）")
if start < 0 or end < 0:
    raise SystemExit("section anchors missing")
replacement = """## 键盘：V6 已整体移除（别再往回加）

用户在 m03615 明确要求「键盘不写了，全部删掉」，所以从 V6 起：

- 镜像里**没有** `usr/local/share/tiny-osk/`（`tiny_osk.py` / `hk_layout.py` / `tiny_osk_caret.py`）
- 镜像里**没有** `usr/local/bin/{tiny-osk,tiny-osk-toggle,tiny-osk-caret}`
- 没有对应的 autostart 与 `.desktop`，快捷键里也没有 `XF86Launch0`
- APK 里**没有** OSK 按钮、没有 `OskBridge`、没有 `tc4.osk_*` intent extra、
  没有「悬浮键盘」设置分类，三指轻选项回到仅 3 个官方选项

历史实现与排查方法见 `spec-changes-v2.md` 的 D 节（标了「已被 V6 移除」），
仅作参考，不要照它恢复。若将来真的要重做，先问用户，别自作主张。

**唯一保留的兼容代码**：`applyImagePatch()` 开头有一小段 `$BIN_DIR/rm -rf/-f`，
作用是在打增量包之前清掉旧版残留的键盘文件（否则从 V5 升上来会留一个
指向已删除程序的自启项，每次登录都报错）。这段是必要的，不要删。

"""
src = src[:start] + replacement + src[end:]

# 4) the upgrade-mechanism section is stale (V4 dialog -> V5/V6 silent patch)
src = src.replace(
"- 每次成功导入/覆盖后都要把 stamp 记进 SharedPreferences，否则每次启动都弹。\n",
"- V5 起不再弹对话框：`autoPatchImageIfOutdated()` 直接静默调 `applyImagePatch()`。\n"
"  `askReimportImage()` 仍保留，作为手动重装的入口。\n"
"- 每次成功导入/覆盖后都要把 stamp 记进 SharedPreferences，否则每次启动都重跑。\n")
src = src.replace(
"   - 以后再说（只更新指纹，不再提示）\n",
"   - 以后再说（只更新指纹，不再提示）——V5 起这条路径自动执行，不必用户点\n")

if src == orig:
    raise SystemExit("nothing changed")
out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
print("ok", len(out.encode("utf-8")))
