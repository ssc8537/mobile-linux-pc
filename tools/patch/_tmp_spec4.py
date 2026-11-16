import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\docs-project-notes-keep-forever\spec-changes-v2.md"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

# --- A. App 侧表格：补 V4 的四个文件 ---
old_rows = """| `app/src/main/res/values/strings.xml`、`values-zh-rCN/strings.xml` | 新增 `tc4_settings_dev_options_title` / `_desc` / `_failed` 三条 |
"""
new_rows = old_rows + """| `app/src/main/java/com/fct/tc4/ui/misc/Global.kt` | **V4**：新增 `builtInImageStamp` / `readBuiltInImageStamp()` / `isBuiltInImageOutdated()`（镜像指纹） |
| `app/src/main/java/com/fct/tc4/ui/main/MainActivity.kt` | **V4**：`onCreate` 里加「镜像过期 → `askReimportImage()`」判断；新增 `askReimportImage()`（三选一对话框）与 `onNormalLaunchContinue()` |
| `app/src/main/java/com/fct/tc4/ui/page/ContainerManageViewModel.kt` | **V4**：新增 `applyImagePatch()`（解压覆盖包，不删容器）；`autoInstallBuiltInContainer()` / `confirmInstall()` / `startBuiltInImport()` 里维护 stamp 与 `installedContainers` |
| `app/src/main/java/com/fct/tc4/ui/page/ContainerMainViewModel.kt` | **V4**：`setupEnvironment()` 里注册 `OskBridge.summon = { Global.sendCommand("/usr/local/bin/tiny-osk-toggle") }`，`onCleared()` 里置 null |
| `app/src/main/java/com/fct/tc4/ui/page/ContainerMainFragment.kt` | **V4**：`createVncIntent` 之后加 `intent.putExtra("tc4.osk_trigger", filesDir/tmp/.tiny_osk_toggle)` |
| `app/src/main/res/values/strings.xml`、`values-zh-rCN/strings.xml` | V4 再加 `tc4_reimport_title/_message/_patch/_confirm/_later` 五条 |
| `app/src/main/assets/rootfs.stamp` | **新增文件**，内容是镜像指纹（当前 `v4-d222bfa6580997c3`），换镜像必须同步改 |
| `app/src/main/assets/rootfs.patch.tar.zst` | **新增文件**，只含 267 个新增/改动文件的覆盖包，`applyImagePatch()` 用它 |
"""
assert old_rows in t
t = t.replace(old_rows, new_rows, 1)

# --- B. AVNC 侧：补 V4 的文件 ---
t = t.replace(
    "- `app/build.gradle` —— 关闭 cmake，改用预编译 `jniLibs`；版本号改 `3.2.2-tc4v2`；加本地 maven 发布仓库",
    "- `app/build.gradle` —— 关闭 cmake，改用预编译 `jniLibs`；版本号 **`3.2.2-tc4v6`**（V4 交付值）；加本地 maven 发布仓库")
t = t.replace(
    "- `.../ui/vnc/VncActivity.kt` —— 缩放提示浮层、九宫格键盘浮层、`openRemoteKeyboard()`",
    "- `.../ui/vnc/VncActivity.kt` —— 缩放提示浮层、**单个 40dp 跟随指针的键盘按钮**\n"
    "  （`positionOskButton()` + 100 ms `oskFollowTick`，V4 起九宫格与右侧常驻按钮都已删除）、\n"
    "  `openRemoteKeyboard()` 三条召唤路径")
t = t.replace(
    "- `app/src/main/res/layout/view_zoom_hint.xml`、`view_osk_ring.xml`",
    "- `app/src/main/res/layout/view_zoom_hint.xml`\n"
    "  （**注意**：`view_osk_ring.xml` 在 V4 已删除，不要再加回来）\n"
    "- `app/src/main/java/com/gaurav/avnc/ui/prefs/ValueLabelPreference.kt`（滑块显示「加速 6 倍」这类数值标签）\n"
    "- `app/src/main/java/com/gaurav/avnc/util/OskBridge.kt`（让宿主 App 注册「召唤容器内键盘」的回调）\n"
    "- `res/values/attrs.xml` 里新增 `<declare-styleable name=\"ValueLabelPreference\">`")

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("spec updated bytes=", len(t))
