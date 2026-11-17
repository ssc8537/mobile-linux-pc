# 03 怎么编译 + 上游更新怎么合并

> 这篇回答两件事：
> **（A）从零到装出 APK 具体敲什么，以及这台机器的坑**
> **（B）官方发了新版，怎么把自己的功能搬过去而不丢东西**
> 改了哪些文件见 `spec-changes-and-rootfs.md`。

---

# A 部分：编译环境与流程

## A1. 工具链（一次装好，之后复用）

| 组件 | 版本 | 位置（相对 `build-env-toolchain/`） |
|---|---|---|
| JDK | 21.0.13+9 (Adoptium) | `jdk21-runtime-deletable/jdk-21.0.13+9` |
| Android SDK | platform 37.0 + 35、build-tools 36.0.0 + 37.0.0 | `sdk-android-platform-tools-deletable` |
| NDK | 28.2.13676358 | 同上 `ndk/` |
| Gradle（编 APK） | **9.4.1** | `gradle-home-cache-deletable/gradle-dist/gradle-9.4.1` |
| Gradle（编 AVNC） | **8.13 bin 版** | 同上 `gradle-dist/gradle-8.13` |

> **必须用 bin 版 Gradle 8.13，不能用 all 版**：all 版里
> `src/kotlin-dsl-provider-plugins/...` 路径超过 Windows 260 字符上限，解压必失败。
> 两个 Gradle 并存是正常的：tiny_container 用 AGP 9.x 需要 9.4.1，
> AVNC fork 用 AGP 8.10.1 需要 8.13。**不要试图统一**。

## A2. 载入环境（每次开新终端都要）

```powershell
# 在工作区根目录（含 build-env-toolchain 的那层）执行
iex (Get-Content "tools\build\env.ps1" -Raw -Encoding UTF8)
```

必须用 `iex`（执行策略不允许 dot-source），且必须 `-Encoding UTF8`（否则中文路径乱码）。
脚本设好 `JAVA_HOME` / `ANDROID_HOME` / `ANDROID_SDK_ROOT` / `ANDROID_USER_HOME` /
`GRADLE_USER_HOME` / `PATH`，并导出 `$env:BUILD_DIR` / `$env:CACHE_DIR` /
`$env:OUTPUT_DIR` / `$env:SOURCE_DIR` / `$env:AVNC_DIR` 五个路径变量，
启动时打印一行 `TC_ROOT=<找到的根目录>` 供核对。

> **脚本里不再写死 `C:\Users\Administrator\...`。** 根目录是「从当前目录向上找
> 含 `build-env-toolchain` 的那一层」得来的；找不到就用当前目录。
> 想指定就别猜：先设 `$env:TC_ROOT` 再 `iex`，或直接设 `$env:BUILD_DIR` / `$env:AVNC_DIR`。

> `$PSScriptRoot` 在 `iex` 下是**空的**，所以脚本里一律从 `(Get-Location).Path` 推导。

## A3. 编 AVNC 分支（只有改了 AVNC 才需要）

```powershell
iex (Get-Content "tools\build\build-avnc.ps1" -Raw -Encoding UTF8)
```

它执行 `gradle publishReleasePublicationToLocalForkRepository`，把 AAR 发布到
`refs-reference-assets-deletable/maven-local/com/github/tiny-computer/avnc/<版本>/`
（纯 git clone 场景则是 `<仓库根>/avnc-maven-local/...`——两边用同一套查找规则）。
耗时约 30 秒 ~ 2 分钟，成功标志 `BUILD SUCCESSFUL` + `GRADLE_EXIT=0`。

发布目录由 `source/avnc/app/build.gradle` 里的 `localForkRepoDir()` 决定，
消费端由 `source/app/settings.gradle.kts` 里的 `resolveAvncMavenLocal()` 决定，
**两边的查找顺序一致**：

1. 环境变量 `AVNC_MAVEN_LOCAL`（想放哪就放哪）
2. 任一祖先目录下的 `avnc-maven-local/`
3. 任一祖先目录下的 `refs-reference-assets-deletable/maven-local/`（原始工作区布局）

因为是从当前目录向上找，无论项目放在 `<工作区>/source/app` 还是
`<工作区>/build-env-toolchain/.../tiny_container`，都不需要改文件。

### 三个必须记住的点

1. **改 AVNC 代码后必须先 bump 版本号**，两处都要改且要一致：
   `avnc-upstream-fork-deletable/app/build.gradle` 的 `version`
   与构建副本 `gradle/libs.versions.toml` 的 `avnc`。
   不 bump 会命中 Gradle 缓存，**改的内容根本不进 AAR**（静默出错，最难查）。
   用 `python tools-probe-scripts-deletable/bump_version.py 3.2.2-tc4v11`（BOM 安全的字节替换）。
2. **本地 maven 仓库必须排在 jitpack 之前**（`settings.gradle.kts` 的
   `dependencyResolutionManagement`），否则会去 jitpack 找不存在的 `3.2.2-tc4vN` 报 `Could not resolve`。
3. **AVNC 只编 Kotlin**，`.so` 用官方 AAR 里的预编译版本放在 `jniLibs/`，
   **不要试图跑它的 CMake**（原因见 A6 第 1 条）。

## A4. 编 APK

```powershell
iex (Get-Content "tools\build\build-apk.ps1" -Raw -Encoding UTF8)
```

脚本会自己找项目目录，按顺序试：`$env:BUILD_DIR` →
`build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container` →
`source/app` → 当前目录，取第一个含 `gradlew` 的，并打印 `BUILD_PROJECT=<路径>`。
它也自己判断有没有 `build-env-toolchain/`：有就用内置 JDK/SDK/Gradle，没有就用 PATH 上的。

- 产物：`<项目>/app/build/outputs/apk/release/app-release.apk`
  （原始工作区下即 `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container/app/build/outputs/apk/release/app-release.apk`）
- 日志：`build-env-toolchain/log-build-apk.txt`（无内置工具链时写到工作区根），
  成功标志 `BUILD SUCCESSFUL` + `GRADLE_EXIT=0`
- 增量编译约 1.5 分钟；换镜像要重打包 assets，约 3~5 分钟
- 脚本内的代理设置不同：`build-avnc.ps1` **走**代理（要拉依赖），
  `build-apk.ps1` **不走**代理（依赖都已在 gradle 缓存里）

## A5. 验证（三件事都要做，缺一不可）

```powershell
$bt = "$env:ANDROID_HOME\build-tools\36.0.0"
$apk = "$env:BUILD_DIR\app\build\outputs\apk\release\app-release.apk"
& "$bt\apksigner.bat" verify --print-certs $apk             # 证书必须是 cd4e54df…66356b
& "$bt\zipalign.exe" -c -p 4 $apk                           # 退出码必须为 0
python tools\patch\check_apk_v2.py $apk                     # 条目数 / 镜像哈希 / dex 关键字
```

`apksigner.bat` 必须先 `iex tools\build\env.ps1`，否则报 `JAVA_HOME is not set`。

经验值（V6）：1338 个 zip 条目，`assets/rootfs.tar.zst` 与
`assets/rootfs.patch.tar.zst` 必须是 `method 0`（STORED），否则说明
`noCompress("zst")` 没生效。dex 关键字检查要覆盖**删掉的功能为 False、保留的功能为 True**
两边（例如 V6 要求 `OskBridge` / `openRemoteKeyboard` 全 False，
`mouseAcceleration` / `applyImagePatch` / `setFZoomLocked` 全 True）。

> AAPT2 会混淆资源路径：编译后的 `res/xml/pref_input.xml` 可能变成 `res/bb.xml`。
> 验证偏好项要用 `aapt2 dump resources` / `aapt2 dump xmltree`，**不要靠 grep dex**。

## A6. 这台机器的坑（踩过的，别再踩）

1. **CMake / ninja 完全不可用**：沙箱禁止子进程管道 stdio，`try_compile` 起的
   `ninja.exe cmTC_xxxx` 会 0 CPU 永久卡死（在纯 ASCII 临时工程里复现过，不是中文路径问题）。
   → 只能关掉 `externalNativeBuild`，JNI 用 NDK clang 手工编译，或用官方预编译 `.so`。
2. **`curl.exe` / `Invoke-WebRequest` 走不通**（schannel `SEC_E_NO_CREDENTIALS 0x8009030e`）。
   → 用 `python tools-probe-scripts-deletable/pdl.py`（多线程 Range 下载）或 `git`。
3. **代理 `127.0.0.1:7897` 对 Google 系慢 60~90 倍**，但 jitpack / GitHub 必须走代理。
   下载脚本第 3 个参数可切 `direct|proxy`。GitHub **上传**绝不能走代理（会 SSL EOF 立刻失败）。
4. **PowerShell 控制台是 GBK**：任何非 ASCII 的 `print` 会崩。→ 结果写文件再读。
5. **`python - <<'PY'` heredoc 不存在**，一律写 `.py` 文件再跑；`python -c` 处理中文路径必乱码。
6. **源码是 CRLF**：用 `edit` 工具匹配 `\n` 会失败。写补丁脚本时
   `open(path, newline='')` 读、写 `\r\n`，或用 `\r?\n` 正则匹配（文件可能是混合换行）。
7. **`Set-Content -Encoding UTF8` 会加 BOM**，Gradle 报 `Unexpected character '' @ line 1`。
   写需要给 Gradle/Kotlin 读的文件时，用
   `[System.IO.File]::WriteAllText($p, $s, (New-Object System.Text.UTF8Encoding $false))`。
8. **`C:\Users\Administrator\.android` 不可写**：`ANDROID_USER_HOME` 已改到缓存目录，
   忽略 `Unable to initialize metrics` 警告。
9. **数据绑定只为声明了 `<variable>` 的布局生成 `*Binding` 类**；没有就自己 `inflate()`。
10. **删 XML 块时用唯一注释锚定，并断言删前删后的行数**。曾用一条正则删
    `cursor_tint_enabled` 一行，连带吞掉了整个指针调参块（后来逐字恢复）。
    同类事故还有：根目录 `.gitignore` 里一个裸 `build/` 把 `tools/build/` 整个吞了。

## A7. 换镜像（三个 assets 必须一起换）

| 文件 | 作用 | 不换的后果 |
|---|---|---|
| `rootfs.tar.zst` | 完整镜像，全新安装 / 清空重装用 | 全新安装拿到旧系统 |
| `rootfs.patch.tar.zst` | 只含新增/改动成员的覆盖包 | 「只更新系统文件」那条路没内容可覆盖 |
| `rootfs.stamp` | 镜像指纹，驱动是否需要重新导入的判断 | 不触发覆盖，用户以为没变化 |

步骤：重打包镜像（命令见 `spec-changes-and-rootfs.md` B10）→ 三份一起复制进
`...\tiny_container\app\src\main\assets\` → 改 `rootfs.stamp` → 重跑 `build-apk.ps1`。
`noCompress.add("zst")` 已在 `app/build.gradle.kts` 里，镜像会以 STORED 存进 APK
（否则打包极慢且 APK 反而更大）。

---

# B 部分：上游更新了怎么办

## B1. 我们的改动分三层，合并难度不同

| 层 | 改在哪 | 合并方式 | 难度 |
|---|---|---|---|
| App 层 | 构建副本 12 个文件 | 手贴 | 低 |
| AVNC 层 | 独立 fork 仓库 | 重新贴补丁 / rebase | 中 |
| 镜像层 | `build_rootfs_v2.py` | 改脚本常量重跑 | 低 |

## B2. 标准流程

### 第 1 步：拿官方新版源码

```powershell
$env:HTTPS_PROXY='http://127.0.0.1:7897'
git -c http.sslBackend=openssl clone --depth 1 https://github.com/Cateners/tiny_container.git <新版目录>
```

（`git` 会把 `Cloning into…` 打到 stderr 并可能返回 1，但目录是好的，别被退出码骗了。）

### 第 2 步：找官方改了什么

对比 `apps-tiny-container-v423-source`（手上的 v4.2.3）和新版目录。重点看：
`build.gradle.kts`（版本号、依赖、SDK）、`gradle/libs.versions.toml`（**avnc 版本号会变**）、
`AndroidManifest.xml`、`ui/page/` 下的 Kotlin 文件、`res/layout/`。

### 第 3 步：把我们的改动贴回去

按 `spec-changes-and-rootfs.md` A1 的表逐条贴（12 个文件）。
**特别注意 `ContainerMainFragment.kt` 的 `fZoomLocked = false`** —— 这是 V1 的核心功能，
官方随时可能重构这段，贴之前先确认新版的 `ServerProfile` 创建点在哪。

也可以直接跑 `tools/patch/` 里的脚本（幂等，锚点断言会失败就说明上游结构变了）。

### 第 4 步：处理 AVNC

- 官方**没换** `avnc` 版本（还是 `030e6c032e`）：本地 fork 不用动，直接用
- 官方**换了** `avnc` 版本：必须在新的上游 commit 上重做 AVNC 补丁：
  1. 在 jitpack 确认新版本号对应哪个 commit，`git clone` 那个 commit
  2. 按 `spec-changes-and-rootfs.md` A2 的表把 17 个修改 + 6 个新增重贴
  3. **不要碰 native 代码**：关掉 `externalNativeBuild`，把官方 AAR 里的
     `jni/<abi>/libnative-vnc.so` 解出来放 `jniLibs/`
     （`tools-probe-scripts-deletable/extract_aar_jni.py` 就是干这个的）
  4. 编 AVNC → 发布到本地 maven → 改 `libs.versions.toml` 的 `avnc` 版本号

### 第 5 步：重建构建副本并编译

`ws-gradle-build-copy-deletable/tiny_container` 是编译副本（原始源码目录在沙箱里不可写）。
每次换版本：
1. 清空副本目录
2. 把新版源码复制进去
3. 重新贴 A1 的 12 个文件改动
4. 补三处构建改动：`signingConfigs`、`noCompress("zst")`、`gradle.properties`
5. 从旧副本复制回 `jniLibs`（21 个 `.so` + 4 个 JNI `.so` + 4 个 ABI 的 `libnative-vnc.so`）
6. 复制三份镜像 assets
7. 编译、三步验证、归档

### 第 6 步：交付

按 `log-version-history.md` 第 5 节「每次交付必须做的事」执行。

## B3. 镜像换版本时

官方镜像在 `https://github.com/tiny-computer/images/releases`，标签如 `260808`。
拿到新镜像后，`build_rootfs_v2.py` 里这些**常量要重新核对**（新版可能变了）：

- 关键文件路径：`xfce4-panel.xml`、`xfce4-keyboard-shortcuts.xml`、`opt/tiny/export.sh`
- `OWNER_UID` / `OWNER_GID` / `OWNER_UNAME` / `OWNER_GNAME`（现在 10258 / `aid_u0_a258`）
- tar 格式（GNU，不是 PAX）
- 面板里要替换的 plugin 编号（现在是 plugin-2 = tasklist）
- deb 依赖（新镜像可能少库，跑 `check_deb_deps.py` 验一遍）

## B4. 最容易出错的四件事

1. **忘了把 `fZoomLocked = false` 贴到新版** → 用户立刻发现缩放又被锁了
2. **AVNC 版本号忘了同步** `libs.versions.toml` → 编进去的是旧 fork，新功能全部消失
3. **`pref_input.xml` 删了官方分类** → 「输入」页直接打不开（11 个 `!!` 等着 NPE）
4. **数据绑定 / 资源名对不上** → 先编译一次看报错，别猜
