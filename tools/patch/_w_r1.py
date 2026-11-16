import io
F = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md"
raw = io.open(F, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")

entry = """### v6-final-no-keyboard-20261116 —— 最终版：彻底移除键盘（用户指定定稿）

- 目录：`apks-archive-keep-forever\\v6-final-no-keyboard-20261116\\`
- 文件：`apk-v6-tc423-xfce-zh-final.apk`
- 大小：761,832,607 字节
- SHA-256：`81DB5DAC13B16B432E2F68077A193B583E6F647D0B0E93923784DD6ED00A4D47`
- 证书：`CN=TinyContainer ZoomPatch` / `cd4e54df0dfaab1f60729d2902664e81a90660aaebbf437fa6a5e6d9e766356b`
  （与 V1~V5 同一把，可直接覆盖安装）
- 内置镜像：`assets/rootfs.tar.zst` 732,826,915 字节
  sha256 `2c671cf642cd8313990d0e72a7cb7c5a2ad78e7c9c4fe3469736aa69fef79b92`；
  增量包 `assets/rootfs.patch.tar.zst` 546,965 字节
  sha256 `caeb4e317afec5d7bb88c96c6ac6b51dec7a802bc6b5840a9d1af06e8ad02dcc`（262 个成员）；
  版本戳 `assets/rootfs.stamp` = `v6-2c671cf642cd8313`
- AVNC 分支：`3.2.2-tc4v10`

**用户指令（m03615）**：键盘不让写了，把涉及键盘的代码全部移除，恢复到「V2 除了键盘以外」
的状态，其余功能全部保留，作为定稿版本。

**移除清单（AVNC 侧 `3.2.2-tc4v9` → `3.2.2-tc4v10`）**

| 移除对象 | 具体改动 |
|---|---|
| 悬浮键盘按钮 | 删掉 `VncActivity` 整个 OSK 区块（`setupOskOverlay` / `applyOskPrefs` / `positionOskButton` / `readCaretRect` / `openRemoteKeyboard` / `oskFollowTick` / `oskButton` 等 200 余行）+ `onCreate` 的 `setupOskOverlay()`、`onStart` 的 `applyOskPrefs()`、`onStop` 的 `removeCallbacks` |
| intent 通道 | 删掉 `oskTriggerPath` / `oskCaretPath` 两个字段与 `tc4.osk_trigger` / `tc4.osk_caret` 两个 extra 的读取 |
| `OskBridge` | 文件删除；`ContainerMainViewModel` 里的 `summon` 注册与 `onCleared()` 注销一并移除 |
| 三指轻点呼出 | `Dispatcher` 删除 `"open-osk"` 分支与 `doOpenRemoteOsk()`；`arrays.xml` 删掉第 4 项；`pref_input.xml` 的 `gesture_tap3` 默认值改回 `none`；`AppPreferences.tap3` 默认值改回 `"none"` |
| 指针微调 | `Dispatcher.nudgePointer` 与 `InputHandler.nudgePointer` / `sendKeySym` 删除（只被九宫格/兜底按键用过） |
| 设置项 | `pref_input.xml` 删掉整个「悬浮键盘」分类；`AppPreferences` 删掉 `oskPointerButton` / `oskThreeFingerTap`；`styles.xml` 删掉 `OskRingButton` |
| 文案 | 两种语言各删 18 条 `osk_*` 字符串 |

**保留（未受影响）**：鼠标加速开关/强度 1~8/慢速 10~100%、滚轮档位 1~9、
指针大小 50~300（默认 150%）、指针颜色 + 行内开关、缩放前确认、
设置页「停止限制子进程」、`pref_mouse`/`pref_vk`/`pref_km` 三个官方分类（V5 恢复的）。
`zoom_mis_touch_guard` 从被删的「悬浮键盘」分类里搬到「指针」分类末尾，功能不变。

**镜像侧移除**：`usr/local/share/tiny-osk/{tiny_osk.py,hk_layout.py,tiny_osk_caret.py}`、
`usr/local/bin/{tiny-osk,tiny-osk-toggle,tiny-osk-caret}`、
`~/.config/autostart/{tiny-osk.desktop,tiny-osk-caret.desktop}`、
`usr/share/applications/tiny-osk.desktop`、`xfce4-keyboard-shortcuts.xml` 里的
`XF86Launch0` 绑定。镜像文件数 115886 原始 + 259 新增（V5 是 268），
`rootfs-v7.tar` 2,683,729,920 字节。

**新增的一处防御**：`applyImagePatch()` 在解压增量包之前先 `rm -rf` 掉上面那批路径，
所以从 V5 升上来时旧键盘残留会被自动清掉，不会出现「自启项还在但程序没了」的报错。

- 已知现象：应用内「检查更新」仍提示有新版（versionName 保持 4.2.3），可忽略。

"""
anchor = "### 后续版本\n"
if anchor not in src:
    raise SystemExit("anchor missing")
src = src.replace(anchor, entry + anchor, 1)
out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
print("ok", len(out.encode("utf-8")))
