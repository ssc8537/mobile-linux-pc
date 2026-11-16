# 第二轮功能规划（讨论稿）v1

> 本文档是**讨论稿**，等用户确认后才进入编码阶段。
> 技术结论全部来自实际读源码 / 读镜像，不是猜测。

---

## 0. 本轮结论速览

| 需求 | 可行性 | 改动位置 | 风险 |
|---|---|---|---|
| 鼠标加速开关 + 强度自定义 | ✅ 现成引擎，只需接线 | AVNC `PointerAcceleration.kt` / `PointerModes.kt` / `pref_input.xml` | 低 |
| 慢速指针速度自定义 | ✅ 一个常量变设置 | 同上 `MIN_FACTOR` | 低 |
| 滚轮每格行数自定义 | ✅ 一个常量变设置 | `PointerModes.kt:deltaPerScroll` | 低 |
| 鼠标颜色（画板+标准色，粉色优先） | ✅ 加 shader 染色 uniform | `Shaders.kt` / `Program.kt` / `Cursor.kt` | 中 |
| 鼠标大小，默认 150% | ✅ 纯 Kotlin 缩放 | `Cursor.kt` | 低 |
| 误触缩放二次确认 | ✅ 纯 Kotlin 计时器 + 居中提示 | `TouchHandler.kt` / `activity_vnc.xml` | 低 |
| Windows 风格任务栏（docklike）+ 固定 Firefox/Thunar/Mousepad | ✅ 插件直接塞进镜像，依赖 13 个库全部已有 | 镜像 `usr/lib/.../panel/plugins/` + `xfce4-panel.xml` | 中 |
| 任务管理器 Ctrl+Shift+Esc | ✅ deb 已可下（xfce4-taskmanager 1.5.8） | 镜像 | 低 |
| 剪贴板历史 Win+V | ✅ deb 已可下（xfce4-clipman-plugin 1.6.6） | 镜像 | 低 |
| Ctrl+C / Ctrl+V 开关 | ⚠️ 需求本身需要修正，见 §4 | — | 无 |
| Linux 内嵌「黑客键盘」悬浮键盘 | ✅ 可做，方案见 §6 | 镜像内新增 Python3-GTK3 小程序 | 高（工作量最大） |
| AI 交接文档 | ✅ 直接写文件 | `docs-ai-handover/` | 无 |

---

## 1. 鼠标三项（加速强度 / 慢速基速 / 滚轮行数）

AVNC 已内置 `PointerAcceleration.kt`（libinput 思路的三段曲线），只是**没有开关也没有可调项**。

现有常量（`avnc-upstream-fork-deletable/app/src/main/java/com/gaurav/avnc/ui/vnc/PointerAcceleration.kt`）：

```
MIN_FACTOR   = 0.3f   慢速时的比例（越小越慢）
MAX_FACTOR   = 3.5f   快速时的上限（越大加速越猛）
THRESHOLD1   = 10f    mm/s，慢速段结束点
THRESHOLD2   = 80f    mm/s，加速段起始点
BASELINE_FACTOR = 1f  中段基准
```

**改法**：这套常量改成读取偏好值，默认值 = 原作者的值（用户要求「默认保留作者的」）。
- 加速强度滑块 → 映射 `MAX_FACTOR`（3.5 → 1.0~8.0）
- 慢速基速滑块 → 映射 `MIN_FACTOR`（0.3 → 0.1~1.0）
- 两项都放在「输入」页，紧跟在「调节灵敏度」之后，配 `?` 帮助按钮

滚轮：`PointerModes.kt` 里
```kotlin
private val deltaPerScroll = 20F //For how much dx/dy, one scroll event will be sent
```
即「手指划 20 像素 = 滚轮转一格」。改成设置项后，「一次滚动几行」就是这个数字（20 → 5~60，数值越大越慢）。
> 说明：VNC 只能发「滚轮一格」，行数由远端应用自己决定，所以准确说法是「一格滚轮的触发距离」。效果上等价于 Windows 的「每次滚动行数」。

---

## 2. 鼠标颜色 / 大小

- **大小**：`Cursor.kt` 里 `RectF(x, y, x+width, y+height)`。乘一个缩放系数即可，纹理是 `GL_LINEAR`，放大会自动插值。默认 1.5（= 当前 150%）。
- **颜色**：AVNC 自绘光标在 `cpp/Cursor.h` 里是**纯白 + alpha**（`0x00FFFFFF`），所以在片元着色器里乘一个 tint 就能整体染色，不影响其他画面元素。
  做法：`Shaders.kt` 的 `FRAGMENT_SHADER` 加 `uniform vec4 u_Tint;`，`Program.kt` 加 uniform 位置 + setter，`Renderer.kt` 画光标前设色、画完复位。
- **调色板**：给 12 个标准色 + 一个系统取色器（Android 原生 `ColorPicker` 对话框自带 HSV 面板）。粉色放第一个。

> 注意：这只影响 **AVNC 自绘的光标**。如果远端把光标烤进画面（多数 XFCE 桌面不会），颜色改不了。

---

## 3. 误触缩放确认

现状：`TouchHandler.kt` 的 `SwipeVsScale` 已经判断「双指角度差 > 45° 算缩放」，但一旦判断成立就直接放大。

新逻辑（纯 Kotlin，`TouchHandler` 内）：
1. 第一次 `onScaleBegin` → **不缩放**，记 `pendingScaleAt = now`，屏幕中间弹提示（半透明背景 + 灰字）：`再缩放一次以确认（1.2 秒内）`
2. 1.2 秒内再次触发 → 正常缩放
3. 超时 → 清除标记

按用户要求：**时长和文案先固定，不做成设置项**，减少选项。

---

## 4. Ctrl+C / Ctrl+V —— 需要更正一下认知

用户的假设需要修正：**Linux GUI 程序的标准复制粘贴本来就是 Ctrl+C / Ctrl+V**，和 Windows 完全一样（Thunar、Mousepad、Firefox 都是）。不存在「Linux 不用这个」这回事。

真正会「看起来失灵」的只有一种场景：**终端里**。终端把 Ctrl+C 定义为「中断当前程序」，所以终端里的复制粘贴是 **Ctrl+Shift+C / Ctrl+Shift+V**。这是 POSIX 从 1970 年代就定下来的约定，不是缺陷。

结论：
- 桌面程序：**不需要任何开关，本来就是 Ctrl+C/V**
- 终端：可以让用户选「终端内也用 Ctrl+C/V 复制粘贴」——但那样就**没法中断程序**了（`Ctrl+C` 停不掉死循环）。这是二选一，不能两全。

**建议**：不做这个开关，改为在镜像里预置**终端快捷键说明**（贴一张 README 到桌面 + 终端欢迎语），并保留 XFCE 默认的 `Ctrl+Shift+C/V`。
请用户在 §9 确认。

---

## 5. Windows 习惯：任务栏 / 任务管理器 / 剪贴板历史

### 5.1 任务栏（docklike）
- 镜像里**没有** docklike，但依赖库 13 个**全部已在镜像内**（含 `libxfce4windowing-0.so.0.0.0`），所以把 `libdocklike.so` + `docklike.desktop` 直接放进镜像即可，**不需要联网 apt**。
- 默认布局：`docklike` 替换掉现在的 `tasklist`，默认固定 **Firefox / Thunar(文件管理器) / Mousepad(文本编辑器)** 三个。
- 用户要求：**默认开启**，但提供一个开关可以关掉（关掉就回退到经典 tasklist）。

### 5.2 任务管理器
- 镜像里**没有** `xfce4-taskmanager`，但 `xfce4-keyboard-shortcuts.xml` 里已经把 `Ctrl+Shift+Esc` 绑到了它 → 现在按下是「命令不存在」。
- 已确认可下载 `xfce4-taskmanager_1.5.8-1_arm64.deb`（117 KB）。

### 5.3 剪贴板历史
- 已确认可下载 `xfce4-clipman-plugin_1.6.6-1+b2_arm64.deb`（36 KB）。
- 实现「Win+V」：clipman 没有全局弹窗快捷键，需要额外做一个小脚本绑到 `<Super>v`，或者用一个轻量弹窗。**这块要单独确认**（见 §9）。

### 5.4 缺失工具的补齐清单（镜像内 + 快捷键已绑但没有程序）
`xfce4-screenshooter`（截图，已确认可下载 160 KB）也一并补上。

---

## 6. ★ Linux 内嵌「黑客键盘」悬浮键盘（最大的一个）

### 6.1 关键技术判断

镜像内已有的能力（已实测）：
- `python3` 3.13.5 + `python3-gi` 3.50.0 ✅
- GTK3 typelib `Gtk-3.0` / `Gdk-3.0` / `Pango` / `GdkPixbuf` ✅（可直接写 GTK3 界面）
- `libXtst.so.6` ✅ + `libX11.so.6` ✅ → 用 Python `ctypes` 调 `XTestFakeKeyEvent` **就能把按键送进 X 服务器**
- `libxkbfile.so.1` / `xkbcomp` / `xmodmap` ✅

镜像内**没有**的：`onboard` / `xvkbd` / `florence` / `matchbox-keyboard`，而且 onboard 还缺 `python3-cairo`、`python3-dbus`、`gir1.2-atspi-2.0` 等一串依赖。

**结论（推荐方案 A）**：不装 onboard，**自己写一个 Python3-GTK3 键盘**。
- 界面：GTK3，粉色主题，圆角按键
- 发键：`ctypes` + `libXtst` 的 `XTestFakeKeyEvent`（零新依赖，纯离线）
- 布局：按用户给的黑客键盘布局（5 行主区 + 右侧小键盘 + F1~F12 排）

**方案 B（不推荐）**：装 onboard + 补 6~8 个 deb。省事但外观是 onboard 的，且依赖链长、字体/主题不好控制。

### 6.2 触发方式（用户说「光标出现时右边出现小按钮」）—— 这是最大的技术难点

X11 下判断「光标是否在文本框里」需要 AT-SPI（辅助功能总线）。镜像里 **`gir1.2-atspi-2.0` 缺失**，装上也经常对 GTK3 应用不可靠。

所以三个可选方案：

| 方案 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **A1** 常驻小把手 | 屏幕右侧边缘一个 20×60 的粉色半透明小条，点一下开键盘 | 100% 可靠，实现简单，随时可用 | 不「智能」，一直存在（可自动半透明） |
| **A2** 自动淡出 | 同上，但 10 秒不动就缩成 6px 的细线，点一下恢复 | 不挡视线 | 稍复杂 |
| **A3** 真·焦点检测 | 装 AT-SPI + 监听 `focus` 事件 | 最贴合用户描述 | 依赖重、不稳、可能失败 |

**建议 A2**。请用户在 §9 确认。

### 6.3 键盘形态（用户要求）
- **悬浮模式**：窄版，屏幕下半部悬空，顶部一条「≡ 拖动手柄」，可拖动、记住位置
- **固定模式**：占屏幕下方 2/5，按键更大，可放更多键
- 设置按钮 → 打开键盘自己的设置页（主题色、大小、布局、悬浮/固定、是否显示小键盘）
- 「传统键盘布局（全键盘）」一键切换：黑客键盘精简布局 ⇄ 全键盘（含 F1~F12、小键盘）

### 6.4 布局（按用户口述 + 照片，待编码时逐一核对）
主区 5 行 + 右侧独立小键盘区，键帽上第二功能（Shift 符号）全部按用户给的对照表实现。

### 6.5 工作量诚实评估
这是本轮**最大**的一块：约 1200~1800 行 Python + 若干资源文件，调试只能在真机上迭代。建议**单独作为一个里程碑**，先做出「能用」版本，再美化。

---

## 7. 一体机的痛点（用户问的）

用户是一体机（无键盘无鼠标，纯触屏）。真实痛点排序：
1. **没有 Esc / Tab / Ctrl / Alt / 方向键** → 这正是悬浮键盘存在的意义 ✅
2. **长按选词、右键** → 目前只能靠 AVNC 的「长按 = 右键」，够用
3. **没有滚轮** → 已由双指滚动 + §1 的滚轮速度解决
4. **没有 F1~F12** → 全键盘模式解决
5. **遮挡内容** → 键盘可拖动 + 固定/悬浮切换
6. **输入法** → 中文目前靠 fcitx5（镜像已装）；键盘本身只做英文，中文输入仍需 fcitx5，这条要跟用户讲清楚

---

## 8. AI 交接文档（结构）

放在 `docs-ai-handover/`，按用户要求「每个文件不要太长」拆成多份：
```
docs-ai-handover/
  00-index-read-me-first.md          索引 + 阅读顺序
  01-project-overview.md             项目是什么、目录地图
  02-upstream-vs-ours.md             官方原版 vs 我们的改动（逐文件 diff 说明）
  03-feature-catalog.md              我们加的功能清单（含代码位置）
  04-sync-upstream-guide.md          官方更新后如何合并（步骤化）
  05-user-habits-preferences.md      用户习惯/偏好（重要！）
  06-naming-conventions.md           命名规范（英文 + 可删除标记 + 5字符专业前缀）
  07-build-recipe.md                 编译环境与命令（含踩过的坑）
```
单文件控制在 ~300 行 / ~12 KB 以内（约 AI 长上下文的 85% 安全线），并做交叉引用。

---

## 9. 待用户决策（6 个问题）

1. **鼠标加速滑块的范围**：`MAX_FACTOR` 上限给到多少？（建议 1.0~8.0，默认 3.5）
2. **Ctrl+C/V**：确认按 §4 处理「不做开关，只加说明」吗？
3. **剪贴板历史 Win+V**：clipman 本身没有全局弹窗，是否接受「装 clipman + 额外一个小弹窗脚本」？还是先只装 clipman、用它的面板图标？
4. **键盘触发**：选 A1（常驻小把手）/ A2（自动淡出，推荐）/ A3（真焦点检测）？
5. **键盘里程碑**：是否同意「先做能用版 → 验收 → 再美化」？还是必须一次做到粉色美化版？
6. **镜像更新方式**：现有容器不会自动更新。是否加一个 App 内按钮「一键更新到新版镜像」（重新解压 rootfs，会清空用户数据）？还是只在新装时生效？

---

## 10. 明确不做 / 已取消

- ~~快照导出 + 火狐配置融进 APK~~ → 用户 2026-11-16 明确取消
- ~~Ctrl+C/V 系统级开关~~ → 见 §4，需求本身建立在误解上
- ~~上传代码到 GitHub~~ → 用户明确要求「等我命令」
