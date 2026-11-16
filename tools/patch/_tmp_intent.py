import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\page\ContainerMainFragment.kt"
with io.open(p, "r", encoding="utf-8", newline="") as f:
    s = f.read()
t = s.replace("\r\n", "\n")
old = """                            val intent = createVncIntent(requireContext(), profile)
                            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT)"""
new = """                            val intent = createVncIntent(requireContext(), profile)
                            // 把容器内的键盘触发文件路径交给 VNC 界面：点小键盘按钮时
                            // 由安卓侧直接写这个文件，容器里的悬浮键盘每秒轮询一次即可弹出。
                            // 走文件而不是按键，是因为容器 X keymap 不一定有 XF86 键位。
                            runCatching {
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
                            }
                            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT)"""
assert old in t, "anchor not found"
t = t.replace(old, new, 1)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(t)
print("intent extra added")
