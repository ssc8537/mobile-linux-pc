# tools/patch — 改源码用的脚本

两个用途：**(1) 记录每个改动点**（可重放、可作为 diff 说明）；
**(2) 重打包镜像**（`build_rootfs_v2.py` 那一串，见 `docs/spec-changes-and-rootfs.md` B10）。

所有脚本都按「锚点断言」写：找不到预期的原文就报错退出，不会静默改坏文件。
所以上游升级后重跑它们，失败的那一个就是「上游结构变了」的准确信号。

路径也不写死：每个脚本头部都有 `_find_ws()`，依次查 `$env:TC_ROOT` → 从脚本所在目录向上找
含 `build-env-toolchain` 或 `source/app` 的目录，找到的就是工作区根 `WS`。
换机器 / 换盘符不用改代码，`export TC_ROOT=...` 或 `$env:TC_ROOT=...` 也能强制指定。

## 常用（会用到）

| 脚本 | 干什么 |
|---|---|
| `bump_version.py` | 同时改 AVNC 的 `version` 与 `libs.versions.toml` 的 `avnc`（**改 AVNC 后必须跑**，否则 Gradle 缓存会配旧 AAR） |
| `extract_aar_jni.py` | 从官方 AAR 抽出 4 个 `libnative-vnc.so` 到 `jniLibs/<abi>/` |
| `build_rootfs_v2.py` | 重打包 rootfs：改 3 个配置文件 + 追加 deb 里的新文件 |
| `make_patch_tar.py` | 只抽出「新增 / 被改」的成员，做增量 overlay |
| `unzst_tar.py` / `zst_tar.py` | zstd 解 / 压（level 19, 4 threads） |
| `check_apk_v2.py` | 验 APK：zip 条目数、两个 zst 是否 STORED、dex 关键字 |

## 改 App 侧（tiny_container）

| 脚本 | 改哪里 |
|---|---|
| `patch_stamp1.py` | `Global.kt` → `builtInImageStamp` / `readBuiltInImageStamp()` / `isBuiltInImageOutdated()` |
| `patch_main_reimport.py` | `MainActivity.kt` → 启动时判断镜像过期、`askReimportImage()` 三选一对话框 |
| `patch_apply_patch_vm.py` | `ContainerManageViewModel.kt` → `applyImagePatch()` |
| `patch_install_stamp.py` | `ContainerManageViewModel.kt` → 安装 / 导入时写 stamp |
| `patch_patch_cleanup.py` | `ContainerManageViewModel.kt` → 打补丁前先 `$BIN_DIR/rm -rf` 掉 V5 键盘残留 |
| `patch_devoptions.py` | `SettingsViewModel.kt` + `SettingsFragment.kt` + strings → 设置页「开发者选项」跳转 |
| `patch_reimport_strings.py` / `patch_strings.py` / `patch_strings2.py` | 各处 strings.xml 文案 |

> `ContainerMainFragment.kt:150 fZoomLocked = false` 这一行没有单独脚本 ——
> 它只在上游那份源码里改过一次，之后所有版本都沿用（见 `docs/spec-changes-and-rootfs.md` A1）。

## 改 AVNC 侧

| 脚本 | 改哪里 |
|---|---|
| `patch_accel.py` | `PointerAcceleration.kt` / `PointerModes.kt` / `AppPreferences.kt` → 加速开关 + 强度 + 慢速基速 |
| `patch_v4_avnc_1.py` | 同上第二轮（滚轮档位两段式、光照亮度染色） |
| `patch_cursor.py` | `Cursor.kt` / `Shaders.kt` / `Program.kt` / `Renderer.kt` → 大小 + tint |
| `patch_touchhandler.py` | `TouchHandler.kt` → 缩放二次确认计时器 |
| `patch_pref_xml.py` | `res/xml/pref_input.xml` → 指针调整 / 指针外观两组，快捷键 `Super+V` |
| `patch_arrays.py` | `values/arrays.xml` |
| `patch_vncactivity.py` / `patch_vncactivity2.py` | `VncActivity.kt`（第二轮加了光标按钮相关代码，V6 已删除） |
| `patch_pointermodes.py` | `PointerModes.kt` |
| `patch_tap3_gate.py` | 三指轻点开关（默认关） |

## 改镜像侧

| 脚本 | 改哪里 |
|---|---|
| `patch_rootfs_v5.py` | 在 `build_rootfs_v2.py` 里插入 5 个键盘相关文件（**已被 `strip_osk_rootfs.py` 撤销**） |
| `strip_osk_rootfs.py` | 把键盘相关常量 / 桌面项 / `reg()` 调用从 `build_rootfs_v2.py` 里摘掉 |
| `strip_osk_avnc.py` | 把键盘相关 Kotlin / XML / 字符串从 AVNC + App 里摘掉（V6 定稿） |
| `patch_clipman_autostart.py` | 补 clipman 的 autostart（deb 自带的那条 `Hidden=true`，不会自启） |
| `patch_clip_shortcut.py` | `Super+V` / `Super+Shift+V` 绑到 clipman |
| `check_deb_deps.py` / `deb_list.py` / `deb_cat.py` | 离线核对 deb 依赖 / 看 deb 内容（确认不用联网 apt） |
| `dl.py` / `dl_debs.py` / `dl_more_debs.py` / `pdl.py` | 下载 deb / 镜像（多线程 Range） |
| `verify_rootfs_v2.py` | 验重打包结果：成员数、owner、关键文件内容 |
| `wire_local_avnc.py` | 把 App 的依赖切到本地 maven 的 AVNC fork |
| `tiny_dot_yaml.yaml` / `tiny.yaml` | 镜像里 `.tiny.yaml` 的样本（37808 B），改选项配置时对照 |

## 子目录

| 目录 | 内容 |
|---|---|
| `_historical-keyboard-do-not-rerun/` | V2~V5 加键盘的 12 个脚本。**V6 已把键盘整体删除，这些只作历史记录，不要再跑。** |
| `_obsolete-checks-do-not-rerun/` | 17 个一次性探针 / 旧版校验（V3 时代的 `final_check_v3.py` 等）。 |
