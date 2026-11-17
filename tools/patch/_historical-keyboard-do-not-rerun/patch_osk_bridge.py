"""V4: a reliable bridge so the Android side can summon the in-system keyboard.

The keyboard runs *inside* the Linux container, so AVNC (a library) cannot start
it directly.  tiny_container does have a live shell inside the container, so it
registers a callback here; AVNC invokes it when the user taps the keyboard
button.  The file trigger stays as a second, independent path.
"""
import io
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AVNC = os.path.join(ROOT, 'avnc-upstream-fork-deletable')
BRIDGE = os.path.join(AVNC, 'app', 'src', 'main', 'java', 'com', 'gaurav', 'avnc',
                      'util', 'OskBridge.kt')
VNC = os.path.join(AVNC, 'app', 'src', 'main', 'java', 'com', 'gaurav', 'avnc',
                   'ui', 'vnc', 'VncActivity.kt')

BRIDGE_SRC = '''package com.gaurav.avnc.util

/**
 * Local fork: lets the host application start the on-screen keyboard that lives
 * inside its Linux container.
 *
 * AVNC is published as a library and has no access to the container shell, so the
 * host app registers [summon] while a desktop session is running.  If no handler
 * is registered the caller falls back to the trigger file / keysym path.
 */
object OskBridge {

    /** Invoked when the user asks for the on-screen keyboard. May run off the UI thread. */
    @Volatile
    var summon: (() -> Unit)? = null
}
'''


def read(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write(path, text, eol):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text if eol == '\n' else text.replace('\n', '\r\n'))


def main():
    with io.open(BRIDGE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(BRIDGE_SRC)
    print('wrote OskBridge.kt')

    src = read(VNC)
    eol = '\r\n' if '\r\n' in src[:2000] else '\n'
    t = src.replace('\r\n', '\n')

    if 'com.gaurav.avnc.util.OskBridge' not in t:
        t = t.replace('import com.gaurav.avnc.ui.vnc.input.InputHandler\n',
                      'import com.gaurav.avnc.ui.vnc.input.InputHandler\nimport com.gaurav.avnc.util.OskBridge\n', 1)

    old = '''        // Fallback: also poke the remote with the hotkey the container grabs.
        if (!delivered) {
            inputHandler?.sendKeySym(0x1008FF40, true)   // XF86XK_Launch0
            inputHandler?.sendKeySym(0x1008FF40, false)
        }'''
    new = '''        // Second path: the host app owns a shell inside the container, so let it
        // launch (or toggle) the keyboard directly. This is the most reliable one.
        val summon = OskBridge.summon
        if (summon != null) {
            try {
                summon.invoke()
                delivered = true
            } catch (e: Exception) {
                Log.w(TAG, "OSK summon hook failed", e)
            }
        }
        // Last resort: poke the remote with the hotkey the container grabs.
        if (!delivered) {
            inputHandler?.sendKeySym(0x1008FF40, true)   // XF86XK_Launch0
            inputHandler?.sendKeySym(0x1008FF40, false)
        }'''
    assert old in t, 'fallback block not found'
    t = t.replace(old, new, 1)

    write(VNC, t, eol)
    print('patched VncActivity: OskBridge.summon')


if __name__ == '__main__':
    main()
