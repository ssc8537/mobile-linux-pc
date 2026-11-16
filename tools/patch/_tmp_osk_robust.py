import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk\tiny_osk.py"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

old = """def main():
    provider = Gtk.CssProvider()"""
new = """def _ensure_display():
    \"\"\"GTK dies with an unhelpful message when DISPLAY is missing. XFCE sessions
    normally export it, but autostart entries can lose it, so guess from the
    sockets in /tmp/.X11-unix before giving up.\"\"\"
    if os.environ.get('DISPLAY'):
        return os.environ['DISPLAY']
    base = '/tmp/.X11-unix'
    try:
        for name in sorted(os.listdir(base)):
            if name.startswith('X') and name[1:].isdigit():
                os.environ['DISPLAY'] = ':' + name[1:]
                return os.environ['DISPLAY']
    except OSError:
        pass
    os.environ.setdefault('DISPLAY', ':6')
    return os.environ['DISPLAY']


def _log(msg):
    try:
        with open('/tmp/.tiny_osk.log', 'a') as f:
            f.write('[tiny_osk] ' + str(msg) + '\\n')
    except OSError:
        pass


def main():
    disp = _ensure_display()
    _log('main start, DISPLAY=%s, pid=%d' % (disp, os.getpid()))
    provider = Gtk.CssProvider()"""
assert old in t, "main() anchor not found"
t = t.replace(old, new, 1)

old2 = """    win = TinyOsk()
    win.show_all()
    win.hide()

    start_hotkey_listener(win)"""
new2 = """    win = TinyOsk()
    win.show_all()
    win.hide()
    _log('window created, hidden, layout=%s docked=%s' % (win.layout_name, win.docked))

    try:
        start_hotkey_listener(win)
        _log('hotkey listener installed (XF86Launch0 / F9)')
    except Exception as exc:      # never let the hotkey break the keyboard
        _log('hotkey listener failed: %r' % (exc,))"""
assert old2 in t, "win creation anchor not found"
t = t.replace(old2, new2, 1)

old3 = """    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()"""
new3 = """    signal.signal(signal.SIGINT, signal.SIG_DFL)
    _log('entering Gtk.main()')
    Gtk.main()"""
assert old3 in t, "Gtk.main anchor not found"
t = t.replace(old3, new3, 1)

old4 = """if __name__ == '__main__':
    if '--toggle' in sys.argv:"""
new4 = """if __name__ == '__main__':
    try:
        if '--toggle' in sys.argv:
            _ensure_display()
            with open(TRIGGER_FILE, 'w') as f:
                f.write('toggle')
            _log('trigger file written by --toggle')
            sys.exit(0)
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        _log('FATAL:\\n' + traceback.format_exc())
        raise
"""
assert old4 in t, "dunder main anchor not found"
i = t.index(old4)
# drop the original trailing block entirely and re-add ours
t = t[:i] + new4
io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("tiny_osk.py hardened, eol=", repr(eol), "lines=", t.count("\n")+1)
