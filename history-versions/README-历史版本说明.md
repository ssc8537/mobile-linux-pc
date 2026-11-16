# 历史版本（HISTORY VERSIONS）

> **这里只是归档说明。APK 文件不在 git 里，请到 [Releases](../../releases) 页面下载。**

GitHub 对 git 仓库里的单个文件限制 100 MB，而我们的 APK 每个约 760 MB，
所以**全部 APK 都放在 Releases 页面**。这个文件夹记录每一版改了什么、什么时候用。

## 当前使用版本

**v6 最终版** -> https://github.com/ssc8537/mobile-linux-pc/releases/tag/v6

## 全部版本

| 版本 | 下载 | 大小 | 状态 | 一句话 |
|---|---|---|---|---|
| v6 | [v6](../../releases/tag/v6) | 761,832,607 B | **当前使用** | 键盘相关代码全部移除的定稿版 |
| v5 | [v5](../../releases/tag/v5) | 761,875,619 B | 历史 | 修「设置 AVNC -> 输入」崩溃；键盘按钮跟随文本光标；移植 Hacker's Keyboard 布局 |
| v4 | [v4](../../releases/tag/v4) | 761,867,363 B | 历史 | 修复「覆盖安装后桌面功能不出现」根因；增量镜像补丁；数字标签；指针颜色开关 |
| v3 | [v3](../../releases/tag/v3) | 761,288,905 B | 历史 | 键盘设置对话框；剪贴板快捷键 Super+V |
| v2 | [v2](../../releases/tag/v2) | 761,267,121 B | 历史 | 鼠标加速/滚轮/指针颜色大小/误触缩放/任务栏/任务管理器/截图/剪贴板 |
| v1 | [v1](../../releases/tag/v1) | 957,130,197 B | 历史 | **自由缩放**（唯一功能）；其余与官方 v4.2.3 一致 |

## SHA-256

```
v6  81DB5DAC13B16B432E2F68077A193B583E6F647D0B0E93923784DD6ED00A4D47
v5  B2CD44F9F678364D3F6D334FDA33AC06A8CB985C48EE2477A54E12A12B51E6A3
v4  95DDD15EB9F6709EC49985B7EF69B44788B1932387DCFE1078880D13960E4527
v3  3EEE8A5CCD85C635BF636152D87D1F64F1DED0F607A45602867A4ABD74455AD4
v2  F964A464EABE6198BBDDF576F825AE4666E1CF3DD8BD9370D36A5C3C0CFEB135
v1  05EE9EF4453EB63D955E82288E8B8237F51D61866EF31A9A4A70DEEACAAB51DA
```

在手机上校验：`sha256sum 文件名.apk`

## 怎么回退

所有版本共用同一把签名证书（alias `tc4`，口令 `tc4zoom`），所以：

1. 到 Releases 下载想回退的那个版本的 APK
2. 直接安装（**不用先卸载**，会覆盖当前版本）

注意：回退只换 APK。如果你的容器已经用新版镜像导入过，容器数据不会跟着回退
（个人文件、书签、密码都还在，只是桌面配置可能仍是新的）。

## 为什么用 Release 而不是直接提交文件

GitHub 对 git 仓库里的单个文件限制 100 MB，APK 有 760 MB，提交必然失败。
Release 页面每个资产上限 2 GB，公开仓库不限总量，而且下载时有进度条、有校验值，
比 clone 一个大仓库方便得多。上游的 tiny_container 也是这么做的。
