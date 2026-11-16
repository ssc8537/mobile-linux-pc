import io
F = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\log-version-history.md"
raw = io.open(F, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")

# 1) archive list
src = src.replace(
 "- `v4-image-patch-oskbutton-20261116/` —— V4（修复镜像未导入 + 指针按钮，**最新**)\n",
 "- `v4-image-patch-oskbutton-20261116/` —— V4（修复镜像未导入 + 指针按钮）\n"
 "- `v5-caret-osk-hk-20261116/` —— V5（光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃）\n"
 "- `v6-final-no-keyboard-20261116/` —— V6（**最终版：移除全部键盘功能**）\n")
src = src.replace(
 "- `v4-image-patch-oskbutton-20261116/` —— V4（修复镜像未导入 + 指针按钮，**最新**）\n",
 "- `v4-image-patch-oskbutton-20261116/` —— V4（修复镜像未导入 + 指针按钮）\n"
 "- `v5-caret-osk-hk-20261116/` —— V5（光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃）\n"
 "- `v6-final-no-keyboard-20261116/` —— V6（**最终版：移除全部键盘功能**）\n")

src = src.replace("## V5 —— 光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃（最新）",
                  "## V5 —— 光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃")

entry = """## V6 —— 最终版：把键盘相关代码全部移除（最新，用户指定定稿）

- 归档：`build-env-toolchain\\apks-archive-keep-forever\\v6-final-no-keyboard-20261116\\apk-v6-tc423-xfce-zh-final.apk`
- 761,832,607 字节，SHA-256 `81DB5DAC13B16B432E2F68077A193B583E6F647D0B0E93923784DD6ED00A4D47`
- 用户指令（m03615）：键盘不让写了，涉及键盘的代码全部移除，恢复到「V2 除了键盘」的状态，
  其他功能全部保留，作为定稿。
- 删掉的东西（AVNC `3.2.2-tc4v9` → `3.2.2-tc4v10`）：
  - `VncActivity` 整个 OSK 区块（按钮/跟随/光标读取/召唤/字段），约 200 行
  - `oskTriggerPath` / `oskCaretPath` 与两个 intent extra
  - `OskBridge` 文件本身 + `ContainerMainViewModel` 里的注册/注销
  - `Dispatcher` 的 `open-osk` 分支、`doOpenRemoteOsk()`、`nudgePointer()`
  - `InputHandler.nudgePointer()` / `sendKeySym()`
  - `AppPreferences.oskPointerButton` / `oskThreeFingerTap`，`tap3` 默认值回到 `"none"`
  - `pref_input.xml` 整个「悬浮键盘」分类、`arrays.xml` 第 4 个三指选项、
    `styles.xml` 的 `OskRingButton`、两种语言各 18 条 `osk_*` 文案
- 镜像侧删除 9 个文件：`usr/local/share/tiny-osk/*`（3 个 py）、`usr/local/bin/tiny-osk*`（3 个）、
  两个 autostart、一个 desktop 项；`xfce4-keyboard-shortcuts.xml` 去掉 `XF86Launch0`。
- 保留：鼠标加速/慢速/滚轮/指针大小/指针颜色/缩放前确认/`pref_mouse`/`pref_vk`/`pref_km`/开发者选项按钮。
- `zoom_mis_touch_guard` 从被删的分类搬到「指针」分类末尾，功能不变。
- 新增防御：`applyImagePatch()` 解压前先 `rm -rf` 旧键盘路径，从 V5 升上来不会留残留自启项。
- 新镜像 `rootfs-v7.tar` 2,683,729,920 字节 → `rootfs-v7.tar.zst` 732,826,915 字节
  （sha `2c671cf642cd8313`）；增量包 546,965 字节（sha `caeb4e317afec5d7`，262 个成员）；
  版本戳 `v6-2c671cf642cd8313`。

"""
anchor = "## 回退方法\n"
if anchor not in src:
    raise SystemExit("anchor missing")
src = src.replace(anchor, entry + anchor, 1)
out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
print("ok", len(out.encode("utf-8")))
