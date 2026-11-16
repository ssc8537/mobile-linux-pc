# 05 镜像内部结构速查（改镜像前读这篇）

> 这篇回答：**容器里长什么样，哪些配置文件改哪一行有用。**

## 系统身份

- 发行版：**Debian GNU/Linux 13 (trixie)**，`DEBIAN_VERSION_FULL=13.6`
- 桌面：XFCE 4.20.4 + xfwm4，GTK 3.24
- 浏览器：Firefox ESR 140.13.0esr
- 包数量：1147
- 内核串是 proot 伪造的：`Linux localhost 6.17.0-PRoot-Distro … aarch64`
- **不是完整 Linux**：proot 是用户态模拟，没有真正的 root、不支持 mount/内核模块、
  部分需要特权的软件（Wine、部分游戏、systemd 服务）跑不起来。这是用户遇到的
  「装了很多软件用不了」的根本原因，不是 App 的 bug。

## 用户与权限

- 主用户 `tiny`，uid/gid 1000（`--change-id=1000:1000`）
- 镜像文件属主统一 `10258:10258 aid_u0_a258`，安装时 App 会 `sed -i '/^aid_/d'`
  清掉 passwd/group 里的 aid 行再补自己的
- `sudo` / `pkexec` 在镜像里存在且是 4755（proot 内可用）

## 关键路径

| 路径 | 说明 |
|---|---|
| `.tiny.yaml`（tar 第一项） | 容器定义：`code: xfce`、启动命令、快捷命令、GPU 选项、lstat 缓存 |
| `/opt/tiny/export.sh` | 导容器的脚本，**V2 已修**（不再删 `~/.mozilla`） |
| `/opt/tiny/` | 字体、微信、亿图、CAJ、WPS 等预置素材 |
| `home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/` | 所有 XFCE 配置（面板、快捷键、主题、窗口管理器） |
| `home/tiny/.config/autostart/` | 自启项（现有 `tiny-clipman.desktop`；自定义键盘的项在 V6 已移除） |
| `~/.config/xfce4/panel/docklike-2.rc` | docklike 任务栏配置（固定项在这里） |
| `/公共` | 与安卓共享目录（对应 App 的 `filesDir/public`） |
| `/mnt/sdcard` | 安卓内部存储 |

## 改面板（最常用）

文件：`home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml`
- 有一个 `panel-1`，`position="p=8;x=678;y=596"`（底部），`size=32`，`plugin-ids` 13 个
- plugin 编号含义：12 whiskermenu、1 directorymenu、**2 docklike（V2 换的）**、
  3 分隔、4 pager、5 分隔、6 systray、11 脉冲音频、13 通知、7 分隔、8 时钟、
  9 分隔、10 显示桌面
- V1 时 plugin-2 是 `tasklist`（原版任务栏，**没有固定功能**）。
  上游 XFCE 的 tasklist 本身就不支持「固定」，固定是独立 `launcher` 插件的行为，
  真正的 Windows 式固定需要一个窗口分组插件 → 所以换了 docklike

## 改快捷键

文件：`home/tiny/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml`
- `commands.default` 放 `type="empty"` 占位，`commands.custom` 放真正命令
- V3 曾加过 `XF86Launch0` → `tiny-osk-toggle`，**V6 已删除**（键盘整体移除）。
  现在自定义的只有：`<Super>v` → `xfce4-popup-clipman`、`<Super><Shift>v` → `xfce4-clipman-history`。
- 原版有个坑：`Print` / `<Primary><Shift>Escape` 绑的是 `xfce4-screenshooter` 和
  `xfce4-taskmanager`，但**这两个软件原本没装**（按了没反应）。V2 已补装。

## 被删掉/没有的软件（用户可能会问）

`libreoffice`、`gimp`、`picom`、`xdotool`、`wmctrl`、`code`、`wine`、
`flameshot`、`copyq`、`rofi` —— 都没有。要的话通过 `.tiny.yaml` 的
`quick_commands` 里加一条一键安装，不要改 App 代码。

## GPU 加速（现成能力，只是默认关）

`.tiny.yaml` 里有 `图形加速` 选项组，包含 `Virgl 加速`（VNC 可用，安全）和
`Adreno GPU 加速`（Turnip+Zink / Freedreno，**只适用于 Termux:X11，VNC 下别开**）。
都在 `enabled: false`，App 的「选项配置」标签页里勾选即可，不需要改代码。
jniLibs 里已带 `virgl_test_server` 与 `libvirglrenderer.so`。

## 截图约束（给后续想美化的人的提醒）

容器内**不要装 GNOME/KDE 主题包**，XFCE 主题只需 GTK3 主题 + 图标主题放到
`~/.themes` / `~/.icons`。当前是 `Fluent-Light` + `Fluent` 图标。

## 键盘：V6 已整体移除（别再往回加）

用户在 m03615 明确要求「键盘不写了，全部删掉」，所以从 V6 起：

- 镜像里**没有** `usr/local/share/tiny-osk/`（`tiny_osk.py` / `hk_layout.py` / `tiny_osk_caret.py`）
- 镜像里**没有** `usr/local/bin/{tiny-osk,tiny-osk-toggle,tiny-osk-caret}`
- 没有对应的 autostart 与 `.desktop`，快捷键里也没有 `XF86Launch0`
- APK 里**没有** OSK 按钮、没有 `OskBridge`、没有 `tc4.osk_*` intent extra、
  没有「悬浮键盘」设置分类，三指轻选项回到仅 3 个官方选项

历史实现与排查方法见 `spec-changes-v2.md` 的 D 节（标了「已被 V6 移除」），
仅作参考，不要照它恢复。若将来真的要重做，先问用户，别自作主张。

**唯一保留的兼容代码**：`applyImagePatch()` 开头有一小段 `$BIN_DIR/rm -rf/-f`，
作用是在打增量包之前清掉旧版残留的键盘文件（否则从 V5 升上来会留一个
指向已删除程序的自启项，每次登录都报错）。这段是必要的，不要删。

## 镜像升级机制（V4 新增，务必理解）

`MainActivity` 原来只在 `installedContainers.isEmpty()` 时导入内置镜像 —— 覆盖安装
时旧容器还在，新镜像**永远不会**被解压。V4 的做法：

- `assets/rootfs.stamp` 存镜像指纹，`Global.builtInImageStamp` 存"已导入过哪个指纹"。
- 启动时两者不一致 → 弹三选一：
  - 只更新系统文件（`applyImagePatch()`，解压 `rootfs.patch.tar.zst` 到现有容器，
    **不删** `dataDir/<code>`）
  - 重新导入（`autoInstallBuiltInContainer()`，会 `deleteRecursively()`）
  - 以后再说（只更新指纹，不再提示）
- V5 起不再弹对话框：`autoPatchImageIfOutdated()` 直接静默调 `applyImagePatch()`。
  `askReimportImage()` 仍保留，作为手动重装的入口。
- 每次成功导入/覆盖后都要把 stamp 记进 SharedPreferences，否则每次启动都重跑。

这条机制是 V4 修掉"装了新版本但桌面功能全都没出现"的关键，改镜像时别忘了三个
assets 一起换（见 `build-make-apk.md` 第 6 节）。
