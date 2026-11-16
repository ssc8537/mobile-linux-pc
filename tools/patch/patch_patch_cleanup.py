# -*- coding: utf-8 -*-
"""Add a defensive cleanup of every keyboard artefact to applyImagePatch().

The patch tarball only adds/overwrites files, so an existing container that
already received the V5 keyboard payload would keep its autostart entries and
binaries.  Remove them explicitly before extracting.
"""
import io
import os

R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
F = os.path.join(R, "build-env-toolchain", "ws-gradle-build-copy-deletable", "tiny_container",
                 "app", "src", "main", "java", "com", "fct", "tc4", "ui", "page",
                 "ContainerManageViewModel.kt")

old = '''                execShell {
                    val patch = $$"""
                        export CONTAINER_DIR=$${app.dataDir}/$$code
                        mkdir -p $CONTAINER_DIR
                        $BIN_DIR/proot --link2symlink $BIN_DIR/tar -xf $CACHE_DIR/rootfs.patch.tar.zst -C $CONTAINER_DIR --delay-directory-restore --preserve-permissions
                        $BIN_DIR/rm -f $CACHE_DIR/rootfs.patch.tar.zst
                    """.trimIndent()
                    Global.setupEnvironment()
                    Global.sendCommand(patch)
                    Global.sendCommand("exit")
                }
'''

new = '''                execShell {
                    val patch = $$"""
                        export CONTAINER_DIR=$${app.dataDir}/$$code
                        mkdir -p $CONTAINER_DIR
                        # 早期版本曾经装过悬浮键盘，这里把它的残留（自启项、二进制、
                        # 日志）一并清掉，否则开机自启会去拉起一个已经不存在的程序。
                        rm -rf "$CONTAINER_DIR/usr/local/share/tiny-osk"
                        rm -f "$CONTAINER_DIR/usr/local/bin/tiny-osk" \\
                              "$CONTAINER_DIR/usr/local/bin/tiny-osk-toggle" \\
                              "$CONTAINER_DIR/usr/local/bin/tiny-osk-caret" \\
                              "$CONTAINER_DIR/home/tiny/.config/autostart/tiny-osk.desktop" \\
                              "$CONTAINER_DIR/home/tiny/.config/autostart/tiny-osk-caret.desktop" \\
                              "$CONTAINER_DIR/usr/share/applications/tiny-osk.desktop"
                        rm -f "$CONTAINER_DIR/tmp/.tiny_osk_log" "$CONTAINER_DIR/tmp/.tiny_osk.log" \\
                              "$CONTAINER_DIR/tmp/.tiny_osk_caret" "$CONTAINER_DIR/tmp/.tiny_osk_toggle"
                        $BIN_DIR/proot --link2symlink $BIN_DIR/tar -xf $CACHE_DIR/rootfs.patch.tar.zst -C $CONTAINER_DIR --delay-directory-restore --preserve-permissions
                        $BIN_DIR/rm -f $CACHE_DIR/rootfs.patch.tar.zst
                    """.trimIndent()
                    Global.setupEnvironment()
                    Global.sendCommand(patch)
                    Global.sendCommand("exit")
                }
'''

raw = io.open(F, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
if old not in src:
    raise SystemExit("applyImagePatch execShell block not found verbatim")
src = src.replace(old, new, 1)

# the doc comment still advertises the keyboard: reword it
src = src.replace(
    "     * 它只包含我们这次新增/修改的文件（任务栏插件、任务管理器、截图、剪贴板、\n"
    "     * 悬浮键盘、修好的 export.sh 等）。这里把它解压到已有容器目录上，\n",
    "     * 它只包含我们这次新增/修改的文件（任务栏插件、任务管理器、截图、剪贴板、\n"
    "     * 修好的 export.sh 等）。这里把它解压到已有容器目录上，\n")

out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
print("patched %d bytes (eol=%s)" % (len(out.encode("utf-8")), "crlf" if crlf else "lf"))
if "悬浮键盘" in out:
    left = [l.strip() for l in out.splitlines() if "悬浮键盘" in l]
    raise SystemExit("doc mention left: %s" % left)
