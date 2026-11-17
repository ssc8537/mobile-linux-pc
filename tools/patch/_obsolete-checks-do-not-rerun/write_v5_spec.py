# -*- coding: utf-8 -*-
"""Append the V5 delta to spec-changes-v2.md (handover doc)."""
import io
import os

P = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\spec-changes-v2.md"
src = io.open(P, encoding="utf-8", newline="").read()

block = '''
## D. V5 新增/改动（在 A/B/C 之外，务必一起看）

### App 侧（tiny_container）

| 文件 | 改动 |
|---|---|
| `ui/main/MainActivity.kt` | 原来的三选一对话框不再弹；`if (Global.installedContainers.isNotEmpty() && Global.isBuiltInImageOutdated()) autoPatchImageIfOutdated()`。函数体 `if (autoPatchStarted) return` 后调 `containerViewModel.applyImagePatch()`。`askReimportImage()` 保留作手动入口 |
| `ui/page/ContainerMainFragment.kt` | 除了 `tc4.osk_trigger`，再传 `tc4.osk_caret`（`filesDir/tmp/.tiny_osk_caret`） |

### AVNC 侧（`3.2.2-tc4v9`）

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

### 重做黑客键盘移植的完整命令链

```powershell
# 1) 生成键位表（读 hackerskeyboard 的 res/xml 与 res/values）
python tools-probe-scripts-deletable/gen_hk_layout.py
# 2) 把 xkb keysym 补丁打进 tiny_osk.py（已应用过就跳过）
python tools-probe-scripts-deletable/patch_osk_hk.py
python tools-probe-scripts-deletable/patch_osk_hk2.py
# 3) 重打包镜像（三份产物必须一起换：rootfs.tar.zst / rootfs.patch.tar.zst / rootfs.stamp）
python tools-probe-scripts-deletable/build_rootfs_v2.py cache\\rootfs-plain.tar cache\\rootfs-v6.tar
python tools-probe-scripts-deletable/make_patch_tar.py cache\\rootfs-plain.tar cache\\rootfs-v6.tar cache\\rootfs-patch-v6.tar
python tools-probe-scripts-deletable/zst_tar.py cache\\rootfs-v6.tar cache\\rootfs-v6.tar.zst 19 4
python tools-probe-scripts-deletable/zst_tar.py cache\\rootfs-patch-v6.tar cache\\rootfs-patch-v6.tar.zst 19 4
```

### 黑客键盘源码参考位置

- 上游：`refs-reference-assets-deletable/hackerskeyboard/`（`klausw/hackerskeyboard`，`--depth 1`）
- 键位 XML：`app/src/main/res/xml/kbd_{full,compact,symbols,symbols_shift}.xml`
- 键码常量：`app/src/main/res/values/keycodes.xml`（全是负数码，映射见 `gen_hk_layout.py` 的 `HKCODE_TO_KEYSYM`）
- 标签/上档字符：`app/src/main/res/values/donottranslate-keymap.xml`
- **坑**：HK 的 XML 用 `xmlns:android="http://schemas.android.com/apk/res-auto"`（自己的 attrs），
  不是 `res/android`；按 `res/android` 解析会得到全空的键位表。

'''

anchor = "## 判断「哪些必须保留」的一句话规则"
assert anchor in src
if "## D. V5 新增/改动" not in src:
    src = src.replace(anchor, block.lstrip("\n") + "\n" + anchor, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(src)
    print("updated spec-changes-v2.md ->", len(src))
else:
    print("already has V5 section")
