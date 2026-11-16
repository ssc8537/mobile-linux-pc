# mobile-linux-pc

Android 上的 Linux 桌面环境定制版（基于开源项目 [Cateners/tiny_container](https://github.com/Cateners/tiny_container)）。

> 这是个人自用定制版，不是官方项目。原项目版权归原作者所有，遵循 GPL-3.0。

## 这是什么

tiny_container 在 Android 上通过 PRoot 运行 Debian 13 + XFCE 桌面，并用内置的 AVNC（VNC 客户端）
显示画面。这个仓库保存的是**我自己的定制版本**的源码改动、构建脚本、交接文档，
以及每一版编译好的 APK（APK 太大，全部放在 [Releases](../../releases) 页面，不在 git 里）。

## 下载 APK

**不要 clone 这个仓库来找 APK** —— APK 每个约 760 MB，GitHub 不允许这么大的文件进 git。

请到 **[Releases](../../releases)** 页面下载：

| 版本 | 说明 |
|---|---|
| **最终版 v6** | 当前使用版本，功能最全，键盘相关代码已全部移除 |
| v5 及更早 | 历史版本，仅供回退 |

每个 Release 里都附带对应的 `guide-usage-zh.md`（使用说明）和 `readme-versions-zh.md`（版本历史）。

**历史版本汇总表（含 SHA-256 与回退方法）→ [history-versions/](history-versions/README-历史版本说明.md)**

## 和官方版的区别

一句话：**桌面能用的功能更多，指针手感可调，但去掉了虚拟键盘。**

### 应用内（设置 AVNC → 输入 / 指针）
- 自由缩放：进入桌面不再默认锁定缩放（官方默认锁定）
- 鼠标加速开关 + 加速强度 1~8 倍可调
- 慢速移动基准速度 10~100% 可调
- 滚轮速度 1~9 档可调（档位 3 = 官方原值）
- 指针大小 50~300%（默认 150%）
- 指针颜色（开关 + 取色板，粉色优先）
- 缩放误触保护：第一次双指缩放只提示，1.2 秒内再缩放才生效
- 设置页新增「停止限制子进程」一键跳转（解决容器启动约 10 秒后被系统杀掉）

### 桌面内
- 任务栏换成 docklike（Windows 风格，同程序多窗口合并，可固定，默认不固定任何程序）
- 补上任务管理器（Ctrl+Shift+Esc）、截图（Print）、剪贴板历史（Super+V）
- 修正导出脚本：导出容器不再删除 `~/.mozilla` 等个人数据
- 镜像升级改为静默增量覆盖，不用再回答对话框

详见 [docs/](docs/) 下的交接文档。

## 仓库结构

```
source/app/     上游 tiny_container v4.2.3 源码（未改动，作对照基线）
source/avnc/    我们改过的 AVNC 库源码（Kotlin 部分）
tools/build/    构建脚本（env.ps1 / build-avnc.ps1 / build-apk.ps1 / install-sdk35.ps1）
tools/patch/    改源码用的 Python 脚本（每个改动点一个脚本，可重放）
docs/           AI 交接文档（先读 guide-master-context.md）
release/        使用说明与版本历史的纯净副本
```

## 怎么重新编译

见 [docs/build-make-apk.md](docs/build-make-apk.md)。要点：

1. 装 JDK 21 + Android SDK（platform 37、build-tools 36.0.0、NDK 28.2.13676358）+ Gradle 9.4.1
2. `source/avnc` 需要 Gradle 8.13，先 `publishReleasePublicationToLocalForkRepository`
3. 把 rootfs 镜像放到 `app/src/main/assets/`（三个文件必须一起换）
4. `gradle assembleRelease`

## 签名

所有版本共用一把 keystore（alias `tc4`，口令 `tc4zoom`），所以可以互相覆盖安装。
密钥副本在 Releases 的 `_signing-keys` 资产里。

## 许可证

GPL-3.0，与上游一致。