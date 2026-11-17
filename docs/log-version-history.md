# 01 版本历史（交付过哪些 APK）

> 这篇只回答一件事：**交付过哪些版本、每版改了什么、怎么回退、签名参数是什么。**
> 要改哪个文件、哪一行，见 `spec-changes-and-rootfs.md`。
> 每一版都已经发到 GitHub Releases：`https://github.com/ssc8537/mobile-linux-pc/releases/tag/vN`

## 0. 归档位置（本机）

`build-env-toolchain/apks-archive-keep-forever/`

| 目录 | 版本 |
|---|---|
| `v1-baseline-zoomfree-20261115/` | V1（用户正式投产的第一版） |
| `v2-features-20261116/` | V2（首批功能） |
| `v3-osk-settings-20261116/` | V3（悬浮键盘补设置入口） |
| `v4-image-patch-oskbutton-20261116/` | V4（修「装了新 APK 桌面没变化」） |
| `v5-caret-osk-hk-20261116/` | V5（光标旁键盘 + 黑客键盘移植） |
| `v6-final-no-keyboard-20261116/` | **V6（当前版本，键盘全删的定稿）** |
| `_signing-keys-keep-forever/tc4-release.jks` | **唯一签名密钥，永久保留** |
| `readme-versions-zh.md` | 每次交付都要在这里追加条目 |

## 1. 签名参数（绝对不能改）

改了老版本就装不上去，用户会被迫卸载（卸载 = 清空容器数据）。

- alias：`tc4`
- storepass / keypass：都是 `tc4zoom`
- 证书 DN：`CN=TinyContainer ZoomPatch, OU=Personal, O=Personal, L=Local, ST=Local, C=CN`
- 证书 SHA-256：`cd4e54df0dfaab1f60729d2902664e81a90660aaebbf437fa6a5e6d9e766356b`
- 所有 V1~V6 共用这一把，因此可以互相覆盖安装

## 2. 六个版本一览

| 版本 | APK 字节数 | 镜像 | AVNC |
|---|---|---|---|
| V1 | 957,130,197 | 官方 `xfce-zh-20260808-160507.tar.zst`（928,728,904） | 上游 `030e6c032e`（未改） |
| V2 | 761,267,121 | `rootfs-v2.tar.zst` 732,818,799 | `3.2.2-tc4v2` |
| V3 | 761,288,905 | `rootfs-v3.tar.zst` 732,840,538 | `3.2.2-tc4v3` |
| V4 | 761,867,363 | `rootfs-v5.tar.zst` 732,841,425 + 覆盖包 554,647 | `3.2.2-tc4v6` |
| V5 | 761,875,619 | `rootfs-v6.tar.zst` 732,846,295 + 覆盖包 559,652 | `3.2.2-tc4v9` |
| V6 | 761,832,607 | `rootfs-v7.tar.zst` 732,826,915 + 覆盖包 546,965 | `3.2.2-tc4v10` |

> 镜像编号（v2/v3/v5/v6/v7）与 APK 版本号（V2~V6）**不是一一对应**，
> 因为 V4 之前改镜像没打版本号，中间跳过了 v4。看表时注意区分。

## 3. 各版本详情

### V1 —— 基线版本（唯一功能：缩放默认自由）

- 文件 `apk-v1-tc423-xfce-zh-zoomfree.apk`，957,130,197 字节
- SHA-256 `05EE9EF4453EB63D955E82288E8B8237F51D61866EF31A9A4A70DEEACAAB51DA`
- 上游 v4.2.3 原样 + **一行改动**：进入图形界面时缩放默认不锁定
  （`ContainerMainFragment.kt:150` `fZoomLocked = false`）
- 为什么只需要一行：AVNC 每次进图形界面都新建一个 `ID = 0` 的
  `ServerProfile`（不落库、不持久化），而 `ServerProfile.flags` 默认带
  `FLAG_ZOOM_LOCKED`。所以在唯一的创建点显式解锁，就等于「每次进来都是自由的，
  切后台回来也是自由的，只有用户自己点锁定才锁」。

### V2 —— 首批功能

- SHA-256 `F964A464EABE6198BBDDF576F825AE4666E1CF3DD8BD9370D36A5C3C0CFEB135`
- **AVNC 侧**（`3.2.2-tc4v2`）：鼠标加速开关 + 强度 1~8、慢速基准 10~100%、
  滚轮速度 1~5、指针大小 50~300%（默认 150%）、指针颜色取色器（粉色优先）、
  缩放误触确认（1.2 秒内二次缩放才生效）、指针旁九宫格键盘按钮、三指轻点呼出键盘
- **App 侧**：设置页新增「停止限制子进程（幻影进程）」一键跳转
- **镜像侧**：任务栏换 docklike（默认固定 Firefox / 文件管理器 / 文本编辑器）、
  补装 taskmanager / screenshooter / clipman / libqrencode4、
  粉色悬浮键盘 `/usr/local/bin/tiny-osk`、修 `/opt/tiny/export.sh` 不再删 `~/.mozilla`

### V3 —— 悬浮键盘补「设置」入口

- SHA-256 `3EEE8A5CCD85C635BF636152D87D1F64F1DED0F607A45602867A4ABD74455AD4`
- 相对 V2 三处：`tiny_osk.py` 加「设置」按钮和 `_open_settings()` 对话框
  （配置存 `~/.config/tiny-osk.conf`：`layout` / `placement` / `key_height` / `opacity`）；
  `Dispatcher.doOpenRemoteOsk()` 加 `oskThreeFingerTap` 开关判断；
  镜像补 `Super+V` → `xfce4-popup-clipman`、`Super+Shift+V` → `xfce4-clipman-history`，
  并新增 `tiny-clipman.desktop` 自启（deb 自带的那条是 `Hidden=true`，不会自启）

### V4 —— 修复「装了新版本但桌面没变化」

- SHA-256 `95DDD15EB9F6709EC49985B7EF69B44788B1932387DCFE1078880D13960E4527`
- **根因**：`MainActivity` 只在 `Global.installedContainers.isEmpty()` 时自动导入内置镜像。
  覆盖安装时旧容器还在 → 新镜像**永远不会**被解压 → 所有镜像侧功能都不出现。
  用户当时反馈「Ctrl+Shift+Esc 报 `执行子进程 XFCE4-taskmanager 失败，没有那个文件或目录`」就是这个病。
- **修法**：`assets/rootfs.stamp` 存镜像指纹，`Global.builtInImageStamp` 存「已导入过哪个」。
  启动时不一致 → 弹三选一（只更新系统文件 / 重新导入 / 以后再说）。
  V5 起改为静默调 `autoPatchImageIfOutdated()`，`askReimportImage()` 留作手动入口。
- 其余：`ValueLabelPreference` 数值标签（滑块旁显示「加速 6 倍」）、
  滚轮范围扩到 1~9（档位 3 = 官方原值 20px，9 = 74px）、
  指针颜色开关挪到颜色那一行、亮度映射染色（纯黑填充也能染色）、
  九宫格删除改为单个 40dp 跟随指针的按钮

### V5 —— 光标旁键盘 + 黑客键盘移植 + 修「输入」页崩溃

- SHA-256 `B2CD44F9F678364D3F6D334FDA33AC06A8CB985C48EE2477A54E12A12B51E6A3`
- 用户反馈「设置 AVNC → 输入 一点就跳进 Linux 桌面」。**根因是自伤**：
  重写 `pref_input.xml` 时删掉了上游的 `pref_mouse` / `pref_vk` / `pref_km` 三个分类，
  而 `PrefsActivity.kt:135/141` 用 `findPreference<SwitchPreference>("hide_local_cursor")!!`
  和 `("capture_pointer")!!`，缺一个就 NPE，整页渲染不出来。
  **教训：改 `pref_input.xml` 绝不能删官方分类，`PrefsActivity` 里有 11 个 `!!`。**
- 移植了 Hacker's Keyboard 的键位表（`gen_hk_layout.py` 解析它的 `res/xml/kbd_*.xml`）
- 键盘按钮改为跟随**文本光标**（AT-SPI）而不是鼠标指针

### V6 —— 当前版本：键盘相关代码全部移除（用户指定定稿）

- SHA-256 `81DB5DAC13B16B432E2F68077A193B583E6F647D0B0E93923784DD6ED00A4D47`
- 用户指令（m03615）：键盘不让写了，涉及键盘的代码全部移除，恢复到「V2 除了键盘」
  的状态，其他功能全部保留，作为定稿。
- 删掉的东西（AVNC `3.2.2-tc4v9` → `3.2.2-tc4v10`）：
  `VncActivity` 整个 OSK 区块约 200 行、`oskTriggerPath` / `oskCaretPath` 与两个 intent extra、
  `OskBridge.kt` 本身及 `ContainerMainViewModel` 里的注册/注销、
  `Dispatcher` 的 `open-osk` 分支与 `doOpenRemoteOsk()` / `nudgePointer()`、
  `InputHandler.nudgePointer()` / `sendKeySym()`、
  `AppPreferences.oskPointerButton` / `oskThreeFingerTap`（`tap3` 默认值回到 `"none"`）、
  `pref_input.xml` 整个「悬浮键盘」分类、`arrays.xml` 第 4 个三指选项、
  `styles.xml` 的 `OskRingButton`、两种语言各 18 条 `osk_*` 文案
- 镜像侧删除 9 个文件（3 个 py、3 个 `usr/local/bin/tiny-osk*`、2 个 autostart、1 个 desktop），
  `xfce4-keyboard-shortcuts.xml` 去掉 `XF86Launch0`
- `zoom_mis_touch_guard` 从被删的分类搬到「指针」分类末尾，功能不变
- **新增防御**：`applyImagePatch()` 解压前先 `$BIN_DIR/rm -rf` 旧键盘路径，
  从 V5 升上来不会留一个指向已删程序的自启项（那段清理代码是必要的，别删）
- 镜像 `rootfs-v7.tar` 2,683,729,920 字节 → `.zst` 732,826,915（sha `2c671cf642cd8313`）；
  覆盖包 546,965 字节（sha `caeb4e317afec5d7`，262 个成员 = 3 改 + 259 新增）；
  版本戳 `v6-2c671cf642cd8313`

## 4. 回退方法

1. 找对应版本的 `.apk`（本机归档目录，或 Releases 页面），传到手机直接安装。
   同一证书，可覆盖安装。
2. V2 及以后 → V1 若提示「降级」，先卸载再装。卸载会清容器数据，
   之后重新导入内置镜像即可（App 会自动做）。
3. 装完不用配置，缩放默认就是自由的。

## 5. 每次交付必须做的事（清单）

1. 新 APK 复制到 `apks-archive-keep-forever/v<N>-<说明>-<日期>/`
2. 在 `readme-versions-zh.md` 追加条目：文件、字节数、SHA-256、相对上一版改了什么
3. 同步一份到 `out-apk-keep-forever/`（只放最新待交付的那一个）
4. 更新本篇的第 2、3 节
5. **不要删旧版本**，用户明确要求保留回退路径
6. 只有用户明确说「上传」时才推 GitHub
