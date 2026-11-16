# 调研报告：把「小容器」改造成 Windows 手感的 Linux 桌面

> 本文件是讨论用的调研结论 + 待确认方案，**尚未开始改代码**。
> 所有结论都来自实际读取源码 / 实际解包镜像 / 实际抓到官方包的验证，不是猜测。

---

## 0. 当前工程结构（已按你的英文命名规则整理）

| 目录 | 作用 | 删除权限 |
|---|---|---|
| `apps-tiny-container-v423-source` | 小容器 App 原始源码（Kotlin） | 保留 |
| `avnc-upstream-fork-deletable` | AVNC 源码（正是 App 依赖的那个 commit `030e6c0`） | 可删 |
| `refs-reference-assets-deletable` | 参考用 AAR 等 | 可删 |
| `tools-probe-scripts-deletable` | 我写的解包/探测脚本 | 可删 |
| `build-env-toolchain/` | JDK21 / Android SDK / Gradle / 缓存 / 构建副本 / 输出 | 见各子目录 |
| `build-env-toolchain/out-apk-keep-forever` | 已交付的 APK + 签名证书 | 永久保留 |
| `黑客键盘-文件-禁止改名-优秀案例2` | 你放的文件（名字里写了禁止改名，我没动） | — |

新增目录将按同样规则命名，例如 `avnc-patch-workspace-deletable`、`docs-project-notes-keep-forever`。

---

## 1. 你这个 Linux 到底是什么

- 发行版：**Debian GNU/Linux 13（代号 trixie）13.6**，arm64。
  - 依据：镜像内 `usr/lib/os-release` → `PRETTY_NAME="Debian GNU/Linux 13 (trixie)"`、`VERSION_ID="13"`、`DEBIAN_VERSION_FULL=13.6`；`etc/debian_version` = `13.6`。
- 桌面：**XFCE 4.20.4**（面板 / 窗口管理器 xfwm4 / Thunar / whiskermenu 2.9.2）。
- 浏览器：Firefox ESR 140.13.0esr。
- 软件包总数：1147 个（dpkg status 统计）。
- 它不是 Ubuntu、也不是 Arch；Ubuntu 和发行版关系是「Ubuntu 基于 Debian」，你这个是原味 Debian。

### 关于「不是原生 Linux」
你的直觉是对的：它是 **PRoot 容器**里跑的 Debian。

- PRoot 用 ptrace 做「路径 / 系统调用的翻译」，不是虚拟机、也不是 Docker 那种内核级容器。
- 它伪造了内核版本串：`Linux localhost 6.17.0-PRoot-Distro ... aarch64`（这是假的，真实内核是安卓手机的）。
- 因此会有这些限制（也是「装了很多软件用不了」的根因）：
  - 没有真正的 root / 内核模块，不能装驱动、不能改内核参数；
  - 没有 systemd，靠 `service` 脚本 + 手动起 dbus 之类；
  - 不能跑 Docker / podman（嵌套容器），不能跑 VirtualBox；
  - 抓包（Wireshark 混杂模式）、VPN（tun/tap）、挂载 loop 镜像一般不行；
  - 沙箱型程序（Chrome / Electron / VS Code）必须关沙箱才能跑 —— 镜像里已经预置了 `MOZ_FAKE_NO_SANDBOX=1` 等环境变量和 `*-no-sandbox.desktop`；
  - ptrace 翻译有性能损耗（这也是它选 XFCE 而不是 GNOME 的原因）。

结论：**把它当「完整 Linux」用会有坑，当「带 apt 的应用运行环境」用体验最好。**

---

## 2. 鼠标加速 —— 好消息：AVNC 里面已经写好了

这不是「要不要移植」的问题，是「要不要给开关」的问题。

- 已有实现：[PointerAcceleration.kt](avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/input/PointerAcceleration.kt)（133 行），libinput 风格三段曲线：
  - 慢速段线性、中速段系数 1.0、快速段 `0.0005 * v² / 80 + 1`；
  - 系数夹在 **0.3 ~ 3.5**；阈值 `THRESHOLD1=10`、`THRESHOLD2=80`（单位是 **mm/s**，用屏幕 DPI 换算）。
- 生效点：[PointerModes.kt:169](avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/input/PointerModes.kt) 的 `if (accelerate) { accelerator.compute(); adx = ...; ady = ... }`。
- **它现在是默认开启的**：只有「触控板/相对模式」才走加速，而 AVNC 默认手势就是 `touchpad`。
- **但没有任何开关**，设置里也找不到 —— 这正是你觉得「不知道有没有」的原因。

所以这个功能要做的是「补一个开关」，而且可以顺手做成更好用的形态：
- 开关放在你说的位置：设置 AVNC → 输入 → 「调节灵敏度」滑块**正下方**；
- 右侧加 `?` 帮助按钮，点开显示说明（复用 AVNC 自带的 `help_btn` 机制，和「手势风格」那条一模一样）；
- 可选：再加一个「加速强度」滑块（把 MAX_FACTOR 从 3.5 调到 2～6），因为手机屏幕 DPI 差异大，固定值不一定顺手。

> 如果要「更接近 Windows 触控板」的手感，还可以把慢速段下限 0.3 提高到 0.5 左右（现在是慢速时指针变慢，有人不喜欢）。

---

## 3. 光标颜色 + 光标大小

都能做，而且**不需要动 C++ 原生代码**：

- **大小**：[Cursor.kt](avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/gl/Cursor.kt) 的 `update()` 里，宽 / 高 / 热点各乘一个缩放系数即可（纹理是 `GL_LINEAR` 放大，不会糊成方块）。默认值按你的要求设为 **1.5（=150%）**，设置里 0.8～3.0 可调。
- **颜色**：[Shaders.kt](avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/gl/Shaders.kt) 的片元着色器加一个 `u_Tint` uniform，[Program.kt](avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/gl/Program.kt) 里加对应的 location + `setUniforms` 重载，绘制光标时传入颜色；帧缓冲绘制时传白色（= 不变色）。
  - AVNC 自带的光标像素是「白色 + alpha」，乘色即精准变色；远端服务器发来的彩色光标会被整体染色（可接受，默认白色时不染色）。
- **取色器**：给一组标准色（**粉色排第一个**，按你的喜好），再给一个「自定义」——弹窗里 HSV/RGB 三个滑块 + 实时预览。这是一个自绘 `Preference` + 一个 layout，约 200 行。

---

## 4. 缩放防误触

- 现在的链路：双指缩放 → `ScaleGestureDetector` → [TouchHandler.kt:236](avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/input/TouchHandler.kt) 的 `onScale()` → `dispatcher.onScale` → `VncViewModel.updateZoom()`。代码里只有「Swipe 还是 Scale」的判定（角度差 > 45°），没有「确认」环节，所以碰一下就会放大。
- 方案（纯 Kotlin）：
  1. 第一次触发缩放时**不缩放**，在屏幕中央弹一条半透明灰字提示（比如「再次双指缩放以确认放大」）；
  2. 若在 N 毫秒（建议 1200ms）内再次开始缩放，则正常缩放，并在本次手势内放行；
  3. 提示用 `activity_vnc.xml` 里动态插入的 TextView（那个位置本来就是给提示留的注释），自带淡入淡出，不挡操作。
- 时长和文案都可以做成设置项，但我建议先固定，避免设置项过多。

---

## 5. 固定任务栏 / Windows 化

### 为什么现在没有「固定」
- 现在的面板只有 1 条，插件顺序是：whiskermenu（开始菜单）、目录菜单、**tasklist（任务栏）**、工作区切换、托盘、音量、通知、时钟、显示桌面。
- XFCE 自带的 `libtasklist.so` **没有**「固定到任务栏」这个功能（我扫了它的字符串，只有内部的 `xfw_window_is_pinned`）。所以你在 Firefox 图标上右键找不到「固定」，是上游设计如此，不是坏了。

### 现成的优秀案例（直接拿来用，不用自己写）
1. **`xfce4-docklike-plugin`** —— Debian 官方源里就有（trixie，0.4.3-1，arm64，93 KB）。
   - 功能原文：「所有窗口按应用归组为一个图标，可以钉住当作启动器」，就是 Windows 任务栏的等价物，右键有 **Pin to Dock**。
   - 我已经下载了这个 deb，并逐个核对了它的 12 个依赖：**全部已经在你的镜像里**（libgtk-3 / libxfce4panel / libxfce4ui / libxfce4windowing / libwnck / libxi …），所以只要把 `libdocklike.so` + `docklike.desktop` 放进镜像即可，不用联网装包。
2. **XFCE 官方自带的双面板模板**：`etc/xdg/xfce4/panel/default.xml` 就是一个「顶部菜单条 + 底部自动隐藏 dock」的 Windows 布局，连 `launcher` 插件的写法都有现成样例。
3. **主题**：你的镜像已经是 `Fluent-Light` + `Fluent` 图标（Win11 风格），这块其实已经到位；差的是窗口阴影 / 淡入淡出（`picom`，镜像里没装）。

### 建议的落地形态
- 面板改造：把 tasklist 换成 **docklike**，并预置 4 个固定项：Firefox、文件管理器、终端、文本编辑器（右键还能自己加/删）。
- 改的是 `home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml`，另外预生成 `~/.config/xfce4/panel/docklike-<id>.rc`（`pinned=` 列表）。
- 这一步**不写一行 App 代码**，纯粹是镜像配置文件 + 一个现成插件。

---

## 6. 「还有哪些实用定制」（按你的使用习惯推的）

我在镜像里查到几个「快捷键绑了、但工具没装」的缺口，正好补上就很 Windows：

| 需求（Windows 习惯） | 现状 | 建议 |
|---|---|---|
| 任务管理器（Ctrl+Shift+Esc） | 快捷键绑了 `xfce4-taskmanager`，但**没装** | 装 `xfce4-taskmanager` |
| 截图（PrintScreen） | 快捷键绑了 `xfce4-screenshooter`，但**没装** | 装 `xfce4-screenshooter`（或 flameshot，可标注） |
| 剪贴板历史（Win+V） | **没有** | `xfce4-clipman-plugin` |
| 窗口阴影 / 动画 | **没有**（picom 未装） | 装 `picom` + 轻量配置，观感立刻「现代化」 |
| 显示桌面按钮 | 已有（showdesktop 插件） | 保留 |
| 窗口按钮布局 | 已经是 `icon,menu:minimize,maximize,close` | 已经是 Windows 顺序，不用改 |

这些既可以**烤进镜像**（新装就是全套），也可以做成 App 里 **「一键安装」按钮**（`快捷方式` 页，你已经有的那种一键命令）。

---

## 7. 导出丢数据 / 火狐数据进 APK

- 你担心的没错：`/opt/tiny/export.sh` 在打包前会 `rm -rf` 掉 `~/.mozilla`、`~/.cache`、`~/.gnupg`、`~/.bash_history` 等，导出即毁数据。
- **我建议根本不用你敲命令**：直接在镜像里把 `export.sh` 里那些破坏性删除行去掉再打包。以后你导出容器，浏览器书签 / 密码 / 插件 / 历史全都在。
  - 对比一下：之前给你的 `sed` 方案要你在终端里敲 3 行；改镜像 = 你什么都不用做。
- 关于「火狐配置融进 APK」：
  - 可行：镜像里目前**没有** `home/tiny/.mozilla`（是空的新装状态），把导出的 `.mozilla` 目录追加进去即可，纯新增、不覆盖任何东西。
  - 但**效率上更推荐**：先用第 7 条修好 export.sh，以后你自己导出就带浏览器数据，不用每次都找我。
  - 如果你想要一次性的「开箱即用浏览器」，把 `.mozilla` 文件夹（或导出的 tar）给我，我在打包时塞进去。

---

## 8. 唯一的重活：必须重编译 AVNC

| 事项 | 说明 |
|---|---|
| 现状 | 小容器是通过 JitPack 用**现成的 AVNC AAR**（`com.github.tiny-computer:avnc:030e6c032e`），App 源码里没有 AVNC。 |
| 影响 | 鼠标加速开关、光标颜色/大小、缩放确认 —— 这三件事全在 AVNC 内部，**必须重新编译 AVNC**。 |
| 好消息 | AVNC 源码已经在你目录里，而且正好是这个 commit（`avnc-upstream-fork-deletable`）。 |
| 关键技术判断 | AVNC 的原生库（VNC 协议、libvncserver）在这个沙箱里**编不了**（CMake/ninja 会卡死，之前已验证）。但**不需要编**：官方 AAR 里已经带 `libnative-vnc.so`，我把它抽出来复用，只重编 Kotlin + 资源。 |
| 交付方式 | 编出新的 AAR → 发布到本地 maven 仓库 → 小容器改成依赖它（版本号 `030e6c032e-patched`）。 |
| 时间 / 风险 | 约 **30–60 分钟**，中等风险（要新下载 Gradle 8.13 + AGP 8.10.1，还要跑通 kapt/Room/dataBinding）。 |

---

## 9. 一件事要先说清楚：老容器不会自动变

- 新 APK **同签名**，可以直接覆盖安装，**App 数据和容器数据都不会丢**。
- 但「内置镜像只在『第一次安装且没有任何容器』时才解压」，所以升级 APK 后，**你手机上已有的那个桌面不会自动换上新的任务栏**。
- 两个解决办法（我建议都做）：
  1. 镜像里烤好新配置 → 以后重装/新设备开箱即用；
  2. 在 `快捷方式` 页加一个 **「一键切换 Windows 风格任务栏」** 按钮 → 现有容器点一下就变，**不用敲任何命令**，也不用重下 928 MB 镜像。

---

## 10. 待你拍板的 4 件事

1. **AVNC 重编译**：同意 / 先只做镜像部分 / 再想想。
2. **任务栏方案**：docklike 替换 tasklist（最像 Windows） / 只用 launcher 固定图标（改动最小） / 两个都做。
3. **实用工具**：任务管理器 + 截图 + 剪贴板 + picom 窗口特效，是否一起烤进镜像（还是只做一键按钮）。
4. **火狐数据**：这次要不要把你导出的 `.mozilla` 一起打进去。

---

## 附：改动清单预览（确认后执行）

**AVNC 侧（Kotlin/资源）**
- `pref_input.xml`：灵敏度滑块下插「鼠标加速」开关（带 `?`）
- 新增 `SwitchPreferenceEx.kt`（因为自带 `help_btn` 只支持 ListPreferenceEx）
- `AppPreferences.kt`：新增 `mouseAcceleration`（默认 true）、`cursorScale`（默认 1.5）、`cursorColor`、`zoomConfirmEnabled`
- `PointerModes.kt`：`if (accelerate && viewModel.pref.input.mouseAcceleration)`
- `Cursor.kt`：按 `cursorScale` 缩放
- `Shaders.kt` + `Program.kt`：新增 tint uniform
- `TouchHandler.kt` + `activity_vnc.xml`：缩放二次确认 + 居中提示
- `strings.xml` + `values-zh-rCN/strings.xml`：新增文案（中英）

**镜像侧（纯配置）**
- `xfce4-panel.xml`：tasklist → docklike，预置固定项
- 新增 `libdocklike.so` + `docklike.desktop` + `docklike-<id>.rc`
- `/opt/tiny/export.sh`：去掉破坏性 `rm`
- `.tiny.yaml`：追加「一键 Windows 任务栏」「一键安装常用工具」等 quick_commands
- 可选：预置 `home/tiny/.mozilla`（你的浏览器数据）
