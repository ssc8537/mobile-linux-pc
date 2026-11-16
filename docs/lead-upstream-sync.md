# 04 上游更新了怎么办（合并流程）

> 这篇回答：**官方作者发了新版，我们怎么把自己的功能搬过去，同时不丢东西。**

## 前提：我们的改动分三层，合并难度不同

| 层 | 改在哪 | 合并方式 | 难度 |
|---|---|---|---|
| App 层 | `apps-tiny-container-v423-source` 的 4 个文件 | 手贴几行 | 低 |
| AVNC 层 | 独立的 fork 仓库 | 重新贴补丁 / rebase | 中 |
| 镜像层 | `rootfs-v2.tar.zst` 的重打包脚本 | 改脚本常量重跑 | 低 |

## 标准流程

### 第 1 步：拿官方新版源码

```powershell
$env:HTTPS_PROXY='http://127.0.0.1:7897'
git -c http.sslBackend=openssl clone --depth 1 https://github.com/Cateners/tiny_container.git <新版目录>
```
（`git` 会把 "Cloning into…" 打到 stderr 并返回 1，但目录是好的，别被退出码骗了。）

### 第 2 步：找官方改了什么

对比 `apps-tiny-container-v423-source`（我们手上的 v4.2.3）和新版目录。
重点看：`build.gradle.kts`（版本号、依赖、SDK）、`gradle/libs.versions.toml`（**avnc 版本号会变**）、
`AndroidManifest.xml`、`ui/page/` 下的 Kotlin 文件。

### 第 3 步：把我们的改动贴回去（按 `spec-changes-v2.md` 的清单逐条）

App 层一共 4 个文件，改动都很小，直接照着 V2 的写法贴。
**特别注意** `ContainerMainFragment.kt` 里 `fZoomLocked = false` 那一行 —— 这是 V1 的核心功能，
官方随时可能重构这个分支的写法，贴的时候要确认新的 `ServerProfile` 创建点在哪。

### 第 4 步：处理 AVNC

- 如果官方**没换** `avnc` 版本（还是 `030e6c032e`）：本地 fork 不用动，直接用。
- 如果官方**换了** `avnc` 版本：必须在新的上游 commit 上重做 AVNC 补丁，见下。

### 第 5 步：重建构建副本并编译

`ws-gradle-build-copy-deletable/tiny_container` 是编译用的副本（原始源码目录在
沙箱里不可写，只能编译副本）。每次换版本都要：
1. 清空副本目录
2. 把新版源码复制进去
3. 重新贴 4 个 App 文件的改动
4. 补 `signingConfigs`、`noCompress("zst")`、`gradle.properties` 三处构建改动
5. 从 `jniLibs` 旧副本复制回 21 个 `.so` + 4 个 JNI `.so`
6. 复制 `rootfs-v2.tar.zst` 到 assets
7. 编译、验证、归档

### 第 6 步：交付

按 `log-version-history.md` 的「每次交付必须做的事」执行。

## AVNC 换版本时怎么重做补丁

AVNC 上游：`https://github.com/tiny-computer/avnc`（是 `gauravsarma1992/avnc` 的分支）。
1. 在 jitpack 上确认新版本号对应哪个 commit
2. `git clone` 那个 commit
3. 按 `spec-changes-v2.md` 的 B 节，把 18 个修改 + 5 个新增文件重新贴一遍
4. 关键：**不要碰 native 代码**。`app/build.gradle` 里关掉 `externalNativeBuild`，
   把官方 AAR 里的 `jni/<abi>/libnative-vnc.so` 解出来放进 `jniLibs/`
   （`tools-probe-scripts-deletable/extract_aar_jni.py` 就是干这个的）
5. 编译 → 发布到本地 maven → 改 `libs.versions.toml` 里的 `avnc` 版本号

## 镜像换版本时

官方镜像在 `https://github.com/tiny-computer/images/releases`，标签如 `260808`。
拿到新镜像后，`build_rootfs_v2.py` 里的这些**常量要重新核对**（新版可能变了）：
- 关键文件路径（`xfce4-panel.xml`、`xfce4-keyboard-shortcuts.xml`、`opt/tiny/export.sh`）
- `OWNER_UID/GID/UNAME/GNAME`（现在是 10258 / `aid_u0_a258`）
- tar 格式（GNU，不是 PAX）
- 面板里要替换的 plugin 编号（现在是 plugin-2 = tasklist）
- deb 依赖（新镜像可能少库，跑 `check_deb_deps.py` 验一遍）

## 最容易出错的三件事

1. **忘了把 `fZoomLocked = false` 贴到新版** → 用户立刻会发现缩放又被锁了
2. **AVNC 版本号忘了同步** `libs.versions.toml` → 编译用的是旧 fork，新功能全部消失
3. **数据绑定 / 资源名对不上** → 先编译一次看报错，别猜
