import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\page\ContainerMainFragment.kt"
with io.open(p, "r", encoding="utf-8", newline="") as f:
    s = f.read()
old = """                            runCatching {
                                val code = arguments?.getString("code") ?: ""
                                if (code.isNotBlank()) {
                                    val trigger = java.io.File(
                                        requireContext().filesDir, "tmp/.tiny_osk_toggle"
                                    )
                                    val hostPath = java.io.File(
                                        requireContext().dataDir, "$code/tmp/.tiny_osk_toggle"
                                    ).absolutePath
                                    intent.putExtra("tc4.osk_trigger", hostPath)
                                    trigger.parentFile?.mkdirs()
                                }
                            }"""
new = """                            runCatching {
                                // 容器里的 /tmp 通过 proot 绑到了 filesDir/tmp
                                // （和上面 VNC 的 UnixSocket 用的是同一个目录）。
                                val trigger = java.io.File(
                                    requireContext().filesDir, "tmp/.tiny_osk_toggle"
                                )
                                trigger.parentFile?.mkdirs()
                                intent.putExtra("tc4.osk_trigger", trigger.absolutePath)
                            }"""
assert old in s, "block not found"
s = s.replace(old, new, 1)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(s)
print("trigger path fixed")
