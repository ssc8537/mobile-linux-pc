import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\docs-project-notes-keep-forever\log-version-history.md"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

t = t.replace("- `v3-osk-settings-20261116/` —— V3（悬浮键盘补设置入口，**最新**）",
              "- `v3-osk-settings-20261116/` —— V3（悬浮键盘补设置入口）\n"
              "- `v4-image-patch-oskbutton-20261116/` —— V4（修复镜像未导入 + 指针按钮，**最新**）")

v1_note = ("- 上游 v4.2.3 原样 + **一行改动**：进入图形界面时缩放默认不再锁定\n"
           "  （`ContainerMainFragment.kt:150` `fZoomLocked = false`；也就是说 V1 唯一实现的功能就是\n"
           "  **自由缩放**：进去就能双指缩放，退后台回来再进也还是自由的，只有用户自己点锁才锁）\n")
if "也就是说 V1 唯一实现的功能就是" not in t:
    t = t.replace("- 上游 v4.2.3 原样 + **一行改动**：进入图形界面时缩放默认不再锁定\n", v1_note, 1)

v4 = """
## V4 —— 修复"装了新版本但桌面没变化"（最新）

- 文件 `apk-v4-tc423-xfce-zh-imagepatch-oskbutton.apk`，761,866,599 字节
- SHA-256 `B1C57CCCB6A35C932E9C1C4F1323F269C81EB2BF7C2F0F4970A72781191D8CFD`
- 内置镜像 `rootfs-v5.tar.zst`（732,841,425 字节，
  sha256 `D222BFA6580997C319403E99C0F18311EAAA51F5BA3A11D6B800204B0EA4A222`）
  + `assets/rootfs.patch.tar.zst`（554,647 字节，267 个新增/改动文件）
  + `assets/rootfs.stamp`（`v4-d222bfa6580997c3`）
- **根因**：`MainActivity` 只在 `installedContainers.isEmpty()` 时自动导入，
  覆盖安装时旧容器还在 → 新镜像从没被解压 → 所有镜像侧功能都没出现。
  现在启动比对 stamp，不一致弹三选一：只更新系统文件（`applyImagePatch()`，
  保留数据）/ 重新导入（清空）/ 以后再说。
- AVNC 分支 `3.2.2-tc4v6`；其余：`ValueLabelPreference` 数值标签、
  滚轮 1~9（`deltaPerScroll = 8 + (档位-1)*6`）、指针颜色独立开关、
  亮度映射染色、九宫格删除改为单个 40dp 跟随按钮、右侧常驻按钮删除、
  OSK 三条召唤路径 + `/tmp/.tiny_osk.log`。
"""
if "## V4 —— 修复" not in t:
    anchor = "## 回退方法"
    i = t.index(anchor)
    t = t[:i] + v4.lstrip("\n") + "\n" + t[i:]

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("log updated bytes=", len(t))
