import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

v1_extra = """
- 本版功能（一句话）：**自由缩放**。进入 Linux 图形界面后，左侧工具栏的"锁定缩放"
  默认是关的，双指可以自由缩放；退到后台再回来、重新进 GUI 也依旧是自由的；
  只有用户自己点那个锁形按钮才会锁定。除此之外与上游 v4.2.3 完全一致。
"""
anchor = "- 备注：用户确认此版本已正式投入使用，功能正常。此版本**没有**任何后续新增功能"
if "本版功能（一句话）" not in t:
    i = t.index(anchor)
    t = t[:i] + v1_extra.lstrip("\n") + t[i:]

v4 = """
### v4-image-patch-oskbutton-20261116 —— 修复"装了新版本但桌面没变化"（推荐安装）

- 文件：`apk-v4-tc423-xfce-zh-imagepatch-oskbutton.apk`
- 大小：761,866,427 字节
- SHA-256：`7E86BB0BEAB5A3345035AE19DE1CD1BB0DF227BEDD23DC7EA344275A9C6DA184`
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
  - 滚轮速度范围 1~5 → **1~9**，`deltaPerScroll = 8 + (档位-1)*6`：
    档位 3 = 20（上游原值），档位 1 = 8（比上游慢 2.5 倍，用户要的"再慢一点"）。
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
"""
if "v4-image-patch-oskbutton-20261116" not in t:
    anchor2 = "### 后续版本"
    i = t.index(anchor2)
    t = t[:i] + v4.lstrip("\n") + "\n" + t[i:]

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("readme updated, bytes=", len(t))
