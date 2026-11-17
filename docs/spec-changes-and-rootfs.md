# 02 改了哪些文件 + 镜像内部结构

> 这篇回答两件事：
> **（A）相对上游我们改了哪些文件、在哪一行**（上游更新时按这个清单贴回去）
> **（B）容器镜像里长什么样、改哪个文件有用**（改镜像前必读）
> 编译步骤见 `build-and-upstream-sync.md`。

> ⚠️ 本文所有行号都以 **V6 交付时**的状态为准。V6 是当前基线。

---

# A 部分：App 与 AVNC 的改动清单

## A0. 先搞清楚改在哪

| 层 | 实际改在哪 | 怎么合并上游更新 |
|---|---|---|
| App 层 | `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container`（`apps-tiny-container-v423-source` 里**只有** `fZoomLocked` 一行） | 手贴 12 个文件 |
| AVNC 层 | `avnc-upstream-fork-deletable`（独立 fork 仓库） | 重新贴补丁 / rebase |
| 镜像层 | `tools-probe-scripts-deletable/build_rootfs_v2.py` | 改脚本常量重跑 |

## A1. App 侧（`com.fct.tc4`）

| 文件 | 改动 | 行号 |
|---|---|---|
| `ui/page/ContainerMainFragment.kt` | `ServerProfile` 创建点加 `fZoomLocked = false`（**V1 的唯一功能，绝不可丢**） | L150（注释 L146-149） |
| `ui/misc/Global.kt` | 新增镜像指纹三件套 | `var builtInImageStamp: String` L279、`fun readBuiltInImageStamp(): String` L284、`fun isBuiltInImageOutdated(): Boolean` L293 |
| `ui/main/MainActivity.kt` | 启动判断 + 静默打补丁 + 手动重装入口 | L272 `if (Global.installedContainers.isNotEmpty() && Global.isBuiltInImageOutdated())`、L275 `autoPatchImageIfOutdated()`、L301 `private fun autoPatchImageIfOutdated()`、L308 `private fun askReimportImage()` |
| `ui/page/ContainerManageViewModel.kt` | 增量覆盖、导入时维护指纹 | `fun applyImagePatch()` L385、`fun startBuiltInImport()` L452、`fun autoInstallBuiltInContainer()` L475、`fun confirmInstall(code: String, launchAfterInstall: Boolean)` L520 |
| `ui/page/SettingsViewModel.kt` | 新增一条可点项「停止限制子进程」 | L131 `id = "dev_options_phantom",` |
| `ui/page/SettingsFragment.kt` | 处理上面的点击，跳开发者选项 | L129 `"dev_options_phantom" -> {` |
| `res/values/strings.xml`、`res/values-zh-rCN/strings.xml` | 新增 `tc4_settings_dev_options_*` 三条 + `tc4_reimport_*` 五条 | — |
| `app/build.gradle.kts` | 加 `signingConfigs`（读 `tc4-release.jks`）、`noCompress.add("zst")` | — |
| `gradle.properties` | `android.overridePathCheck=true`、`org.gradle.vfs.watch=false` | — |
| `settings.gradle.kts` | 本地 maven 仓库**必须排在 jitpack 之前** | 依赖块内 |
| `gradle/libs.versions.toml` | `avnc = "3.2.2-tc4v10"` | — |
| `assets/rootfs.stamp` | 新增文件，内容 `v6-2c671cf642cd8313`（换镜像必须同步改） | — |
| `assets/rootfs.patch.tar.zst` | 新增文件，只含新增/改动的 262 个成员 | — |
| `assets/rootfs.tar.zst` | 完整镜像 732,826,915 字节（以 STORED 存进 APK，必须配 `noCompress("zst")`） | — |

其余 App 文件全是上游原文件。

### 这几条改动在干什么（读代码前先看这个）

- **`fZoomLocked = false`**：AVNC 每次进图形界面都新建 `ID = 0` 的 `ServerProfile`
  （不落库、不持久化），而 `ServerProfile.flags` 默认带 `FLAG_ZOOM_LOCKED`（`0x04L`，
  见 AVNC 的 `model/ServerProfile.kt:125`）。所以只要在唯一的创建点显式解锁，
  就永远自由——包括切后台再回来。用户手动点「锁定缩放」才锁。
- **镜像指纹机制**：解决「装了新 APK 但桌面功能全都没出现」。原来的
  `MainActivity` 只在 `installedContainers.isEmpty()` 时导入内置镜像，覆盖安装时
  旧容器还在，新镜像永远不被解压。现在记指纹 → 不一致就覆盖（不删 `dataDir/<code>`）。

## A2. AVNC 侧（fork 自 `https://github.com/tiny-computer/avnc`，基线 commit `030e6c0`）

版本号 `3.2.2-tc4v10`。相对上游 **17 个文件改动（+419 / −43 行）、6 个新增**。

| 文件 | 改动 |
|---|---|
| `app/build.gradle` | 注释掉 `externalNativeBuild`（CMake 在本机沙箱不可用）；`ndk { abiFilters ... }`；版本号；本地 maven 发布仓库 |
| `gradle.properties` | `android.overridePathCheck=true`、`org.gradle.vfs.watch=false` |
| `util/AppPreferences.kt` | `Input` 内新增偏好键；关键默认值：`cursor_size` **默认 150**（`coerceIn(50,300)`）、`cursor_tint_enabled` 默认 **false**、`mouse_acceleration` 默认 **true**、`zoom_mis_touch_guard` 默认 **true** |
| `ui/vnc/input/PointerAcceleration.kt` | 加速曲线参数化。`fun strengthToMaxFactor(strength: Int): Float = 0.5f + (strength.coerceIn(1, 8) - 1) * 0.6f` ⇒ **强度 6 = 3.5f = 上游原值**；`minFactor() = slowPointerSpeed / 100f`；三层曲线 `THRESHOLD1 = 10f` / `THRESHOLD2 = 80f` / `BASELINE_FACTOR = 1f` 未改 |
| `ui/vnc/input/PointerModes.kt` | `deltaPerScroll` 改为按 `scrollSpeed` 分两段：`<= 3` 时 `8F + scrollSpeed * 4F`（1→12、2→16、3→20 = 上游原值），否则 `20F + (scrollSpeed - 3) * 9F`（4→29 … 9→74）；加速开关判断 |
| `ui/vnc/input/TouchHandler.kt` | 缩放误触二次确认：`ZOOM_CONFIRM_WINDOW_MS = 1200L` |
| `ui/vnc/input/Dispatcher.kt` / `InputHandler.kt` | V6 后只剩缩放提示转发（键盘相关的 `open-osk` / `nudgePointer` / `sendKeySym` 已删） |
| `ui/vnc/gl/Cursor.kt` | `var scale = 1f`，按它缩放 `width` / `height` / `normalDrawRect` 与热点 |
| `ui/vnc/gl/Program.kt`、`Shaders.kt` | 新增 `u_Tint` uniform + `setTint()`；片元着色器用**亮度映射**染色，所以纯黑填充的指针也能被染色 |
| `ui/vnc/gl/Renderer.kt` | 每帧读 `cursorScale` / `cursorTint`，`tint == 0 \|\| !cursorTintEnabled` 时不染色 |
| `ui/vnc/VncActivity.kt` | 缩放误触提示浮层（键盘区块 V6 已全部删除） |
| `res/xml/pref_input.xml` | 新增设置项。**258 行，5 个分类顺序：输入 / 指针 / 鼠标 / 虚拟键盘 / 键盘映射** |
| `res/values/{str,array,style}*.xml`、`values-zh-rCN/strings.xml`、`res/values/attrs.xml` | 文案、三指选项、`OskRingButton` 已删、`ValueLabelPreference` 的 styleable |
| `app/roomSchema/.../7.json` | 构建时自动生成，非手改 |

新增文件：
- `ui/prefs/ValueLabelPreference.kt`（滑块旁显示「加速 6 倍」「150%」「档位 3」）
- `ui/prefs/SwitchPreferenceEx.kt`（带 `?` 帮助按钮的开关）
- `ui/prefs/ColorPreference.kt`（取色器，粉色优先）
- `res/layout/view_zoom_hint.xml`（缩放提示浮层）
- `res/layout/view_switch_help.xml`（开关 + `?` 的行布局）
- `app/src/main/jniLibs/<abi>/libnative-vnc.so`（4 个 ABI，从官方 AAR 提取，**不要重编**）

### `pref_input.xml` 的完整 key 顺序（改它之前必读）

输入：`gesture_style`(22) `gesture_double_tap`(31) `gesture_long_press`(39) `gesture_tap2`(47)
`gesture_tap3`(55, 默认 `none`) `gesture_swipe1`(63) `gesture_swipe2`(71) `gesture_swipe3`(79)
`gesture_double_tap_swipe`(87) `gesture_long_press_swipe`(96) `gesture_swipe_sensitivity`(104)
`invert_vertical_scrolling`(110) `mouse_acceleration`(118) `mouse_acceleration_strength`(126)
`slow_pointer_speed`(135) `scroll_speed`(143) `zoom_mis_touch_guard`(151)

指针：`cursor_size`(163) `cursor_tint`(170)
鼠标：`mouse_passthrough`(180) `capture_pointer`(188) `hide_local_cursor`(193) `hide_remote_cursor`(198) `mouse_back`(205)
虚拟键盘：`vk_open_with_keyboard`(216) `vk_use_super_with_single_tap`(221) `vk_row_count`(228)
键盘映射：`km_right_alt_to_super`(243) `km_language_switch_to_super`(248) `km_back_to_escape`(253)

> **不能删任何官方分类**。`PrefsActivity.kt:135/141` 对 `hide_local_cursor` 和
> `capture_pointer` 用了 `!!`，缺一个就 NPE，整个「输入」页打不开（V5 踩过这个坑）。

## A3. 可重放的补丁脚本（`tools/patch/`）

App 侧每个改动点一个脚本，按顺序跑就能把上游原版改成 V6 基线：

| 脚本 | 目标文件 |
|---|---|
| `patch_stamp1.py` | `Global.kt`（指纹三件套） |
| `patch_install_stamp.py` | `ContainerManageViewModel.kt`（导入时写指纹） |
| `patch_apply_patch_vm.py` | `ContainerManageViewModel.kt`（`applyImagePatch()`） |
| `patch_patch_cleanup.py` | `ContainerManageViewModel.kt`（解压前清旧键盘残留） |
| `patch_main_reimport.py` | `MainActivity.kt`（启动判断 + 两个函数） |
| `patch_devoptions.py` | `SettingsViewModel.kt` + `SettingsFragment.kt` + 文案 |
| `patch_reimport_strings.py` / `patch_strings.py` / `patch_strings2.py` | `strings.xml` |

> 注意：部分脚本里写的是**绝对路径**
> `p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\…'`，
> 换机器要改这一行。脚本都是幂等写法（先 `assert` 锚点存在再替换）。

---

# B 部分：镜像内部结构

## B1. 系统身份

- 发行版 **Debian GNU/Linux 13 (trixie)**，`DEBIAN_VERSION_FULL=13.6`，arm64
- 桌面 XFCE 4.20.4 + xfwm4，GTK 3.24；浏览器 Firefox ESR 140.13.0esr；1147 个包
- 内核串是伪造的：`Linux localhost 6.17.0-PRoot-Distro … aarch64`
- **不是完整 Linux**：proot 是用户态路径/系统调用翻译，没有真 root、没有 systemd、
  不支持 mount / 内核模块 / loop 设备 / tun-tap。Wine、部分游戏、Docker、
  Wireshark 混杂模式基本跑不起来；Chrome / Electron / VS Code 必须关沙箱
  （镜像里已预置 `MOZ_FAKE_NO_SANDBOX=1` 与 `*-no-sandbox.desktop`）。
  **这是用户「装了很多软件用不了」的根因，不是 App 的 bug。**
  最好的心智模型：把它当「带 apt 的应用运行环境」，不是「完整 Linux」。

## B2. 用户与权限

- 主用户 `tiny`，uid/gid 1000（`--change-id=1000:1000`）
- tar 内文件属主统一 `10258:10258 aid_u0_a258`；安装时 App 会
  `sed -i '/^aid_/d'` 清掉 passwd/group 里的 aid 行再补自己的
- `sudo` / `pkexec` 存在且是 4755（proot 内可用）

## B3. 关键路径

| 路径 | 说明 |
|---|---|
| `.tiny.yaml`（tar 第一项） | 容器定义：`code: xfce`、启动命令、快捷命令、GPU 选项组、lstat 缓存 |
| `/opt/tiny/export.sh` | 导出容器的脚本，**V2 已修**（不再 `apt clean`、不再删 `~/.mozilla`） |
| `/opt/tiny/` | 字体、微信、亿图、CAJ、WPS 等预置素材 |
| `home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/` | 所有 XFCE 配置（面板、快捷键、主题、窗口管理器） |
| `home/tiny/.config/autostart/` | 自启项（现在只有 `tiny-clipman.desktop`） |
| `home/tiny/.config/xfce4/panel/docklike-2.rc` | docklike 任务栏配置（固定项 `pinned=` 在这里，V6 已清空） |
| `/公共` | 与安卓共享的目录（对应 App 的 `filesDir/public`） |
| `/mnt/sdcard` | 安卓内部存储 |

## B4. 改面板（最常用）

文件 `home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml`

- 只有 `panel-1`：`position="p=8;x=678;y=596"`（底部）、`size=32`、13 个 plugin
- plugin 编号含义：12 whiskermenu、1 directorymenu、**2 docklike（V2 换的）**、
  3 分隔、4 pager、5 分隔、6 systray、11 脉冲音频、13 通知、7 分隔、8 时钟、9 分隔、10 显示桌面
- V1 时 plugin-2 是 `tasklist`（原版任务栏，**没有固定功能**）。XFCE 的 tasklist 本身
  就不支持「固定」，固定是独立 `launcher` 插件的行为。真正的 Windows 式固定需要
  窗口分组插件，所以换成了 docklike。

## B5. 改快捷键

文件 `home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml`

- `commands.default` 放 `type="empty"` 占位，`commands.custom` 放真正命令
- 现在自定义的只有两条：`<Super>v` → `xfce4-popup-clipman`、`<Super><Shift>v` → `xfce4-clipman-history`
- V3 曾加过 `XF86Launch0` → `tiny-osk-toggle`，**V6 已删**
- 原版有个坑：`Print` 与 `<Primary><Shift>Escape` 绑的是 `xfce4-screenshooter` 和
  `xfce4-taskmanager`，但**这两个软件原本没装**（按了没反应）。V2 已补装。

## B6. 被删掉/没有的软件

`libreoffice`、`gimp`、`picom`、`xdotool`、`wmctrl`、`code`、`wine`、`flameshot`、
`copyq`、`rofi` 都没有。要补装就走 `.tiny.yaml` 的 `quick_commands` 加一条一键安装命令，
**不要改 App 代码**。

## B7. GPU 加速（现成能力，默认关）

`.tiny.yaml`（容器定义，即可在「选项配置」标签页里勾的那个列表）里有 `图形加速` 选项组：

- `Virgl 加速`：`GALLIUM_DRIVER=virpipe` + 起 `virgl_test_server`，**VNC 下可用、安全**
- `Adreno GPU 加速`（四个子项：`Turnip + Zink`、`启用 DRI3 的 Turnip + Zink`、
  `Freedreno`、`启用 DRI3 的 Freedreno`）：**只适用于 Termux:X11，VNC 下别开**

全部 `enabled: false`。App 的「选项配置」页勾选即可，不需要改代码。
jniLibs 里已带 `virgl_test_server` 与 `libvirglrenderer.so` / `libepoxy.so`，
`Global.kt` 会把它们 symlink 到 `bootstrap/bin` 与 `bootstrap/lib`。

## B8. 美化约束

容器内**不要装 GNOME/KDE 主题包**。XFCE 主题只需 GTK3 主题 + 图标主题放到
`~/.themes` / `~/.icons`。当前是 `Fluent-Light` 主题 + `Fluent` 图标。

## B9. 键盘：V6 已整体移除（别再往回加）

用户在 m03615 明确要求「键盘不写了，全部删掉」，所以 V6 起：

- 镜像里**没有** `usr/local/share/tiny-osk/`（`tiny_osk.py` / `hk_layout.py` / `tiny_osk_caret.py`）
- 镜像里**没有** `usr/local/bin/{tiny-osk,tiny-osk-toggle,tiny-osk-caret}`
- 没有对应 autostart 与 `.desktop`，快捷键里没有 `XF86Launch0`
- APK 里没有 OSK 按钮、没有 `OskBridge`、没有 `tc4.osk_*` intent extra、
  没有「悬浮键盘」设置分类，三指轻点回到官方 3 个选项

历史实现在 `archive-research-and-plans.md`，**只作参考，不要照它恢复**。
若将来真的要重做，先问用户。

> **唯一保留的相关代码**：`applyImagePatch()` 开头那几条 `$BIN_DIR/rm -rf` / `rm -f`，
> 用来在打增量包前清掉旧版残留的键盘文件（否则从 V5 升上来会留一个指向已删程序的
> 自启项，每次登录报错）。这段是必要的，不要删。

## B10. 镜像重打包命令（当前就是这条链）

```powershell
$env:PYTHONPATH = "<workspace>\tools-probe-scripts-deletable\pyz2"   # zstandard wheel，pip 装不上
python tools-probe-scripts-deletable\unzst_tar.py <in.tar.zst> cache\rootfs-plain.tar
python tools-probe-scripts-deletable\build_rootfs_v2.py cache\rootfs-plain.tar cache\rootfs-v7.tar
python tools-probe-scripts-deletable\make_patch_tar.py cache\rootfs-plain.tar cache\rootfs-v7.tar cache\rootfs-patch-v7.tar
python tools-probe-scripts-deletable\verify_rootfs_v2.py cache\rootfs-v7.tar
python tools-probe-scripts-deletable\zst_tar.py cache\rootfs-v7.tar cache\rootfs-v7.tar.zst 19 4
python tools-probe-scripts-deletable\zst_tar.py cache\rootfs-patch-v7.tar cache\rootfs-patch-v7.tar.zst 19 4
```

V6 实测产出：`copied members: 115886`、`patched files: 3`、`appended new members: 259`、
`rootfs-v7.tar` 2,683,729,920 字节 → `.zst` 732,826,915（sha `2c671cf642cd8313`）；
覆盖包 546,965 字节（sha `caeb4e317afec5d7`，262 个成员 = 3 改 + 259 新增）。

脚本**不解压到磁盘**，逐个 tar 成员流式重写，所以 uid/gid/权限/时间戳原样保留；
身份固定 `10258:10258 aid_u0_a258`，格式必须是 **GNU tar**（不是 PAX）。

`build_rootfs_v2.py` 里可改的关键常量：`OWNER_UID = 10258`、`OWNER_UNAME`/`OWNER_GNAME = 'aid_u0_a258'`、
`DEBS` 指向 `build-env-toolchain/cache-downloads-deletable/debs`，deb 清单是
`libqrencode4` / `xfce4-taskmanager` / `xfce4-screenshooter` / `xfce4-clipman` /
`xfce4-clipman-plugin` / `xfce4-docklike-plugin`（六个）。

## B11. 版本戳必须同步（否则用户以为没变化）

三份 assets 必须一起换：`rootfs.tar.zst`（全新安装）、`rootfs.patch.tar.zst`（增量）、
`rootfs.stamp`（指纹）。写 stamp 用下面这行，避免 PowerShell 5.1 的
`Set-Content -Encoding UTF8` 加 BOM（Gradle 会报 `Unexpected character ''`）：

```powershell
[System.IO.File]::WriteAllText("<...>\assets\rootfs.stamp", "v6-<sha前16位>", (New-Object System.Text.UTF8Encoding $false))
```

## B12. 判断「哪些必须保留」的一句话规则

> 只要文件在本文档出现，就用**我们的版本**；没出现的，一律用**上游新版本**。
> 上游若改了同一个文件，用 `git diff` 只挑我们的那几行重新贴到新版上，**不要整文件覆盖**。
