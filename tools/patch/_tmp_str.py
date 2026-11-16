import io, os
base = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\res"
zh = {
 "tc4_reimport_patch": "只更新系统文件（推荐，保留个人数据）",
 "tc4_reimport_message": "检测到内置 Linux 镜像有新版本。\n\n推荐选择“只更新系统文件”：只覆盖桌面程序、任务栏、悬浮键盘等系统文件，你的文档、浏览器配置、已装软件都保留。\n\n如果系统出现异常，再选择“彻底重新导入”，但那会清空容器里的所有个人数据。",
}
en = {
 "tc4_reimport_patch": "Update system files only (recommended, keeps your data)",
 "tc4_reimport_message": "A newer built-in Linux image was detected.\n\nRecommended: update system files only — desktop apps, taskbar and the floating keyboard are replaced; your documents, browser profile and installed apps are kept.\n\nUse “Re-import” only if the system misbehaves; it wipes all personal data inside the container.",
}
def patch(path, table, anchor):
    s = io.open(path, encoding="utf-8").read()
    lines = []
    for k, v in table.items():
        if ('name="%s"' % k) in s:
            print("exists:", k)
            continue
        lines.append('    <string name="%s">%s</string>' % (k, v))
    if not lines:
        return
    assert anchor in s, anchor
    ins = "\n".join(lines) + "\n"
    s = s.replace(anchor, ins + anchor, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", os.path.basename(path))

patch(os.path.join(base, "values-zh-rCN", "strings.xml"), zh, '    <string name="tc4_reimport_title">')
patch(os.path.join(base, "values", "strings.xml"), en, '    <string name="tc4_reimport_title">')
