import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\docs-project-notes-keep-forever\spec-rootfs-map.md"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

extra = """
## 悬浮键盘（tiny_osk.py）为什么以前"召唤不出来"

V4 之前只有一条路：AVNC 往远端发 `XF86XK_Launch0` 键码。这条路依赖容器里 X 的 keymap
真的把 XF86Launch0 映射到某个 keycode，只要不认就彻底没反应，而且键盘进程本身
静默崩溃也看不出来。V4 改成三条并联 + 全程日志：

1. **触发文件**：AVNC 写 `filesDir/tmp/.tiny_osk_toggle`（容器 `/tmp` 就是它的 bind）。
2. **`OskBridge`**（最可靠）：AVNC 回调宿主 App → 宿主 `Global.sendCommand("/usr/local/bin/tiny-osk-toggle")`。
3. 兜底才发 `XF86XK_Launch0`。

配套加固：
- `usr/local/bin/tiny-osk`：进程已在 → 转 `tiny-osk-toggle`；DISPLAY 空则从
  `/tmp/.X11-unix/X0..X6` 里猜；全程 `>> /tmp/.tiny_osk.log 2>&1`。
- `usr/local/bin/tiny-osk-toggle`：先 `pgrep -f tiny_osk.py`，不在就 `nohup` 拉起来
  再 `sleep 1` 写触发文件，所以"键盘压根没启动"也能救回来。
- `tiny_osk.py`：`_ensure_display()`、`_log()`、`__main__` 里 catch `BaseException`
  并把 traceback 写进日志；`start_hotkey_listener` 失败不再拖死整个键盘。

**排查顺序**（用户报"键盘没出来"时）：
1. `cat /tmp/.tiny_osk.log` —— 有没有 Python traceback
2. `pgrep -f tiny_osk.py` —— 进程在不在
3. `ls -l /tmp/.X11-unix/` —— DISPLAY 猜对没有
4. 手动 `python3 /usr/local/share/tiny-osk/tiny_osk.py` 看是否报 GTK 缺库

## 镜像升级机制（V4 新增，务必理解）

`MainActivity` 原来只在 `installedContainers.isEmpty()` 时导入内置镜像 —— 覆盖安装
时旧容器还在，新镜像**永远不会**被解压。V4 的做法：

- `assets/rootfs.stamp` 存镜像指纹，`Global.builtInImageStamp` 存"已导入过哪个指纹"。
- 启动时两者不一致 → 弹三选一：
  - 只更新系统文件（`applyImagePatch()`，解压 `rootfs.patch.tar.zst` 到现有容器，
    **不删** `dataDir/<code>`）
  - 重新导入（`autoInstallBuiltInContainer()`，会 `deleteRecursively()`）
  - 以后再说（只更新指纹，不再提示）
- 每次成功导入/覆盖后都要把 stamp 记进 SharedPreferences，否则每次启动都弹。

这条机制是 V4 修掉"装了新版本但桌面功能全都没出现"的关键，改镜像时别忘了三个
assets 一起换（见 `build-make-apk.md` 第 6 节）。
"""
if "## 悬浮键盘（tiny_osk.py）为什么以前" not in t:
    t = t.rstrip("\n") + "\n" + extra

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("rootfs map updated bytes=", len(t))
