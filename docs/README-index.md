# 交接文档索引（给下一个接手的 AI）

5 篇，按顺序读。**先读 00**，不要跳。

| 顺 | 文件 | 这篇解决什么 | 大小 |
|---|---|---|---|
| 1 | [00 总览与用户习惯](guide-master-context.md) | 项目是什么、用户脾气与硬性要求、命名规则、从哪开始、已作废清单 | ~1100 汉字 |
| 2 | [01 版本历史](log-version-history.md) | 交付过哪 6 个版本、各自改了什么、签名参数、怎么回退、交付清单 | ~1270 汉字 |
| 3 | [02 改动清单与镜像结构](spec-changes-and-rootfs.md) | 相对上游改了哪些文件（带行号）+ 容器内部结构速查 + 重打包命令 | ~1870 汉字 |
| 4 | [03 编译与上游同步](build-and-upstream-sync.md) | 从零编出 APK、这台机器的 10 个坑、官方更新后怎么合并 | ~1520 汉字 |
| 5 | [04 历史调研与被否决方案](archive-research-and-plans.md) | 为什么这么设计、哪些方案被用户否决了（**只作参考，别照做**） | ~2590 汉字 |

## 三条最容易犯的错

1. **以为 `apps-tiny-container-v423-source` 是当前基线** —— 不是。它只有
   `fZoomLocked = false` 一行改动；真正的 V6 基线是
   `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container`（或仓库的 `source/app/`）。
2. **改完 AVNC 忘了 bump 版本号** —— 两处（`app/build.gradle` 的 `version` 与
   `libs.versions.toml` 的 `avnc`）都要改且一致，否则 Gradle 缓存会配上旧 AAR，改的内容静默丢失。
3. **往键盘功能上加代码** —— 用户 m03615 已明确全部删除，别再恢复。

## 归档

`_retired-keep-forever/` 里是本文档集的前一版（8 篇拆分版本），内容已被上表取代，
但保留了更早期的行号细节。只在需要考古时查。
