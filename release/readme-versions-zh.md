# APK 版本归档 / APK Version Archive

本目录保存**所有已经交付给用户、可回退**的 APK 版本。
每个版本一个子目录，目录名格式：`v<序号>-<说明>-<日期>`。
**这些文件永久保留，不要删除。**

This folder keeps every delivered, roll-back-able APK build.
One subdirectory per version: `v<index>-<note>-<date>`. **Never delete these files.**

---

## 回退方法 / How to roll back

1. 打开对应版本目录，找到 `apk-v*.apk`。
2. 传到手机，直接安装。
   - 所有版本都用**同一把签名证书** `_signing-keys-keep-forever/tc4-release.jks`
     （alias `tc4`，storepass / keypass `tc4zoom`），
     所以可以彼此覆盖安装，不会出现"应用未安装 / 签名冲突"。
   - 如果 Android 提示版本降级（versionCode 相同则不会），先卸载当前版本再装 V1；
     卸载会清掉容器数据，装完重新导入镜像即可。
3. 安装完不需要做任何配置，缩放默认自由。

`out-apk-keep-forever/` 只放**最新待交付**的 APK；正式存档一律进本目录。

---

## 版本清单 / Version index

### v1-baseline-zoomfree-20261115 —— 已投产的基线版本（用户当前在用）

- 文件：`apk-v1-tc423-xfce-zh-zoomfree.apk`
- 大小：957,130,197 字节（约 912.8 MiB）
- SHA-256：`05EE9EF4453EB63D955E82288E8B8237F51D61866EF31A9A4A70DEEACAAB51DA`
- 本版实现的功能（一句话）：**自由缩放** —— 进入 Linux 桌面时不再默认锁定缩放，
  单指/双指缩放随时可自由使用，只有你自己点工具栏的锁形按钮才会锁定；
  退到后台、重新进入图形界面，依旧是自由缩放。除此之外与官方 v4.2.3 完全一致。
- 上游基准：Cateners/tiny_container v4.2.3（versionCode 4，versionName 4.2.3）
- 内置镜像：`xfce-zh-20260808-160507.tar.zst`（928,728,904 字节，
  sha256 `38093D8D1CE5C8F98349C0B03135CCC3236E81EF94F04CFEA844F7A53409D2C2`），
  以 STORED（不压缩）方式放在 `assets/rootfs.tar.zst`
- 本版相对上游的**唯一改动**：
  - `app/src/main/java/com/fct/tc4/ui/page/ContainerMainFragment.kt:150`
    在 `GuiNavigationEvent.OpenAvnc` 分支创建 `ServerProfile` 时追加一行
    `fZoomLocked = false`
  - 效果：进入 Linux 图形界面时，AVNC 的"锁定缩放"默认关闭（自由缩放）；
    退到后台再回来、重新进入 GUI，也依旧是自由缩放；只有用户自己点工具栏的
    锁形按钮才会锁定。
- 构建附带改动（不影响功能，仅为了能在本机编出 APK）：
  - 新增 `signingConfigs.release`（自签证书）
  - 移除 `externalNativeBuild.cmake`，4 个 JNI `.so` 预先用 NDK clang 手工编译进 `jniLibs/arm64-v8a`
  - `androidResources { noCompress.add("zst") }`
  - `gradle.properties`：`android.overridePathCheck=true`、`org.gradle.vfs.watch=false`
- 已知现象：应用内"检查更新"会提示有新版（因为 versionName 仍是 4.2.3，与上游相同），
  可以忽略。
- 本版功能（一句话）：**自由缩放**。进入 Linux 图形界面后，左侧工具栏的"锁定缩放"
  默认是关的，双指可以自由缩放；退到后台再回来、重新进 GUI 也依旧是自由的；
  只有用户自己点那个锁形按钮才会锁定。除此之外与上游 v4.2.3 完全一致。
- 备注：用户确认此版本已正式投入使用，功能正常。此版本**没有**任何后续新增功能
  （鼠标加速开关、光标颜色/大小、任务栏 dock、悬浮键盘等都不包含）。

### v2-features-20261116 —— 功能增强版（鼠标/光标/悬浮键盘/任务栏）

- 文件：`apk-v2-tc423-xfce-zh-mouse-cursor-osk.apk`
- 大小：761,267,121 字节（约 726.0 MiB，比 v1 小约 190 MB —— 新镜像内层压缩率更好）
- SHA-256：`F964A464EABE6198BBDDF576F825AE4666E1CF3DD8BD9370D36A5C3C0CFEB135`
- 签名：与 v1 同一证书（SHA-256 `cd4e54df…66356b`），可直接覆盖安装
- 内置镜像：重新打包的 `rootfs-v2.tar.zst`（732,818,799 字节，
  sha256 `5E1B7C61AE0C59C2F429C4BA4F3595B10625FC892C2CD3D32F948DF7F4DEF5F2`），
  以 STORED 方式放在 `assets/rootfs.tar.zst`
- 相对 v1 新增（APK 侧，AVNC fork `3.2.2-tc4v2`）：
  - 输入设置新增"鼠标加速"开关（默认开）+ 加速强度滑块 1~8（默认 6 = 上游原值）
  - 新增"慢速移动速度"滑块 10~100（默认 30 = 上游原值）
  - 新增"滚轮速度"滑块 1~5（默认 3 = 上游原值 20 像素/格）
  - 新增"指针大小"滑块 50~300（默认 150 = 1.5 倍）与"指针颜色"取色器（粉色在前，可恢复原色）
  - 新增"缩放前确认"：首次双指缩放只弹提示，1.2 秒内再缩放才真正生效（防误触）
  - 新增悬浮键盘入口：指针旁九宫格按钮（默认开）与三指轻点（默认开）
  - 设置页新增"停止限制子进程"跳转按钮（直达开发者选项）
- 相对 v1 新增（镜像侧）：
  - docklike 任务栏替换原 tasklist，默认固定 Firefox / 文件管理器 / 文本编辑器
  - 新增 xfce4-taskmanager、xfce4-screenshooter、xfce4-clipman(+plugin)、libqrencode4
  - 新增粉色悬浮键盘 `/usr/local/bin/tiny-osk`（python3 + GTK3 + XTEST，可拖动、
    可停靠、双布局、设置入口），自启 + `XF86Launch0` 快捷键 + `/tmp/.tiny_osk_toggle` 触发
  - 修复 `/opt/tiny/export.sh`：不再删除 `~/.mozilla` 等个人数据（导出容器不再丢浏览器资料）
- 已知现象：应用内"检查更新"仍提示有新版（versionName 保持 4.2.3），可忽略。

### v3-osk-settings-20261116 —— 悬浮键盘补上"设置"入口（推荐安装）

- 文件：`apk-v3-tc423-xfce-zh-osk-settings.apk`
- 大小：761,288,905 字节（约 726.0 MiB）
- SHA-256：`3EEE8A5CCD85C635BF636152D87D1F64F1DED0F607A45602867A4ABD74455AD4`
- 签名：与 v1/v2 同一证书，可直接覆盖安装（会清掉旧容器，装完重新导入镜像即可）
- 内置镜像：`rootfs-v3.tar.zst`（732,840,538 字节，
  sha256 `CDCA41CDE1CFC8CF683A9FCC8D42119F917FC99E34367BF00C0C6BD6A166C0E3`）
- 相对 v2 的改动：
  - **悬浮键盘新增"设置"按钮**（顶部工具栏，位于 布局/停靠 后面）。点开是
    "悬浮键盘设置"对话框，可改：默认布局（全键盘 / 精简键盘）、默认位置
    （悬浮 / 停靠）、按键高度（32~64 px，默认 40）、不透明度（60~100%，默认 96%）。
    保存到 `~/.config/tiny-osk.conf`，下次启动沿用。
  - 按键尺寸改为跟随"按键高度"设置（原来固定 40 px）。
  - "三指轻点"开关现在真正生效：关掉后三指轻点不再请求键盘
    （AVNC fork 版本号 `3.2.2-tc4v2` → `3.2.2-tc4v3`）。
  - 剪贴板历史对齐 Windows：`Super+V` → `xfce4-popup-clipman`，
    `Super+Shift+V` → `xfce4-clipman-history`；并新增用户级自启动
    `~/.config/autostart/tiny-clipman.desktop`（deb 自带的那条是 `Hidden=true`，
    不会自动跑，所以必须自己加一条）。
- 其余功能与 v2 完全一致。

### v4-image-patch-oskbutton-20261116 —— 修复"装了新版本但桌面没变化"（推荐安装）

- 文件：`apk-v4-tc423-xfce-zh-imagepatch-oskbutton.apk`
- 大小：761,867,363 字节
- SHA-256：`95DDD15EB9F6709EC49985B7EF69B44788B1932387DCFE1078880D13960E4527`
- 签名：与 v1/v2/v3 同一证书，可直接覆盖安装
- 内置镜像：`rootfs-v5.tar.zst`（732,841,425 字节，
  sha256 `D222BFA6580997C319403E99C0F18311EAAA51F5BA3A11D6B800204B0EA4A222`）
  + 新增覆盖包 `assets/rootfs.patch.tar.zst`（554,647 字节，只含 267 个新增/改动文件）
  + 新增 `assets/rootfs.stamp`（镜像指纹，内容 `v4-d222bfa6580997c3`）
- **本版最重要的一处修复（用户反馈"任务栏没变、键盘没出现、Ctrl+Shift+Esc 报找不到命令"）**：
  v2/v3 把新镜像放进 APK 了，但 `MainActivity` 只在"一个容器都没有"时才自动导入，
  覆盖安装时旧容器还在，新镜像 732 MB 从来没被解压过，所以所有镜像侧功能都没生效。
  现在启动时比对 `assets/rootfs.stamp` 与已记录的指纹，不一致就弹三选一对话框：
  - **只更新系统文件（推荐，保留个人数据）** → `applyImagePatch()`，把
    `rootfs.patch.tar.zst` 解压到现有容器上，不删 `dataDir/<code>`；
    浏览器配置、文档、已装软件都保留。
  - 重新导入（会清空容器数据）→ 原 `autoInstallBuiltInContainer()`。
  - 这次先不导入 → 记下指纹，以后不再提示（下次换镜像会再提示）。
- 相对 v3 的其余改动：
  - 鼠标加速强度滑块显示"加速 N 倍"，慢速速度显示"N%"，滚轮速度显示"档位 N"
    （新增 `ValueLabelPreference`）。
  - 滚轮速度范围 1~5 → **1~9**。`deltaPerScroll` 分段计算：
    档位 1~3 用 `8 + 档位*4`（12 / 16 / 20 px），档位 3 = 20 px = 上游原值不动；
    档位 4~9 用 `20 + (档位-3)*9`（29 / 38 / 47 / 56 / 65 / 74 px）。
    也就是档位 9 比官方原值慢 3.7 倍（用户要的"再慢一点"），档位 3 保持原样。
  - 指针颜色新增**独立开关**"启用指针颜色"（默认关），就在颜色行上方、`?` 左边；
    关掉时完全不染色。
  - 指针染色算法改为按亮度映射（`luma` + `mix(0.30,1.15)`），不再是简单乘法，
    所以黑色填充部分也会变成所选颜色的深色，不再"只有描边变粉"。
  - **九宫格彻底删除**（`view_osk_ring.xml` 已移除），改为**光标旁一个 40dp 小按钮**：
    每 100 ms 跟随远端指针，8 个方向里挑第一个不出屏的位置放着；点它就是召唤键盘。
    右侧那个常驻按钮也一并移除（用户明确说没让做）。
  - 悬浮键盘三条召唤路径（原来只有一条，且依赖 X keymap）：
    1. 写触发文件 `filesDir/tmp/.tiny_osk_toggle`（容器 `/tmp` 就是它的 bind）；
    2. `OskBridge.summon` → 宿主 App 往容器 shell 里执行
       `/usr/local/bin/tiny-osk-toggle`（最可靠）；
    3. 兜底才发 `XF86XK_Launch0`。
  - `tiny-osk` / `tiny-osk-toggle` 两个脚本加了日志 `/tmp/.tiny_osk.log`；
    toggle 发现键盘进程不在会先 `nohup` 拉起来再写触发文件；
    `tiny_osk.py` 启动时自己猜 DISPLAY（`/tmp/.X11-unix/X*`），
    任何异常都写进日志而不是静默退出。键盘按键区也按实体键盘补了
    `[{ }] \| ;: '" ,< .> /?` 和 `0/Ins` 的副标。
- 已知现象：应用内"检查更新"仍提示有新版（versionName 保持 4.2.3），可忽略。

### v5-caret-osk-hk-20261116 —— 光标旁键盘 + 真·黑客键盘移植 + 修「输入」崩溃（推荐安装）

- 目录：`apks-archive-keep-forever\v5-caret-osk-hk-20261116\`
- 文件：`apk-v5-tc423-xfce-zh-caret-osk-hk.apk`
- 大小：761,875,619 字节
- SHA-256：`B2CD44F9F678364D3F6D334FDA33AC06A8CB985C48EE2477A54E12A12B51E6A3`
- 证书：`CN=TinyContainer ZoomPatch` / `cd4e54df0dfaab1f60729d2902664e81a90660aaebbf437fa6a5e6d9e766356b`（与前四版同一把，可覆盖安装）
- 内置镜像：`assets/rootfs.tar.zst` 732,846,295 字节 sha `eea4cc0ae499eace`；
  增量包 `assets/rootfs.patch.tar.zst` 559,652 字节 sha `f2cb1aa3fd51c498`（271 个成员）；
  版本戳 `assets/rootfs.stamp` = `v5-eaa4cc0ae499eace`
- AVNC 分支：`3.2.2-tc4v9`

本版修的四件事（对应用户 m03286 反馈）：

1. **「设置 AVNC → 输入」打不开（是我的回归 bug）**：
   我重写 `pref_input.xml` 时删掉了官方 `pref_mouse` / `pref_vk` / `pref_km` 三个分类，
   而 `PrefsActivity.kt` 对这 11 个配置项做了 `!!` 非空断言，找不到就抛 NPE，整页崩。
   三个分类已原样恢复，现在的 `pref_input.xml` = 官方 24 个 key + 我们新增 8 个 key。
2. **键盘按钮改成跟「文本光标」而不是鼠标指针**：
   新增容器内 `tiny_osk_caret.py`（AT-SPI 取焦点文本控件的字符范围，取不到则退回
   活动窗口右侧 1/3 处），每 180ms 写 `/tmp/.tiny_osk_caret`（一行 `可见 x y w h`），
   经 proot 绑定到 `filesDir/tmp`；Android 侧 `VncActivity.readCaretRect()` 读它，
   经 `frameState.toVP()` 映射到视图坐标，按 8 方向避让摆放 40dp 按钮。
   无光标时按钮 `GONE`，不再常驻。新增字段 `oskCaretPath`、intent extra `tc4.osk_caret`。
3. **真·黑客键盘移植（不再是自写布局）**：
   克隆 `klausw/hackerskeyboard`，`tools-probe-scripts-deletable/gen_hk_layout.py`
   解析它自己的 `res/xml/kbd_full.xml`、`kbd_compact.xml`、`kbd_symbols.xml`、
   `kbd_symbols_shift.xml` 与 `res/values/keycodes.xml`、`donottranslate-keymap.xml`，
   生成 `osk/hk_layout.py`（HK_FULL 6 行 79 键 / HK_COMPACT 6 行 63 键 /
   HK_SYMBOLS 5 行 40 键 / HK_SYMBOLS_SHIFT 5 行 40 键），每格
   `(label, keysym, role, shift_label, width_pct, popup)`。
   `tiny_osk.py` 改为从 `hk_layout` 取表，并新增 `shift_locked`、长按输入 popup 字符、
   按行归一化宽度；`_fill_grid()` 按 6 元组解包、`set_homogeneous(True)`。
4. **任务栏不再预固定程序**：`docklike-2.rc` 的 `pinned=` 已清空（78 字节）。

另：`MainActivity` 的三选一对话框改为**静默自动打补丁** `autoPatchImageIfOutdated()`，
装完首次进入不需要点任何东西；`askReimportImage()` 保留作手动入口。

### v6-final-no-keyboard-20261116 —— 最终版：彻底移除键盘（用户指定定稿）

- 目录：`apks-archive-keep-forever\v6-final-no-keyboard-20261116\`
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

### 后续版本

新版本编译完成后在此处追加条目，格式同上（版本目录、文件、大小、SHA-256、
相对上一版新增/修复了什么）。
