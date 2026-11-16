# 03 怎么编译出 APK（本机环境 + 全部坑）

> 这篇回答：**从零到装出 APK，具体敲什么。**
> 环境装在 `build-env-toolchain/` 下，全部带 `-deletable` 后缀，可随时删掉重建。

## 1. 工具链（一次装好，之后复用）

| 组件 | 版本 | 位置 |
|---|---|---|
| JDK | 21.0.13+9 (Adoptium) | `build-env-toolchain/jdk21-runtime-deletable/jdk-21.0.13+9` |
| Android SDK | platform 37.0 + 35、build-tools 36.0.0 + 37.0.0 | `.../sdk-android-platform-tools-deletable` |
| NDK | 28.2.13676358 | 同上 `ndk/` |
| Gradle（APK） | 9.4.1 | `.../gradle-home-cache-deletable/gradle-dist/gradle-9.4.1` |
| Gradle（AVNC） | 8.13 **bin 版** | 同上 `gradle-dist/gradle-8.13` |

**必须用 bin 版 Gradle 8.13，不能用 all 版**：all 版里 `src/kotlin-dsl-provider-plugins/...`
路径超过 Windows 260 字符上限，解压必失败。

## 2. 环境变量脚本

`build-env-toolchain/env.ps1` 设好 `JAVA_HOME` / `ANDROID_HOME` / `ANDROID_SDK_ROOT` /
`ANDROID_USER_HOME` / `GRADLE_USER_HOME` / PATH 等。**用 `iex` 加载，不能 dot-source**
（执行策略限制）：

```powershell
iex (Get-Content "build-env-toolchain\env.ps1" -Raw -Encoding UTF8)
```

`-Encoding UTF8` 是必须的，否则中文路径变乱码。

## 3. 编译 AVNC 分支（改了 AVNC 才需要）

```powershell
iex (Get-Content "build-env-toolchain\build-avnc.ps1" -Raw -Encoding UTF8)
```

它执行 `gradle publishReleasePublicationToLocalForkRepository`，产物发布到
`refs-reference-assets-deletable/maven-local/com/github/tiny-computer/avnc/<版本>/`。

关键点：
- 速度约 1~2 分钟
- `settings.gradle.kts` 里**本地 maven 仓库必须排在 jitpack 之前**，否则会去 jitpack 找
  不存在的 `3.2.2-tc4vN` 并报 `Could not resolve`
- 改 AVNC 代码后**必须**先 bump 版本号（`app/build.gradle` 的 `version` 与构建副本
  `gradle/libs.versions.toml` 的 `avnc`），两处要一致；不 bump 会命中 Gradle 缓存，
  改的东西根本不进 AAR
- AVNC 只用 Kotlin 源码编译，`.so` 用官方 AAR 里的预编译版本（`jniLibs/`），
  **不要试图跑它的 cmake**

## 4. 编译 APK

```powershell
iex (Get-Content "build-env-toolchain\build-apk.ps1" -Raw -Encoding UTF8)
```

产物：`build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container/app/build/outputs/apk/release/app-release.apk`
日志：`build-env-toolchain/log-build-apk.txt`，成功标志 `BUILD SUCCESSFUL` + `GRADLE_EXIT=0`。
增量编译约 1.5 分钟；换镜像会重打包 assets，约 3~5 分钟。

## 5. 验证（三件事都要做）

```powershell
$bt = "$env:ANDROID_HOME\build-tools\36.0.0"
& "$bt\apksigner.bat" verify --print-certs <apk>       # 证书必须是 cd4e54df…66356b
& "$bt\zipalign.exe" -c -p 4 <apk>                     # 退出码 0
python tools-probe-scripts-deletable\check_apk_v2.py <apk>   # 条目数 / 镜像哈希 / dex 字符串
```
`apksigner.bat` 必须先 `iex env.ps1`，否则报 `JAVA_HOME is not set`。

## 6. 换镜像（三个 assets 必须一起换）

从 V4 起，`assets/` 里跟镜像有关的是**三个**文件，少一个用户就装不上新功能：

| 文件 | 作用 | 不换的后果 |
|---|---|---|
| `rootfs.tar.zst` | 完整镜像，全新安装 / 清空重装用 | 全新安装拿到旧系统 |
| `rootfs.patch.tar.zst` | 只含新增/改动文件的覆盖包（V4 是 267 个） | 「只更新系统文件」那条路无内容可覆盖 |
| `rootfs.stamp` | 镜像指纹，驱动「是否需要重新导入」的判断 | 不弹三选一对话框，用户以为没变化 |

替换步骤：

1. `python tools-probe-scripts-deletable/make_patch_tar.py <stock.tar> <new.tar> <patch.tar>`
   生成覆盖包（`stock.tar` 是官方原始镜像解压出来的 plain tar）。
2. `python tools-probe-scripts-deletable/zst_tar.py <patch.tar> rootfs.patch.tar.zst 19 4`
3. 三个文件一起复制到
   `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container/app/src/main/assets/`
4. **`rootfs.stamp` 内容必须改**，格式 `v<版本>-<镜像sha256前16位>`，例如
   `v4-d222bfa6580997c3`。用下面这行写，避免 PowerShell 5.1 的 `Set-Content -Encoding UTF8` 加 BOM：

```powershell
[System.IO.File]::WriteAllText("<...>\assets\rootfs.stamp", "v5-<sha前16位>", (New-Object System.Text.UTF8Encoding $false))
```

5. 重新跑 `build-apk.ps1`。
6. `noCompress.add("zst")` 已在 `app/build.gradle.kts` 里，镜像与覆盖包都会以 STORED
   存进 APK（否则打包极慢且 APK 反而更大）。

## 7. 重打包镜像（改镜像内容）

```powershell
$env:PYTHONPATH = "tools-probe-scripts-deletable\pyz2"   # zstandard wheel，pip 装不上
python tools-probe-scripts-deletable\unzst_tar.py <in.tar.zst> <plain.tar>
python tools-probe-scripts-deletable\build_rootfs_v2.py <plain.tar> <out.tar>
python tools-probe-scripts-deletable\zst_tar.py <out.tar> <out.tar.zst> 19 4
python tools-probe-scripts-deletable\verify_rootfs_v2.py <out.tar>
python tools-probe-scripts-deletable\make_patch_tar.py <stock.tar> <out.tar> <patch.tar>
python tools-probe-scripts-deletable\zst_tar.py <patch.tar> <patch.tar.zst> 19 4
```
脚本**不解压到磁盘**，逐个 tar 成员流式重写，所以 uid/gid/权限/时间戳原样保留；
身份固定为 `10258:10258 aid_u0_a258`，格式必须是 **GNU tar**（不是 PAX）。

## 8. 这台机器的坑（踩过的，别再踩）

1. **CMake / ninja 完全不可用**：沙箱禁止子进程管道 stdio，ninja 会 0 CPU 永久卡死。
   → JNI 用 NDK clang 手工编译（V1 已编好放在 `jniLibs/arm64-v8a/`）。
2. **`curl.exe` / `Invoke-WebRequest` 走不通**（schannel `SEC_E_NO_CREDENTIALS`）。
   → 用 `python tools-probe-scripts-deletable/pdl.py`（多线程 Range 下载）或 `git`。
3. **代理 `127.0.0.1:7897` 比直连慢 60~90 倍**（Google 系）。GitHub/Adoptium 直连反而慢，
   jitpack 必须走代理。下载脚本第 3 个参数可切 `direct|proxy`。
4. **PowerShell 控制台是 GBK**：任何非 ASCII 的 `print` 会崩。→ 结果写文件再读。
5. **`python - <<'PY'`  heredoc 在这里不存在**，一律写 `.py` 文件再跑。
6. **`$PSScriptRoot` 在 `iex` 下是空的**，脚本里用 `(Get-Location).Path`。
7. **控制台里的 `python -c` 处理中文路径会乱码**，用 `.py` 文件 + 参数。
8. 源码文件是 **CRLF**，用 `edit` 工具匹配 `\n` 会失败；写补丁脚本时用
   `open(path, newline='')` 读、写 `\r\n`。已有文件可能是混合换行，用 `\r?\n` 正则匹配。
9. 数据绑定**只为声明了 `<variable>` 的布局生成 `*Binding` 类**；没有就自己 `inflate()`。
10. `C:\Users\Administrator\.android` 不可写：`ANDROID_USER_HOME` 已改到 cache 目录，
    忽略 `Unable to initialize metrics` 警告。
