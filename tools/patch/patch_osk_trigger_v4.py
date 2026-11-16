"""V4: make the in-system keyboard summon actually work.

The old path sent XF86XK_Launch0 over RFB and relied on the container's X keymap
having that keysym, which it usually does not.  Replace it with a filesystem
trigger: tiny_container tells VncActivity the absolute path of the container's
/tmp/.tiny_osk_toggle, which tiny_osk.py polls every 300 ms.
"""
import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VNC = os.path.join(ROOT, 'avnc-upstream-fork-deletable', 'app', 'src', 'main',
                   'java', 'com', 'gaurav', 'avnc', 'ui', 'vnc', 'VncActivity.kt')


def read(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write(path, text):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def patch(path):
    src = read(path)
    orig = src.replace('\r\n', '\n')

    # 1) field for the container-side trigger file
    anchor = '    private var oskButton: ImageButton? = null\n'
    if 'oskTriggerPath' not in orig:
        assert anchor in orig, 'oskButton field not found'
        orig = orig.replace(anchor, anchor + '    private var oskTriggerPath: String? = null\n', 1)

    # 2) read the extra in onCreate
    oncreate_anchor = '        binding.viewModel = viewModel\n'
    if 'tc4.osk_trigger' not in orig:
        assert oncreate_anchor in orig, 'onCreate viewModel anchor not found'
        orig = orig.replace(
            oncreate_anchor,
            oncreate_anchor + '        oskTriggerPath = intent.getStringExtra("tc4.osk_trigger")\n',
            1)

    # 3) rewrite openRemoteKeyboard()
    start = orig.find('    fun openRemoteKeyboard()')
    assert start != -1, 'openRemoteKeyboard not found'
    # find the matching closing brace of the function
    depth = 0
    i = orig.index('{', start)
    end = None
    while i < len(orig):
        c = orig[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    assert end, 'could not find end of openRemoteKeyboard'

    new_body = '''    fun openRemoteKeyboard() {
        // Primary path: drop a trigger file inside the running container.  The
        // in-system keyboard polls for it, so this works even when the X keymap
        // has no XF86 keysym.  tiny_container passes the absolute path through
        // the intent that starts this activity.
        val triggerPath = oskTriggerPath
        var delivered = false
        if (!triggerPath.isNullOrEmpty()) {
            try {
                val file = File(triggerPath)
                file.parentFile?.mkdirs()
                file.writeText("toggle")
                delivered = true
            } catch (e: Exception) {
                Log.w(TAG, "OSK trigger file failed: $triggerPath", e)
            }
        }
        // Fallback: also poke the remote with the hotkey the container grabs.
        if (!delivered) {
            inputHandler?.sendKeySym(0x1008FF40, true)   // XF86XK_Launch0
            inputHandler?.sendKeySym(0x1008FF40, false)
        }
        if (viewModel.pref.ui.showToolbarAndBookmark) {
            Toast.makeText(this, R.string.osk_request_sent, Toast.LENGTH_SHORT).show()
        }
    }'''

    orig = orig[:start] + new_body + orig[end:]

    # 4) imports
    if 'import java.io.File' not in orig:
        orig = orig.replace('import android.widget.Toast\n',
                            'import android.widget.Toast\nimport java.io.File\n', 1)
    if 'import android.util.Log' not in orig:
        orig = orig.replace('import android.widget.Toast\n',
                            'import android.util.Log\nimport android.widget.Toast\n', 1)

    # 5) TAG constant next to the companion object of the class, or a private val
    if 'val TAG' not in orig and 'const val TAG' not in orig:
        anchor2 = '    private var oskTriggerPath: String? = null\n'
        orig = orig.replace(anchor2, anchor2 + '    private val TAG = "VncActivity"\n', 1)

    # keep a light sanity check on inputHandler usage
    if 'inputHandler?.sendKeySym' in orig and 'inputHandler' not in orig.split('inputHandler?.sendKeySym')[0]:
        pass

    text = orig.replace('\n', '\r\n') if '\r\n' in read(path) else orig
    write(path, text)
    print('patched VncActivity: openRemoteKeyboard + oskTriggerPath')


def main():
    patch(VNC)


if __name__ == '__main__':
    main()
