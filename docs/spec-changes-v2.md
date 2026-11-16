# 02 我们改了什么（相对上游的文件清单）

> 这篇回答：**哪些文件是我们改的，哪些是上游原文件。**
> 上游更新时，只保留下面列出的「我们的改动」，其余一律用官方新版本覆盖。

## 我们的仓库结构

```
apps-tiny-container-v423-source   App 源码（上游 v4.2.3 副本，含我们的一行修改）
avnc-upstream-fork-deletable      AVNC 分支（我们在这里加功能，编译成 AAR）
build-env-toolchain               构建环境 + APK 归档（永久保留）
docs-project-notes-keep-forever   文档（本目录，永久保留）
refs-reference-assets-deletable   参考素材、本地 maven 仓、jni 预编译库
tools-probe-scripts-deletable     一次性探测脚本、镜像重打包脚本
```

## A. App 侧（`apps-tiny-container-v423-source` / 构建副本）

| 文件 | 我们的改动 |
|---|---|
| `app/src/main/java/com/fct/tc4/ui/page/ContainerMainFragment.kt` | 第 150 行附近 `ServerProfile` 里加 `fZoomLocked = false`（**V1 的唯一功能改动**，必须保留） |
| `app/src/main/java/com/fct/tc4/ui/page/SettingsViewModel.kt` | `refresh()` 里新增 `ActionSetting("dev_options_phantom", …)` |
| `app/src/main/java/com/fct/tc4/ui/page/SettingsFragment.kt` | `handleAction()` 新增 `"dev_options_phantom"` 分支，跳 `Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS` |
| `app/src/main/res/values/strings.xml`、`values-zh-rCN/strings.xml` | 新增 `tc4_settings_dev_options_title` / `_desc` / `_failed` 三条 |
| `app/src/main/java/com/fct/tc4/ui/misc/Global.kt` | **V4**：新增 `builtInImageStamp` / `readBuiltInImageStamp()` / `isBuiltInImageOutdated()`（镜像指纹） |
| `app/src/main/java/com/fct/tc4/ui/main/MainActivity.kt` | **V4**：`onCreate` 里加「镜像过期 → `askReimportImage()`」判断；新增 `askReimportImage()`（三选一对话框）与 `onNormalLaunchContinue()` |
| `app/src/main/java/com/fct/tc4/ui/page/ContainerManageViewModel.kt` | **V4**：新增 `applyImagePatch()`（解压覆盖包，不删容器）；`autoInstallBuiltInContainer()` / `confirmInstall()` / `startBuiltInImport()` 里维护 stamp 与 `installedContainers` |
| `app/src/main/java/com/fct/tc4/ui/page/ContainerMainViewModel.kt` | **V4**：`setupEnvironment()` 里注册 `OskBridge.summon = { Global.sendCommand("/usr/local/bin/tiny-osk-toggle") }`，`onCleared()` 里置 null |
| `app/src/main/java/com/fct/tc4/ui/page/ContainerMainFragment.kt` | **V4**：`createVncIntent` 之后加 `intent.putExtra("tc4.osk_trigger", filesDir/tmp/.tiny_osk_toggle)` |
| `app/src/main/res/values/strings.xml`、`values-zh-rCN/strings.xml` | V4 再加 `tc4_reimport_title/_message/_patch/_confirm/_later` 五条 |
| `app/src/main/assets/rootfs.stamp` | **新增文件**，内容是镜像指纹（当前 `v4-d222bfa6580997c3`），换镜像必须同步改 |
| `app/src/main/assets/rootfs.patch.tar.zst` | **新增文件**，只含 267 个新增/改动文件的覆盖包，`applyImagePatch()` 用它 |

其余 App 文件**全是上游原文件**，上游更新时直接覆盖。

## B. AVNC 分支（`avnc-upstream-fork-deletable`）

上游是 `https://github.com/tiny-computer/avnc`，锁定 commit `030e6c0`（= jitpack 版本号 `030e6c032e`）。
我们改了 18 个文件、新增 5 个。**行号一律以 V3 交付时的状态为准。**

（V3 相对 V2 只多改了一处：`Dispatcher.doOpenRemoteOsk()` 里加了三指开关判断。）

修改：
- `app/build.gradle` —— 关闭 cmake，改用预编译 `jniLibs`；版本号 **`3.2.2-tc4v6`**（V4 交付值）；加本地 maven 发布仓库
- `gradle.properties` —— 加 `android.overridePathCheck=true`、`org.gradle.vfs.watch=false`
- `app/src/main/java/com/gaurav/avnc/util/AppPreferences.kt` —— `Input` 内新增 9 个偏好键；
  `Gesture.tap3` 默认值 `"none"` → `"open-osk"`
- `.../ui/vnc/input/PointerAcceleration.kt` —— 加速曲线参数化（min/max 可调）
- `.../ui/vnc/input/PointerModes.kt` —— `deltaPerScroll` 改为按 `scrollSpeed` 计算；加速开关判断
- `.../ui/vnc/input/Dispatcher.kt` —— 新增 `onZoomMisTouchHint()`、`nudgePointer()`、`doOpenRemoteOsk()`
- `.../ui/vnc/input/InputHandler.kt` —— 转发 `nudgePointer()` / `sendKeySym()`
- `.../ui/vnc/input/TouchHandler.kt` —— 缩放误触二次确认逻辑（`ZOOM_CONFIRM_WINDOW_MS = 1200L`）
- `.../ui/vnc/gl/Cursor.kt` —— 指针缩放 `scale`
- `.../ui/vnc/gl/Program.kt`、`Shaders.kt` —— 新增 `u_Tint` uniform 与 `setTint()`
- `.../ui/vnc/gl/Renderer.kt` —— 每帧设置 `cursor.scale` 与 tint
- `.../ui/vnc/VncActivity.kt` —— 缩放提示浮层、**单个 40dp 跟随指针的键盘按钮**
  （`positionOskButton()` + 100 ms `oskFollowTick`，V4 起九宫格与右侧常驻按钮都已删除）、
  `openRemoteKeyboard()` 三条召唤路径
- `res/values/strings.xml`、`values-zh-rCN/strings.xml`、`res/values/arrays.xml`、
  `res/values/styles.xml`、`res/xml/pref_input.xml` —— 新增设置项与帮助文案
- `app/roomSchema/...7.json` —— 构建时自动生成，非手改

新增：
- `app/src/main/java/com/gaurav/avnc/ui/prefs/SwitchPreferenceEx.kt`（带帮助按钮的开关）
- `app/src/main/java/com/gaurav/avnc/ui/prefs/ColorPreference.kt`（取色器）
- `app/src/main/res/layout/view_zoom_hint.xml`
  （**注意**：`view_osk_ring.xml` 在 V4 已删除，不要再加回来）
- `app/src/main/java/com/gaurav/avnc/ui/prefs/ValueLabelPreference.kt`（滑块显示「加速 6 倍」这类数值标签）
- `app/src/main/java/com/gaurav/avnc/util/OskBridge.kt`（让宿主 App 注册「召唤容器内键盘」的回调）
- `res/values/attrs.xml` 里新增 `<declare-styleable name="ValueLabelPreference">`
- `app/src/main/jniLibs/<abi>/libnative-vnc.so`（从官方 AAR 提取，**不要重编**）

## C. 镜像侧（重打包进 `assets/rootfs.tar.zst`）

由 `tools-probe-scripts-deletable/build_rootfs_v2.py` 生成，改了三处、加了 263 个文件：
- `home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml` —— plugin-2 由 tasklist 改 docklike
- `.../xfce4-keyboard-shortcuts.xml` —— 增加 `XF86Launch0` → `tiny-osk-toggle`
- `opt/tiny/export.sh` —— 删掉 `apt clean` 与两条 `rm -rvf`（保留 `cd /` 与 tar）
- 剪贴板历史快捷键：`<Super>v` → `xfce4-popup-clipman`，
  `<Super><Shift>v` → `xfce4-clipman-history`（在同一个 shortcuts xml 里）
- 新增：六个 deb 的全部文件、`usr/local/bin/tiny-osk`、`tiny-osk-toggle`、
  `usr/local/share/tiny-osk/tiny_osk.py`、autostart 项（含
  `tiny-clipman.desktop`）、`docklike-2.rc`
- `tiny_osk.py` 源文件在 `tools-probe-scripts-deletable/osk/tiny_osk.py`，改完必须重新跑
  `build_rootfs_v2.py` + `zst_tar.py` 才会进镜像。它的配置写在容器的
  `~/.config/tiny-osk.conf`（键：`layout` / `placement` / `key_height` / `opacity`）。

## D. V5 新增/改动（**已被 V6 移除，仅作历史参考**）

### App 侧（tiny_container）

| 文件 | 改动 |
|---|---|
| `ui/main/MainActivity.kt` | 原来的三选一对话框不再弹；`if (Global.installedContainers.isNotEmpty() && Global.isBuiltInImageOutdated()) autoPatchImageIfOutdated()`。函数体 `if (autoPatchStarted) return` 后调 `containerViewModel.applyImagePatch()`。`askReimportImage()` 保留作手动入口 |
| `ui/page/ContainerMainFragment.kt` | 除了 `tc4.osk_trigger`，再传 `tc4.osk_caret`（`filesDir/tmp/.tiny_osk_caret`） |

### AVNC 侧（`3.2.2-tc4v9`，已废弃）

| 文件 | 改动 |
|---|---|
| `res/xml/pref_input.xml` | **V5 最重要的修复**：恢复官方 `pref_mouse` / `pref_vk` / `pref_km` 三个分类。`PrefsActivity.kt` 对这 11 个 key 做了 `!!`，缺一个就 NPE、整页打不开 |
| `ui/vnc/VncActivity.kt` | 新增字段 `oskCaretPath` / `oskCaretStamp` / `oskCaretRect`；`onCreate` 读 extra `tc4.osk_caret`；新增 `readCaretRect()`（按 mtime 缓存，一行 `visible x y w h`）；`positionOskButton()` 改为以光标右下角为锚点，无光标时按钮 `GONE` |

### 镜像侧（`build_rootfs_v2.py` 多产出 4 个文件 + 改 1 个）

| 路径 | 说明 |
|---|---|
| `usr/local/share/tiny-osk/hk_layout.py` | 由 `gen_hk_layout.py` 从 hackerskeyboard 源码生成的键位表 |
| `usr/local/share/tiny-osk/tiny_osk_caret.py` | AT-SPI + X11 取光标位置，写 `/tmp/.tiny_osk_caret` |
| `usr/local/bin/tiny-osk-caret` | 上面那个脚本的启动器（带 DISPLAY 猜测与单实例保护） |
| `home/tiny/.config/autostart/tiny-osk-caret.desktop` | 开机自启光标桥 |
| `home/tiny/.config/xfce4/panel/docklike-2.rc` | `pinned=` 清空（用户要求不预固定任何程序） |

### 重做黑客键盘移植的完整命令链（V6 起不再使用）

```powershell
# 1) 生成键位表（读 hackerskeyboard 的 res/xml 与 res/values）
python tools-probe-scripts-deletable/gen_hk_layout.py
# 2) 把 xkb keysym 补丁打进 tiny_osk.py（已应用过就跳过）
python tools-probe-scripts-deletable/patch_osk_hk.py
python tools-probe-scripts-deletable/patch_osk_hk2.py
# 3) 重打包镜像（三份产物必须一起换：rootfs.tar.zst / rootfs.patch.tar.zst / rootfs.stamp）
python tools-probe-scripts-deletable/build_rootfs_v2.py cache\rootfs-plain.tar cache\rootfs-v6.tar
python tools-probe-scripts-deletable/make_patch_tar.py cache\rootfs-plain.tar cache\rootfs-v6.tar cache\rootfs-patch-v6.tar
python tools-probe-scripts-deletable/zst_tar.py cache\rootfs-v6.tar cache\rootfs-v6.tar.zst 19 4
python tools-probe-scripts-deletable/zst_tar.py cache\rootfs-patch-v6.tar cache\rootfs-patch-v6.tar.zst 19 4
```

### 黑客键盘源码参考位置

- 上游：`refs-reference-assets-deletable/hackerskeyboard/`（`klausw/hackerskeyboard`，`--depth 1`）
- 键位 XML：`app/src/main/res/xml/kbd_{full,compact,symbols,symbols_shift}.xml`
- 键码常量：`app/src/main/res/values/keycodes.xml`（全是负数码，映射见 `gen_hk_layout.py` 的 `HKCODE_TO_KEYSYM`）
- 标签/上档字符：`app/src/main/res/values/donottranslate-keymap.xml`
- **坑**：HK 的 XML 用 `xmlns:android="http://schemas.android.com/apk/res-auto"`（自己的 attrs），
  不是 `res/android`；按 `res/android` 解析会得到全空的键位表。


## E. V6 改动（当前基线：键盘全部移除）

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
$env:PYTHONPATH="$PWD\tools-probe-scripts-deletable\pyz2"
python tools-probe-scripts-deletable/build_rootfs_v2.py cache\rootfs-plain.tar cache\rootfs-v7.tar
python tools-probe-scripts-deletable/make_patch_tar.py cache\rootfs-plain.tar cache\rootfs-v7.tar cache\rootfs-patch-v7.tar
python tools-probe-scripts-deletable/zst_tar.py cache\rootfs-v7.tar cache\rootfs-v7.tar.zst 19 4
python tools-probe-scripts-deletable/zst_tar.py cache\rootfs-patch-v7.tar cache\rootfs-patch-v7.tar.zst 19 4
# 版本戳（无 BOM！）
[System.IO.File]::WriteAllText("assets\rootfs.stamp", "v6-2c671cf642cd8313", (New-Object System.Text.UTF8Encoding $false))
```

产出：`rootfs-v7.tar` 2,683,729,920 字节 → `.zst` 732,826,915（sha `2c671cf642cd8313`）；
增量包 546,965 字节（sha `caeb4e317afec5d7`，262 个成员 = 3 patched + 259 new）。

## 判断「哪些必须保留」的一句话规则

> 只要文件在本文档出现，就用**我们的版本**；没出现的，一律用**上游新版本**。
> 上游若改了同一个文件，用 `git diff` 只挑我们的那几行重新贴到新版上，不要整文件覆盖。
