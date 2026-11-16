# -*- coding: utf-8 -*-
"""Pass the caret file path to the VNC activity (sibling of the toggle file)."""
import io

P = (r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain"
     r"\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4"
     r"\ui\page\ContainerMainFragment.kt")
src = io.open(P, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in src else "\n"

old = '''                                val trigger = java.io.File(
                                    requireContext().filesDir, "tmp/.tiny_osk_toggle"
                                )
                                trigger.parentFile?.mkdirs()
                                intent.putExtra("tc4.osk_trigger", trigger.absolutePath)'''
new = '''                                val tmpDir = java.io.File(requireContext().filesDir, "tmp")
                                tmpDir.mkdirs()
                                val trigger = java.io.File(tmpDir, ".tiny_osk_toggle")
                                intent.putExtra("tc4.osk_trigger", trigger.absolutePath)
                                // 容器里的光标位置由 tiny_osk_caret.py 写进同一个 /tmp，
                                // 安卓侧读它来决定“键盘按钮”贴在文本光标旁边。
                                val caret = java.io.File(tmpDir, ".tiny_osk_caret")
                                intent.putExtra("tc4.osk_caret", caret.absolutePath)'''
assert old in src, "intent extras block not found"
src = src.replace(old, new, 1)

io.open(P, "w", encoding="utf-8", newline="").write(src)
print("ok, caret extra:", src.count("tc4.osk_caret"))
