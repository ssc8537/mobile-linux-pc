import io
F = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\spec-changes-v2.md"
raw = io.open(F, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")

src = src.replace("## D. V5 新增/改动（在 A/B/C 之外，务必一起看）",
                  "## D. V5 新增/改动（**已被 V6 移除，仅作历史参考**）")
src = src.replace("### AVNC 侧（`3.2.2-tc4v9`）",
                  "### AVNC 侧（`3.2.2-tc4v9`，已废弃）")
src = src.replace("### 重做黑客键盘移植的完整命令链",
                  "### 重做黑客键盘移植的完整命令链（V6 起不再使用）")
src = src.replace("    | `ui/page/ContainerMainFragment.kt` | 除了 `tc4.osk_trigger`，再传 `tc4.osk_caret`（`filesDir/tmp/.tiny_osk_caret`） |",
                  "    | ~~`ui/page/ContainerMainFragment.kt`~~ | ~~再传 `tc4.osk_caret`~~ —— **V6 已删除** |")

entry = """## E. V6 改动（当前基线：键盘全部移除）

用户 m03615 指令：键盘不让写了，涉及键盘的代码全部移除，其他功能保留，作为定稿。
**V6 之后，与键盘相关的 A/B/C/D 各节内容都不再适用于当前构建。**

### App 侧（tiny_container）

| 文件 | 改动 |
|---|---|
| `ui/page/ContainerMainFragment.kt` | 删掉 `runCatching { ... intent.putExtra("tc4.osk_trigger" / "tc4.osk_caret") }` 整块；`createVncIntent` 之后直接 `addFlags` + `startActivity` |
| `ui/page/ContainerMainViewModel.kt` | 删掉 `import com.gaurav.avnc.util.OskBridge`、`setupEnvironment()` 里的 `OskBridge.summon = {...}`、`onCleared()` 里的 `OskBridge.summon = null` |
| `ui/page/ContainerManageViewModel.kt` | `applyImagePatch()` 的 shell 片段新增 3 条 `$BIN_DIR/rm -rf` / `rm -f`，在解压增量包之前清掉旧键盘残留（`usr/local/share/tiny-osk`、3 个 `usr/local/bin/tiny-osk*`、2 个 autostart、1 个 desktop、4 个 `/tmp/.tiny_osk*`） |

### AVNC 侧（`3.2.2-tc4v10`）

| 文件 | 改动 |
|---|---|
| `ui/vnc/VncActivity.kt` | 删除 OSK 区块（`oskButtonSizeDp`/`oskButtonGapDp`/`dp()`/`oskFollowTick`/`setupOskOverlay`/`applyOskPrefs`/`readCaretRect`/`positionOskButton`/`openRemoteKeyboard`）、字段 `oskButton`/`oskTriggerPath`/`oskCaretPath`/`oskCaretStamp`/`oskCaretRect`、`onCreate` 里的两个 extra 与 `setupOskOverlay()`、`onStart` 的 `applyOskPrefs()`、`onStop` 的 `removeCallbacks`；顺带删掉只被它用到的 `Gravity`/`ImageButton`/`FrameLayout`/`PointF`/`File`/`OskBridge` import |
| `ui/vnc/input/Dispatcher.kt` | 删除 `"open-osk"` 分支、`doOpenRemoteOsk()`、`nudgePointer()` |
| `ui/vnc/input/InputHandler.kt` | 删除 `nudgePointer()` 与 `sendKeySym()` |
| `util/AppPreferences.kt` | 删除 `oskPointerButton` / `oskThreeFingerTap`；`tap3` 默认值 `"open-osk"` → `"none"` |
| `util/OskBridge.kt` | **文件删除** |
| `res/xml/pref_input.xml` | 删除整个「悬浮键盘」分类；`zoom_mis_touch_guard` 搬到「指针」分类 `scroll_speed` 之后；`gesture_tap3` 的 `app:defaultValue` 改回 `none` |
| `res/values/arrays.xml` | `tap3_action_entries` / `tap3_action_values` 各删第 4 项 |
| `res/values/styles.xml` | 删除 `<style name="OskRingButton">` |
| `res/values/strings.xml`、`res/values-zh-rCN/strings.xml` | 各删 18 条 `osk_*` |

### 镜像侧

| 路径 | 改动 |
|---|---|
| `usr/local/share/tiny-osk/{tiny_osk.py,hk_layout.py,tiny_osk_caret.py}` | 不再写入 |
| `usr/local/bin/{tiny-osk,tiny-osk-toggle,tiny-osk-caret}` | 不再写入 |
| `home/tiny/.config/autostart/{tiny-osk.desktop,tiny-osk-caret.desktop}` | 不再写入 |
| `usr/share/applications/tiny-osk.desktop` | 不再写入 |
| `home/tiny/.config/xfce4/xfconf/.../xfce4-keyboard-shortcuts.xml` | 去掉 `XF86Launch0` 的 `default` + `custom` 两行，保留 `Super+V` / `Super+Shift+V` 剪贴板快捷键 |
| `build_rootfs_v2.py` | 常量 `OSK_SRC` / `HK_LAYOUT_SRC` / `CARET_SRC`、`OSK_LAUNCHER` / `CARET_LAUNCHER` / `OSK_TOGGLE` / `OSK_AUTOSTART` / `CARET_AUTOSTART` / `OSK_APP_ENTRY` 与 `build_extras()` 里 10 条 `reg(...)` 全部删除 |

### V6 重打包镜像的命令（当前版本就是这条链）

```powershell
$env:PYTHONPATH="$PWD\\tools-probe-scripts-deletable\\pyz2"
python tools-probe-scripts-deletable/build_rootfs_v2.py cache\\rootfs-plain.tar cache\\rootfs-v7.tar
python tools-probe-scripts-deletable/make_patch_tar.py cache\\rootfs-plain.tar cache\\rootfs-v7.tar cache\\rootfs-patch-v7.tar
python tools-probe-scripts-deletable/zst_tar.py cache\\rootfs-v7.tar cache\\rootfs-v7.tar.zst 19 4
python tools-probe-scripts-deletable/zst_tar.py cache\\rootfs-patch-v7.tar cache\\rootfs-patch-v7.tar.zst 19 4
# 版本戳（无 BOM！）
[System.IO.File]::WriteAllText("assets\\rootfs.stamp", "v6-2c671cf642cd8313", (New-Object System.Text.UTF8Encoding $false))
```

产出：`rootfs-v7.tar` 2,683,729,920 字节 → `.zst` 732,826,915（sha `2c671cf642cd8313`）；
增量包 546,965 字节（sha `caeb4e317afec5d7`，262 个成员 = 3 patched + 259 new）。

"""
anchor = "## 判断「哪些必须保留」的一句话规则\n"
if anchor not in src:
    raise SystemExit("anchor missing")
src = src.replace(anchor, entry + anchor, 1)
out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
print("ok", len(out.encode("utf-8")))
