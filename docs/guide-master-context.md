# 00 总览与用户习惯（接手先读这一篇）

> 这是「小小容器 / Tiny Container」个人定制项目的 AI 交接文档。
> 你是在 GitHub 仓库 `https://github.com/ssc8537/mobile-linux-pc` 里读到这篇的，说明你要接手。
> **先读完本文件**，再按第 6 节的顺序读其余 4 篇。不要一上手就改代码。

---

## 1. 这个项目是什么

- 上游开源项目：`https://github.com/Cateners/tiny_container`（Kotlin 安卓 App，包名 `com.fct.tc4`）
- 它在手机上用 **PRoot** 跑 Debian 13 + XFCE，再用内嵌的 **AVNC**（VNC 客户端库）把桌面显示出来
- 系统镜像内置在 APK 的 `assets/rootfs.tar.zst` 里，首次启动自动导入，**不联网下载**
- 系统身份：Debian 13.6 (trixie)、XFCE 4.20.4、Firefox ESR 140.13、1147 个包
- 内核串是 proot 伪造的：`Linux localhost 6.17.0-PRoot-Distro ... aarch64`
- **当前交付版本：V6**（键盘相关代码已全部移除的定稿版），见 `log-version-history.md`

### 关键架构事实（最容易判断错的一条）

App 侧代码有**两份**，用途不同：

| 目录 | 内容 | 能不能直接编译 |
|---|---|---|
| `apps-tiny-container-v423-source` | 上游 v4.2.3 原版 + **只有一行** `fZoomLocked = false` | 可编译，但**没有** V2~V6 的任何功能 |
| `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container` | **真正的 V6 基线**，所有改动都在这里 | 这是实际编译用的副本 |

> 沙箱里原始源码目录不可写，所以一直编副本。V2 以后所有 App 侧改动都只存在于副本里。
> 仓库 `source/app/` 已经把副本的 12 个文件同步过来了，是准确的 V6 基线。

## 2. 用户明确说过的偏好（务必遵守）

1. **界面要粉色系**（淡粉、能看清、要漂亮），这是他的审美基准。
2. **要 Windows 的使用习惯**，不喜欢 Linux 原生那套；鼠标、任务栏、快捷键都按 Windows 来。
3. **讨厌误触**。绝对不要用「双击」当任何功能的触发方式（会误开应用）。
4. **必须有回退版本**。每次交付 APK 都要进版本归档，出错能退回上一版。
5. **文档用中文写**（`.md` 不影响代码，他看得懂中文）。
6. **交付要能直接装**：APK 必须已签名，且所有版本用同一把证书，能互相覆盖安装。
7. **不要自作主张加功能**。清单里没提到的默认按他说的做；拿不准就先问，不要直接写。
8. **先探讨再动手**。大功能要先给方案和取舍，他确认后才写代码。
9. **不要往 GitHub 推送**，除非他明确下命令说「上传」。
10. 他的手机：iQOO Neo 10（骁龙 8 Gen 3）。也提到想在一体机（触摸大屏）上用。
11. 他不是程序员，**无法自己调试**：你写代码 → 编 APK → 他装上试用 → 回报现象 → 你改。
    所以他描述的是「现象」，你要负责翻译成代码位置。

## 3. 文件命名规则（他的硬性要求）

- **全部英文**，不要中文目录名 / 文件名（唯一例外见下）。
- 格式：`<5 个字符的专业前缀>-<一眼能看懂的解释>-<权限标记>`
  - 例：`build-env-toolchain`、`refs-reference-assets-deletable`、`docs-project-notes-keep-forever`
- 权限标记只有两种：
  - `-deletable`（可删除：一次性工具、缓存、中间产物）
  - `-keep-forever`（永久保留：交付物、文档、签名密钥）
- 例外：用户自己建的 `黑客键盘-优秀案例2`（名字里写了禁止改名），不要动它。

## 4. 仓库里有什么

```
source/app/       V6 基线 App 源码（真基线，不是上游原版）
source/avnc/      改过的 AVNC 库源码（Kotlin 部分，版本 3.2.2-tc4v10）
tools/build/      构建脚本 env.ps1 / build-avnc.ps1 / build-apk.ps1 / install-sdk35.ps1
tools/patch/      改源码用的 Python 脚本，每个改动点一个，可重放
docs/             这 5 篇交接文档
release/          guide-usage-zh.md（使用说明）、readme-versions-zh.md（版本历史）
history-versions/ 历史版本汇总（SHA-256 + 回退方法）
```

**APK 不在 git 里**（每个约 760 MB，git 存不下），全部在 Releases：
`https://github.com/ssc8537/mobile-linux-pc/releases/tag/vN`（N = 1~6），v6 是最新版。

## 5. 交付一条新 APK 要做什么

1. 改 `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container`（App 侧）
   和/或 `avnc-upstream-fork-deletable`（AVNC 侧）和/或镜像重打包脚本
2. 编 AVNC → 编 APK（见 `build-and-upstream-sync.md`）
3. 三步验证：`apksigner verify --print-certs`、`zipalign -c -p 4`、dex 关键字检查
4. 归档到 `build-env-toolchain/apks-archive-keep-forever/v<N>-<说明>-<日期>/`
5. 在 `readme-versions-zh.md`、`log-version-history.md` 追加条目（文件、字节数、SHA-256、改了什么）
6. 只有在用户明确说「上传」时才推 GitHub / 发 Release

## 6. 文档阅读顺序

| 顺 | 文件 | 这篇解决什么 |
|---|---|---|
| 1 | `guide-master-context.md`（本篇） | 项目是什么、用户脾气、命名规则、从哪开始 |
| 2 | `log-version-history.md` | 交付过哪 6 个版本、各自改了什么、怎么回退、签名参数 |
| 3 | `spec-changes-and-rootfs.md` | 相对上游改了哪些文件（带行号）+ 镜像内部结构速查 |
| 4 | `build-and-upstream-sync.md` | 从零编出 APK、这台机器的坑、上游更新怎么合并 |
| 5 | `archive-research-and-plans.md` | 历史调研与被否决的方案（**只作参考，不要照做**） |

## 7. 已作废、不要再往回加的东西

- **虚拟键盘 / 悬浮键盘 / 黑客键盘移植 / 光标旁键盘按钮 / 三指呼出键盘**：
  用户在 m03615 明确说「键盘不写了，全部删掉」，V6 已彻底移除。别自作主张恢复。
- **把手机容器快照打进 APK** 的方案：用户 m00917 亲自否决（导出会碰到设备上的真实数据）。
- **Ctrl+C / Ctrl+V 移植**：用户取消（GUI 程序本来就支持，只有终端要 Ctrl+Shift+C/V）。

细节与理由见 `archive-research-and-plans.md`。
