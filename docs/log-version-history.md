# 01 版本历史（交付过哪些 APK）

> 这篇只回答一件事：**我们交付过哪些版本、每版改了什么、怎么回退。**
> 详细到行号的技术说明见 `spec-changes-v2.md`。

## 归档位置

`build-env-toolchain/apks-archive-keep-forever/`
- `v1-baseline-zoomfree-20261115/` —— V1（用户已投产使用）
- `v2-features-20261116/` —— V2（功能增强版）
- `v3-osk-settings-20261116/` —— V3（悬浮键盘补设置入口）
- `v4-image-patch-oskbutton-20261116/` —— V4（修复镜像未导入 + 指针按钮）
- `v5-caret-osk-hk-20261116/` —— V5（光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃）
- `v6-final-no-keyboard-20261116/` —— V6（**最终版：移除全部键盘功能**）
- `_signing-keys-keep-forever/tc4-release.jks` —— **唯一签名密钥，永久保留**
- `readme-versions-zh.md` —— 每次交付都要在这里追加条目

签名参数（不要改，改了老版本就装不上去）：alias `tc4`，storepass / keypass 都是 `tc4zoom`，
证书 DN `CN=TinyContainer ZoomPatch`，SHA-256 `cd4e54df0dfaab1f60729d2902664e81a90660aaebbf437fa6a5e6d9e766356b`。

## V1 —— 基线版本（用户当前在用，功能正常）

- 文件 `apk-v1-tc423-xfce-zh-zoomfree.apk`，957,130,197 字节
- SHA-256 `05EE9EF4453EB63D955E82288E8B8237F51D61866EF31A9A4A70DEEACAAB51DA`
- 上游 v4.2.3 原样 + **一行改动**：进入图形界面时缩放默认不再锁定
  （`ContainerMainFragment.kt:150` `fZoomLocked = false`；也就是说 V1 唯一实现的功能就是
  **自由缩放**：进去就能双指缩放，退后台回来再进也还是自由的，只有用户自己点锁才锁）
- 内置镜像：原始官方 `xfce-zh-20260808-160507.tar.zst`（928,728,904 字节）

## V2 —— 功能增强版

- 文件 `apk-v2-tc423-xfce-zh-mouse-cursor-osk.apk`，761,267,121 字节
- SHA-256 `F964A464EABE6198BBDDF576F825AE4666E1CF3DD8BD9370D36A5C3C0CFEB135`
- 内置镜像：重新打包的 `rootfs-v2.tar.zst`（732,818,799 字节，
  sha256 `5E1B7C61AE0C59C2F429C4BA4F3595B10625FC892C2CD3D32F948DF7F4DEF5F2`）
- APK 侧（AVNC 分支 `3.2.2-tc4v2`）：鼠标加速开关 + 强度 1~8、慢速速度 10~100、
  滚轮速度 1~5、指针大小 50~300（默认 150）、指针颜色取色器（粉色优先、可恢复）、
  缩放误触确认（1.2 秒内二次缩放才生效）、指针旁九宫格键盘按钮、三指轻点呼出键盘、
  设置页「停止限制子进程」跳转按钮
- 镜像侧：docklike 任务栏（默认固定 Firefox / 文件管理器 / 文本编辑器）、
  新增 taskmanager / screenshooter / clipman / libqrencode4、
  粉色悬浮键盘 `/usr/local/bin/tiny-osk`（可拖动 / 可停靠 / 双布局 / 设置入口 / 自启）、
  修复 `/opt/tiny/export.sh` 不再删 `~/.mozilla` 等个人数据

## V3 —— 悬浮键盘补上「设置」入口（推荐装这个）

- 文件 `apk-v3-tc423-xfce-zh-osk-settings.apk`，761,288,905 字节
- SHA-256 `3EEE8A5CCD85C635BF636152D87D1F64F1DED0F607A45602867A4ABD74455AD4`
- 内置镜像：`rootfs-v3.tar.zst`（732,840,538 字节，
  sha256 `CDCA41CDE1CFC8CF683A9FCC8D42119F917FC99E34367BF00C0C6BD6A166C0E3`）
- 相对 V2 只改了两处：
  1. `tiny_osk.py` 增加「设置」按钮 + `_open_settings()` 对话框；配置存
     `~/.config/tiny-osk.conf`（`layout` / `placement` / `key_height` / `opacity` 四键），
     按键高度改为读 `self.key_height`（原来是写死的 40 px）。
  2. `Dispatcher.doOpenRemoteOsk()` 增加 `if (!viewModel.pref.input.oskThreeFingerTap) return`，
     让「三指轻点」开关真正生效。AVNC 分支版本号 `3.2.2-tc4v2` → `3.2.2-tc4v3`。
  3. 镜像里补了剪贴板历史的 Windows 化：`Super+V` → `xfce4-popup-clipman`、
     `Super+Shift+V` → `xfce4-clipman-history`，并新增
     `home/tiny/.config/autostart/tiny-clipman.desktop`（deb 自带的 autostart 是
     `Hidden=true`，不会自动启动，必须自己补一条）。

## V4 —— 修复"装了新版本但桌面没变化"

- 文件 `apk-v4-tc423-xfce-zh-imagepatch-oskbutton.apk`，761,867,363 字节
- SHA-256 `95DDD15EB9F6709EC49985B7EF69B44788B1932387DCFE1078880D13960E4527`
- 内置镜像 `rootfs-v5.tar.zst`（732,841,425 字节，
  sha256 `D222BFA6580997C319403E99C0F18311EAAA51F5BA3A11D6B800204B0EA4A222`）
  + `assets/rootfs.patch.tar.zst`（554,647 字节，267 个新增/改动文件）
  + `assets/rootfs.stamp`（`v4-d222bfa6580997c3`）
- **根因**：`MainActivity` 只在 `installedContainers.isEmpty()` 时自动导入，
  覆盖安装时旧容器还在 → 新镜像从没被解压 → 所有镜像侧功能都没出现。
  现在启动比对 stamp，不一致弹三选一：只更新系统文件（`applyImagePatch()`，
  保留数据）/ 重新导入（清空）/ 以后再说。
- AVNC 分支 `3.2.2-tc4v6`；其余：`ValueLabelPreference` 数值标签、
  滚轮 1~9（`deltaPerScroll` 档位 3=20px 保持不变、9=74px）、指针颜色独立开关、
  亮度映射染色、九宫格删除改为单个 40dp 跟随按钮、右侧常驻按钮删除、
  OSK 三条召唤路径 + `/tmp/.tiny_osk.log`。

## V5 —— 光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃

- 归档：`build-env-toolchain\apks-archive-keep-forever\v5-caret-osk-hk-20261116\apk-v5-tc423-xfce-zh-caret-osk-hk.apk`
- 761,875,619 字节，SHA-256 `B2CD44F9F678364D3F6D334FDA33AC06A8CB985C48EE2477A54E12A12B51E6A3`
- 改了三层：
  - App 侧：`MainActivity` 静默打补丁 `autoPatchImageIfOutdated()`；
    `ContainerMainFragment` 多传一个 `tc4.osk_caret` 路径。
  - AVNC 侧（`3.2.2-tc4v9`）：`pref_input.xml` 恢复官方三个分类；
    `VncActivity` 用 `readCaretRect()` 读光标文件决定按钮位置。
  - 镜像侧：新增 `hk_layout.py`、`tiny_osk_caret.py`、`tiny-osk-caret` 与它的 autostart；
    `docklike-2.rc` 清空 `pinned=`。
- 教训：**改 `pref_input.xml` 不能删官方分类**，`PrefsActivity` 里有 11 个 `!!`。

## V6 —— 最终版：把键盘相关代码全部移除（最新，用户指定定稿）

- 归档：`build-env-toolchain\apks-archive-keep-forever\v6-final-no-keyboard-20261116\apk-v6-tc423-xfce-zh-final.apk`
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

## 回退方法

1. 找到对应版本目录里的 `.apk`，传到手机直接安装（同一证书，可覆盖安装）。
2. V1 → V2 是升级直接装；V2 → V1 若提示降级，先卸载再装（卸载会清容器数据，
   之后重新导入内置镜像即可）。
3. 装完不用配置，缩放默认就是自由的。

## 每次交付必须做的事

1. 新 APK 复制到 `apks-archive-keep-forever/v<序号>-<说明>-<日期>/`
2. 在 `readme-versions-zh.md` 追加条目：文件、字节数、SHA-256、相对上一版改了什么
3. 同步到 `out-apk-keep-forever/`（只放最新待交付的那一个）
4. **不要删旧版本**，用户明确要求保留回退路径
