import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\page\ContainerMainViewModel.kt"
s = io.open(p, encoding="utf-8", newline="").read()
t = s.replace("\r\n", "\n")

if "com.gaurav.avnc.util.OskBridge" not in t:
    t = t.replace("import com.fct.tc4.ui.misc.UpdateResult\n",
                  "import com.fct.tc4.ui.misc.UpdateResult\nimport com.gaurav.avnc.util.OskBridge\n", 1)

old = """        Global.setupEnvironment()
        val containerDir = "${app.dataDir.absolutePath}/$code\""""
new = """        Global.setupEnvironment()
        // 悬浮键盘跑在容器里面，AVNC 自己起不来，所以把"往容器 shell 里敲一条命令"
        // 这个能力注册给它。点小键盘按钮时就会执行 tiny-osk-toggle。
        OskBridge.summon = {
            Global.sendCommand("tiny-osk-toggle")
        }
        val containerDir = "${app.dataDir.absolutePath}/$code\""""
assert old in t, "setupEnvironment anchor not found"
t = t.replace(old, new, 1)

old2 = """    override fun onCleared() {"""
new2 = """    override fun onCleared() {
        OskBridge.summon = null"""
assert old2 in t, "onCleared anchor not found"
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bridge registered")
