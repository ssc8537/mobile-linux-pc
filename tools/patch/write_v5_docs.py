# -*- coding: utf-8 -*-
"""Append the V5 entry to both version-history documents."""
import io
import os

R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"

README = os.path.join(R, "build-env-toolchain", "apks-archive-keep-forever",
                      "readme-versions-zh.md")
LOG = os.path.join(R, "docs-project-notes-keep-forever", "log-version-history.md")

V5_README = '''### v5-caret-osk-hk-20261116 —— 光标旁键盘 + 真·黑客键盘移植 + 修「输入」崩溃（推荐安装）

- 目录：`apks-archive-keep-forever\\v5-caret-osk-hk-20261116\\`
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

'''

V5_LOG = '''## V5 —— 光标旁键盘 + 黑客键盘移植 + 修「输入」崩溃（最新）

- 归档：`build-env-toolchain\\apks-archive-keep-forever\\v5-caret-osk-hk-20261116\\apk-v5-tc423-xfce-zh-caret-osk-hk.apk`
- 761,875,619 字节，SHA-256 `B2CD44F9F678364D3F6D334FDA33AC06A8CB985C48EE2477A54E12A12B51E6A3`
- 改了三层：
  - App 侧：`MainActivity` 静默打补丁 `autoPatchImageIfOutdated()`；
    `ContainerMainFragment` 多传一个 `tc4.osk_caret` 路径。
  - AVNC 侧（`3.2.2-tc4v9`）：`pref_input.xml` 恢复官方三个分类；
    `VncActivity` 用 `readCaretRect()` 读光标文件决定按钮位置。
  - 镜像侧：新增 `hk_layout.py`、`tiny_osk_caret.py`、`tiny-osk-caret` 与它的 autostart；
    `docklike-2.rc` 清空 `pinned=`。
- 教训：**改 `pref_input.xml` 不能删官方分类**，`PrefsActivity` 里有 11 个 `!!`。

'''

for path, block, anchor in (
        (README, V5_README, "### 后续版本"),
        (LOG, V5_LOG, "## 回退方法"),
):
    src = io.open(path, encoding="utf-8", newline="").read()
    if "v5-caret-osk-hk" in src:
        print("already has v5:", path)
        continue
    assert anchor in src, "anchor missing in " + path
    src = src.replace(anchor, block + anchor, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(src)
    print("updated", path, "->", len(src), "bytes")
