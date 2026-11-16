import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\docs-project-notes-keep-forever\build-make-apk.md"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

old6 = """## 6. 换镜像

1. 把新的 `.tar.zst` 复制到
   `build-env-toolchain/ws-gradle-build-copy-deletable/tiny_container/app/src/main/assets/rootfs.tar.zst`
2. 重新跑 `build-apk.ps1`
3. `noCompress.add("zst")` 已在 `app/build.gradle.kts` 里，镜像会以 STORED 存进 APK
   （否则打包极慢且 APK 反而更大）
"""
new6 = """## 6. 换镜像（三个 assets 必须一起换）

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
   `v4-d222bfa6580997c3` 或 5 带 BOM。用下面这行写，避免 PowerShell 加 BOM：

```powershell
[System.IO.File]::WriteAllText("<...>\\assets\\rootfs.stamp", "v5-<sha前16位>", (New-Object System.Text.UTF8Encoding $false))
```

5. 重新跑 `build-apk.ps1`。
6. `noCompress.add("zst")` 已在 `app/build.gradle.kts` 里，镜像与覆盖包都会以 STORED
   存进 APK（否则打包极慢且 APK 反而更大）。
"""
assert old6 in t
t = t.replace(old6, new6, 1)

old7 = """python tools-probe-scripts-deletable\\verify_rootfs_v2.py <out.tar>
```
"""
new7 = """python tools-probe-scripts-deletable\\verify_rootfs_v2.py <out.tar>
python tools-probe-scripts-deletable\\make_patch_tar.py <stock.tar> <out.tar> <patch.tar>
python tools-probe-scripts-deletable\\zst_tar.py <patch.tar> <patch.tar.zst> 19 4
```
"""
assert old7 in t
t = t.replace(old7, new7, 1)

t = t.replace("- `settings.gradle.kts` 里**本地 maven 仓库必须排在 jitpack 之前**，否则会去 jitpack 找\n  不存在的 `3.2.2-tc4v2` 并报 `Could not resolve`",
              "- `settings.gradle.kts` 里**本地 maven 仓库必须排在 jitpack 之前**，否则会去 jitpack 找\n  不存在的 `3.2.2-tc4vN` 并报 `Could not resolve`\n"
              "- 改 AVNC 代码后**必须**先 bump 版本号（`app/build.gradle` 的 `version` 与构建副本\n"
              "  `gradle/libs.versions.toml` 的 `avnc`），两处要一致；不 bump 会命中 Gradle 缓存，\n"
              "  改的东西根本不进 AAR")

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("build doc updated bytes=", len(t))
