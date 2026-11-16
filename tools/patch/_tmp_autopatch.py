import io, os, re

BASE = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
BUILD = os.path.join(BASE, r"build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container")
ACT = os.path.join(BUILD, r"app\src\main\java\com\fct\tc4\ui\main\MainActivity.kt")

with open(ACT, 'rb') as f:
    raw = f.read()
src = raw.decode('utf-8')
eol = '\r\n' if '\r\n' in src else '\n'
s = src.replace('\r\n', '\n')

# Replace the interactive prompt with an automatic, data-preserving patch.
old_call = """        if (Global.installedContainers.isNotEmpty() && Global.isBuiltInImageOutdated()) {
            askReimportImage()
            return
        }"""
new_call = """        if (Global.installedContainers.isNotEmpty() && Global.isBuiltInImageOutdated()) {
            // Local fork: apply the additive image patch silently so new desktop
            // features appear without the user having to answer a dialog.
            autoPatchImageIfOutdated()
        }"""
assert old_call in s, 'call site not found'
s = s.replace(old_call, new_call, 1)

# Append the new method right before askReimportImage's declaration.
anchor = "    private fun askReimportImage() {"
assert anchor in s, 'askReimportImage not found'

new_method = '''    /**
     * Local fork: silently overlay the new system files onto the existing container.
     *
     * The overlay only adds/replaces system files (docklike taskbar, on-screen
     * keyboard, task manager, screenshot tool, clipboard manager) and never
     * touches /home, so the user's documents and browser profile survive.
     */
    private var autoPatchStarted = false

    private fun autoPatchImageIfOutdated() {
        if (autoPatchStarted) return
        autoPatchStarted = true
        val containerViewModel: ContainerManageViewModel by viewModels()
        containerViewModel.applyImagePatch()
    }

'''
s = s.replace(anchor, new_method + anchor, 1)

out = s.replace('\n', eol)
with open(ACT, 'wb') as f:
    f.write(out.encode('utf-8'))
print('MainActivity patched, eol=%r' % eol)
print('applyImagePatch calls:', s.count('applyImagePatch()'))
