# 04 历史调研与被否决的方案（只作参考，不要照做）

> ⚠️ **这篇是历史档案。** 里面大部分内容已经在 V2~V6 实现了，
> 少数方案被用户当场否决。**不要按这篇去写代码**，要改东西看
> `spec-changes-and-rootfs.md`（现状）和 `log-version-history.md`（哪版做了什么）。
>
> 保留它的原因：这些调研结论都是**实际读源码 / 实际解包镜像 / 实际验过官方包**得出的，
> 以后要重新讨论同类需求时，不用从头查一遍。

---

## 1. 用户提过哪些需求（原始清单，m00917 + m01384）

按用户原话归纳，共 7 组：

1. **鼠标加速**：手机触屏拖动鼠标太费劲，要「笔记本触控板」那种加速。
   位置指定在：设置 AVNC → 输入 → 「调节灵敏度」滑块**下面**，带 `?` 说明，**默认勾选**。
2. **鼠标颜色 + 大小**：给画板 + 标准色（粉色排第一），大小默认 **150%**，可自己调。
3. **Windows 化的 Linux**：Firefox 要能「固定到任务栏」（现在没这个右键项）；
   想要更多实用定制；问「别人有没有把 Windows 习惯搬到 Linux 的开源项目，直接抄源码」。
4. **版本问题**：我这个 Linux 到底是什么发行版？为什么不是「原生」的？为什么装很多软件用不了？
5. **缩放误触**：双指放大有时是误触，希望第一次只弹提示，短时间内第二次才真放大。
6. **数据保存**：火狐账号同步不好用，想把火狐配置 / 容器快照塞进 APK；
   以及「导出容器会不会丢数据」。
7. **项目文件管理规范**：全英文命名、标可删除、`<5字符专业前缀>-<说明>-<权限>`。

另有 m01384 的补充决策：性能（GPU）能不能开、能不能加一个「跳转到开发者选项」的按钮
（因为每次都要手动开「停止限制应用子进程」才能用）、Ctrl+C/V 不要了、
键盘要「光标旁浮出」而不是固定区域、**绝对禁止双击触发**。

---

## 2. 关键调研结论（都已落地，记录依据）

### 2.1 鼠标加速 —— AVNC 早就写好了，只是没有开关

不是「要不要移植」，是「要不要给开关」。

- `PointerAcceleration.kt`（上游 133 行）是 libinput 风格三段曲线：
  慢速段线性、中速段系数 1.0、快速段 `0.0005 * v² / 80 + 1`；
  系数夹在 `0.3 ~ 3.5`，阈值 `THRESHOLD1 = 10` / `THRESHOLD2 = 80`（单位 **mm/s**，用屏幕 DPI 换算）。
- 生效点在 `PointerModes.kt` 的 `if (accelerate) { accelerator.compute(); adx = ...; ady = ... }`。
- **默认就是开着的**（只有触控板 / 相对模式才走加速，而 AVNC 默认手势就是 `touchpad`），
  但设置里没有任何开关 —— 这就是用户「不知道有没有」的原因。
- 最终落地：加了开关 + 强度 1~8（`strengthToMaxFactor`，6 = 3.5 = 上游值）+
  慢速基速 10~100%（映射 `MIN_FACTOR`）+ 滚轮档位 1~9。
  `?` 说明复用了 AVNC 自带的 `help_btn` 机制（原本只支持 `ListPreferenceEx`，
  所以新写了 `SwitchPreferenceEx`）。

### 2.2 光标颜色 / 大小 —— 不用碰原生代码

- **大小**：`Cursor.kt` 的 `update()` 里宽 / 高 / 热点各乘一个系数（纹理是 `GL_LINEAR`，
  放大不会糊成方块）。默认 1.5 = 150%。
- **颜色**：AVNC 自绘光标在 `cpp/Cursor.h` 里是**纯白 + alpha**（`0x00FFFFFF`），
  所以片元着色器乘 tint 就能整体染色，不影响其他画面元素。
  → `Shaders.kt` 加 `uniform vec4 u_Tint;`，`Program.kt` 加 location + setter，
  `Renderer.kt` 画光标前设色、画完复位。
- **重要修正**：V4 发现「纯黑填充」的光标乘色后仍是黑的，改成**亮度映射**染色
  （用亮度决定色相强度）才解决了「用户选粉色但光标还是黑的」。
- **取色器**：`ColorPreference` 自绘（12 个标准色 + 系统 HSV 面板），粉色放第一个。
- 限制：只影响 **AVNC 自绘的光标**。若远端把光标烤进画面（多数 XFCE 桌面不会），改不了。

### 2.3 缩放防误触

- 现状：`TouchHandler.kt` 的 `SwipeVsScale` 只在「双指角度差 > 45°」时判定为缩放，
  一旦成立就直接放大，没有确认环节。
- 落地：第一次 `onScaleBegin` 不缩放，屏幕中央弹半透明灰字提示，
  `ZOOM_CONFIRM_WINDOW_MS = 1200L` 内再次触发才放行。
- 按用户要求：**时长和文案先固定，不做成设置项**（减少选项）。

### 2.4 「固定任务栏」为什么没有，怎么解决的

- 上游面板只有 1 条，插件顺序：whiskermenu（开始菜单）、目录菜单、**tasklist**、
  工作区切换、托盘、音量、通知、时钟、显示桌面。
- **XFCE 自带的 `libtasklist.so` 没有「固定」功能**（扫字符串只有内部的
  `xfw_window_is_pinned`）。所以 Firefox 图标右键找不到「固定」，是上游设计如此，不是坏了。
  XFCE 里「固定」是独立 `launcher` 插件的行为。
- 优秀案例：**`xfce4-docklike-plugin`**（Debian trixie 0.4.3-1，arm64 95,260 字节）
  ——「所有窗口按应用归组为一个图标，可钉住当启动器」，就是 Windows 任务栏等价物，
  右键有 **Pin to Dock**。
- **已验证 13 个 `Depends` 库在镜像里全都有**（libgtk-3 / libxfce4panel / libxfce4ui /
  libxfce4windowing / libwnck / libxi …），所以只把 `libdocklike.so` + `docklike.desktop`
  塞进镜像即可，**完全离线、不用 apt**。
- 真实 rc 格式（读上游 `nsz32/docklike-plugin` 源码确认）：
  `~/.config/xfce4/panel/docklike-<id>.rc`，组 `[user]`，`pinned=` 是 GKeyFile 列表。
  V6 里 `pinned=` 已按用户要求清空（他说「任务栏固定那 3 个东西你就不要给我管了」）。

### 2.5 「Windows 习惯」的缺口清单

| 需求（Windows 习惯） | 当时的现状 | 处理 |
|---|---|---|
| 任务管理器（Ctrl+Shift+Esc） | 快捷键绑了 `xfce4-taskmanager`，但**没装** | V2 装上了 |
| 截图（Print） | 快捷键绑了 `xfce4-screenshooter`，但**没装** | V2 装上了 |
| 剪贴板历史（Win+V） | **没有** | V2 装 clipman；V3 补 `Super+V` / `Super+Shift+V` 与自启 |
| 窗口阴影 / 动画 | 没装 `picom` | 未做（用户没要） |
| 显示桌面按钮 | 已有 showdesktop | 保留 |
| 窗口按钮布局 | 已是 `icon,menu:minimize,maximize,close` | 已是 Windows 顺序，不用改 |

> clipman 的 deb 自带 autostart 是 `Hidden=true`，不会自启，必须自己补一条
> `home/tiny/.config/autostart/tiny-clipman.desktop`。这一点当时踩过。

### 2.6 「为什么装了很多软件用不了」

见 `spec-changes-and-rootfs.md` B1。核心一句：proot 是用户态系统调用翻译，
不是虚拟机也不是内核容器 → 没真 root、没 systemd、不支持 mount / 内核模块 / loop / tun-tap，
Wine、Docker、Wireshark 混杂模式基本不可能，Chrome / Electron / VS Code 必须关沙箱。
**最好的心智模型是「带 apt 的应用运行环境」，不是「完整 Linux」。**

### 2.7 性能 / GPU（用户问过能不能加速）

镜像的 `.tiny.yaml` 里**已经内置 GPU 选项组**，只是默认全关：
`Virgl 加速`（`GALLIUM_DRIVER=virpipe` + `virgl_test_server`，**VNC 下可用、安全**）、
`Adreno GPU 加速`（Turnip+Zink / Freedreno 四选一，**只适用于 Termux:X11，VNC 下别开**）。
App 的「选项配置」页勾选即可，**不需要改代码**。jniLibs 里已带
`libvirglrenderer.so` / `libepoxy.so` / `virgl_test_server`。

### 2.8 「停止限制子进程」按钮

- 痛点：安卓 12+ 的 **Phantom Process Killer** 限制单个应用 fork 子进程数（>32 个就杀）。
  proot 容器会 fork 一堆进程，所以约 10 秒后整个 Linux 被杀。
- 官方解法：开发者选项 →「停止限制应用子进程的系统资源用量」；
  或 `adb shell settings put global settings_enable_monitor_phantom_procs false`。
- App 侧只能「跳过去」，不能自己改：`AndroidManifest.xml` 里**没有**
  `WRITE_SECURE_SETTINGS`，且该权限只能 `adb shell pm grant` 授予。
- 落地：设置页加一条 `dev_options_phantom`，`startActivity(Intent(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS))`。
  原来的 `Signal9Activity`（error code 9 那个页面）只有说明文字，**没有**跳转按钮。

---

## 3. 被否决 / 已取消的方案（别再提）

### 3.1 把手机容器快照打进 APK —— 用户 m00917 亲自取消

- 技术上是**可行**的：导出/导入全链路没有任何完整性校验，镜像里 `.tiny.yaml` 存在就
  可以直接当内置镜像用；`tar` 里的 `.tiny.yaml` 决定安装行为。
- **但实际做了会毁用户数据**：`/opt/tiny/export.sh` 打包前会 `apt clean` 并
  `rm -rf ~/.mozilla`、`~/.cache`、`~/.gnupg`、`~/.bash_history` 之类。
  也就是说「导出」这个动作本身就会在真机上删掉东西。
- 结论：方案弃用。V2 改成了**修 `export.sh`**（去掉那些破坏性删除行），
  以后用户自己导出就自带浏览器数据，不用每次找我们。
- 火狐配置直接塞镜像的做法也**没做**（用户说以时间和效率为主，且他不想学命令）。

### 3.2 Ctrl+C / Ctrl+V 移植 —— 需求本身建立在误解上

- Linux GUI 程序的标准复制粘贴**本来就是 Ctrl+C / Ctrl+V**（Thunar、Mousepad、Firefox 都是）。
- 唯一「看起来失灵」的是**终端**：终端把 Ctrl+C 定义为中断，所以复制粘贴是
  **Ctrl+Shift+C / Ctrl+Shift+V**（POSIX 从 1970 年代就这样）。
- 想让终端也用 Ctrl+C/V → 就没法中断程序（Ctrl+C 停不掉死循环），二选一，不能两全。
- 用户 m01384 直接取消了这个任务（「把这个任务撤离就行，建议也不要了」）。
  **已实现的部分（如果有）不需要保留为开关。**

### 3.3 悬浮键盘 / 黑客键盘移植 —— 用户 m03615 全部叫停

这是投入最大、最后被砍的一块。整个过程值得记下来，避免下次重复踩坑：

**当时的能力盘点（实测，镜像内）**
- 有：`python3` 3.13.5、`python3-gi` 3.50.0、GTK3 typelib（Gtk-3.0 / Gdk-3.0 / Pango /
  GdkPixbuf）、`libXtst.so.6` + `libX11.so.6`（`ctypes` 调 `XTestFakeKeyEvent` 就能发按键）、
  `libxkbfile` / `xkbcomp` / `xmodmap`。
- 没有：`onboard` / `xvkbd` / `florence` / `matchbox-keyboard`；
  onboard 还缺 `python3-cairo`、`python3-dbus`、`gir1.2-atspi-2.0` 一串依赖。

**当时的结论**
- 方案 A（采用）：不装 onboard，自己写 Python3-GTK3 键盘，粉色主题、圆角按键，
  用 `ctypes` + `libXtst` 发键（零新依赖、纯离线）。约 1200~1800 行。
- 方案 B（不推荐）：装 onboard + 补 6~8 个 deb。省事但外观不受控、依赖链长。

**触发方式的三个候选**（用户要「光标旁浮出」，且禁止双击）
| 方案 | 做法 | 结论 |
|---|---|---|
| A1 常驻小把手 | 屏幕边缘一个 20×60 粉色半透明小条 | 100% 可靠但一直存在 |
| A2 自动淡出 | 同上，10 秒不动缩成 6px 细线 | 当时推荐这个 |
| A3 真·焦点检测 | 装 AT-SPI 监听 focus 事件 | 依赖重、对 GTK3 应用不稳 |

后来用户改成：**三指轻点** + **光标周围 8 方向按钮环**，两个独立开关、可同时开。

**实际做出来了什么（V2~V5）**
- V2：粉色 GTK3 键盘 `tiny_osk.py`（可拖动 / 可停靠 / 双布局 / 自启）+ 九宫格召唤按钮
- V3：加「设置」按钮 + `~/.config/tiny-osk.conf`（`layout` / `placement` / `key_height` / `opacity`）
- V5：移植 Hacker's Keyboard 键位表 + 键盘按钮改为跟随**文本光标**（AT-SPI，
  `ctypes` 调 `libatspi.so.0`，失败回退到活动窗口矩形，通过 `/tmp/.tiny_osk_caret` 传坐标）
- **V6：全部移除。** 用户原话：「键盘我还是不让你写了吧…你直接把你写的涉及键盘的所有代码都移除掉，
  恢复到最初 V2 版本的状态」，其他功能全部保留，作为定稿。

**踩过的坑（以后重做还会遇到）**
1. Hacker's Keyboard 的 XML 用自己的命名空间
   `xmlns:android="http://schemas.android.com/apk/res/android"` 是**错的**，
   它实际是 `http://schemas.android.com/apk/res-auto`，用真命名空间解析会得到空表。
2. AT-SPI 对 GTK3 应用经常不可靠，必须有「活动窗口矩形」兜底。
3. GTK 窗口的「停靠」只是 `resize()` + `move()` 到屏幕下方，不是真的 WM 停靠。
4. 内置 Python 无 pip 可用（离线），所有依赖必须走 apt 或 `ctypes`。

### 3.4 光标旁「九宫格」按钮 —— V4 改为单个跟随按钮

- 原始设计：指针周围 3×3 八个方向的按钮环，靠近屏幕边缘要自动避让。
- 实际问题：太挤、误触率高。
- V4 改为：单个 40dp 按钮，每 100ms 刷新一次跟随指针，靠近边缘时翻到另一侧。
- V6 随键盘一起删除。

---

## 4. 早期「工程结构」结论（命名规范的来源）

用户 m00917 定的命名规则，落地情况：

| 原目录 | 现名 | 删除权限 |
|---|---|---|
| `Linux-小小容器` | `build-env-toolchain` | 主体保留 |
| `tiny_container-优秀案例1` | `apps-tiny-container-v423-source` | 保留（基线对照） |
| `_tools` | `tools-probe-scripts-deletable` | 可删 |
| `_refs` | `refs-reference-assets-deletable` | 可删 |
| `avnc-fork` | `avnc-upstream-fork-deletable` | 可删（但改过的代码已进 git） |

`build-env-toolchain/` 的子目录：`jdk21-runtime-deletable`、
`sdk-android-platform-tools-deletable`、`gradle-home-cache-deletable`、
`cache-downloads-deletable`、`out-apk-keep-forever`、
`ws-gradle-build-copy-deletable`、`apks-archive-keep-forever`。
`黑客键盘-优秀案例2` 未改动（名字里写了禁止改名）。

---

## 5. 早期给用户的 4 个待决问题（已全部有答案，留档）

1. AVNC 要不要重编译？ → **要**，已做（Kotlin 重编 + 复用官方 `.so`），见 `spec-changes-and-rootfs.md` A2。
2. 任务栏方案？ → **docklike 替换 tasklist**，V6 起不预置固定项。
3. 实用工具要不要烤进镜像？ → **要**，任务管理器 / 截图 / 剪贴板都已烤进去。
4. 火狐数据要不要打进 APK？ → **不要**（见 §3.1，改为修 `export.sh`）。
