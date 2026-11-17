import io

P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk\tiny_osk.py'
s = io.open(P, 'r', encoding='utf-8', newline='').read()

# 1) add the trigger-file constant + CLI toggle helper right after the layout selector line
old = "        self.layout_name = os.environ.get('TINY_OSK_LAYOUT', 'full')"
assert old in s

# 2) append a file-watch timer in main() and the --toggle CLI mode
old_main = """    win = TinyOsk()
    win.show_all()
    win.hide()

    start_hotkey_listener(win)
"""
new_main = """    win = TinyOsk()
    win.show_all()
    win.hide()

    start_hotkey_listener(win)

    # Secondary trigger that never depends on the X keymap: anything inside the
    # container can create TRIGGER_FILE (see /usr/local/bin/tiny-osk-toggle).
    def watch_trigger():
        if os.path.exists(TRIGGER_FILE):
            try:
                os.unlink(TRIGGER_FILE)
            except OSError:
                pass
            win.toggle()
        return True

    GLib.timeout_add(300, watch_trigger)
"""
assert old_main in s
s = s.replace(old_main, new_main, 1)

# 3) define TRIGGER_FILE next to DISPLAY
old_root = "ROOT = x11.XDefaultRootWindow(DISPLAY)"
new_root = "ROOT = x11.XDefaultRootWindow(DISPLAY)\n\nTRIGGER_FILE = os.environ.get('TINY_OSK_TRIGGER', '/tmp/.tiny_osk_toggle')"
assert old_root in s
s = s.replace(old_root, new_root, 1)

# 4) CLI --toggle mode before main()
old_entry = """if __name__ == '__main__':
    main()"""
new_entry = """if __name__ == '__main__':
    if '--toggle' in sys.argv:
        io_open = open
        with io_open(TRIGGER_FILE, 'w') as f:
            f.write('toggle')
        sys.exit(0)
    main()"""
assert old_entry in s
s = s.replace(old_entry, new_entry, 1)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
