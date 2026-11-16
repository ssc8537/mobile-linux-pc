import io
F = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\page\ContainerManageViewModel.kt"
raw = io.open(F, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
src = raw.replace("\r\n", "\n")
src = src.replace('                        rm -rf "$CONTAINER_DIR/usr/local/share/tiny-osk"',
                  '                        $BIN_DIR/rm -rf "$CONTAINER_DIR/usr/local/share/tiny-osk"')
src = src.replace('                        rm -f "$CONTAINER_DIR/usr/local/bin/tiny-osk" \\',
                  '                        $BIN_DIR/rm -f "$CONTAINER_DIR/usr/local/bin/tiny-osk" \\')
src = src.replace('                        rm -f "$CONTAINER_DIR/tmp/.tiny_osk_log" "$CONTAINER_DIR/tmp/.tiny_osk.log" \\',
                  '                        $BIN_DIR/rm -f "$CONTAINER_DIR/tmp/.tiny_osk_log" "$CONTAINER_DIR/tmp/.tiny_osk.log" \\')
out = src.replace("\n", "\r\n") if crlf else src
io.open(F, "w", encoding="utf-8", newline="").write(out)
print("ok", len(out.encode("utf-8")))
