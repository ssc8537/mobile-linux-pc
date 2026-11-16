import io, re
base = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\res"
zh_msg = "检测到内置 Linux 镜像有新版本（新增了 Windows 风格任务栏、悬浮键盘、任务管理器等）。\\n\\n推荐选“只更新系统文件”：只覆盖桌面程序、任务栏、悬浮键盘这些系统文件，你的文档、浏览器配置、已安装的软件都保留。\\n\\n只有系统真的出问题时，才选“重新导入”——它会清空容器里的所有个人数据。"
en_msg = "A newer built-in Linux image was detected (Windows-like taskbar, floating keyboard, task manager and more).\\n\\nRecommended: update system files only — desktop programs, taskbar and the floating keyboard are replaced while your documents, browser profile and installed apps are kept.\\n\\nPick Re-import only if the system actually misbehaves; that wipes all personal data inside the container."

for path, msg in ((base + r"\values-zh-rCN\strings.xml", zh_msg),
                  (base + r"\values\strings.xml", en_msg)):
    s = io.open(path, encoding="utf-8").read()
    m = re.search(r'( *)<string name="tc4_reimport_message">.*?</string>', s, re.S)
    assert m, "message not found in " + path
    s = s[:m.start()] + m.group(1) + '<string name="tc4_reimport_message">' + msg + '</string>' + s[m.end():]
    io.open(path, "w", encoding="utf-8", newline="").write(s)
    print("message updated in", path.split("\\")[-2])
