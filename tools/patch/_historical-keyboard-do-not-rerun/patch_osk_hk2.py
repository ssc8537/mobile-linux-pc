# -*- coding: utf-8 -*-
"""Finish the Hacker's Keyboard port inside tiny_osk.py.

1. `_rows()` delegates to `_hk_rows()` (the old hand-written tables are gone).
2. `_fill_grid()` unpacks HK's 6-tuple cells and sizes keys by percentage.
3. `self.shift_locked` is initialised and toggled by the Shift key, so the
   symbol layer has a shifted variant just like HK's kbd_symbols_shift.xml.
4. HK's popup characters are reachable by long-press on a key.
"""
import io
import os

BASE = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk"
P = os.path.join(BASE, "tiny_osk.py")
src = io.open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- 1. _rows()
old = """    def _rows(self):
        if self.fn_mode:
            return FULL_LAYOUT
        if self.symbol_mode:
            return SYMBOL_LAYOUT
        if self.layout_name == 'hackers':
            return HACKERS_LAYOUT
        return FULL_LAYOUT
"""
new = """    def _rows(self):
        return self._hk_rows()
"""
assert old in src, "old _rows body not found"
src = src.replace(old, new, 1)

# ------------------------------------------------- 2. state: shift_locked
old_state = "        self.symbol_mode = False\n        self.fn_mode = False\n"
assert old_state in src, "state block not found"
src = src.replace(
    old_state,
    "        self.symbol_mode = False\n        self.fn_mode = False\n        self.shift_locked = False\n",
    1,
)

# ------------------------------------------------- 3. _fill_grid: 6-tuple cells
old_fill = """        for row in self._rows():
            hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            hb.set_homogeneous(False)
            for key in row:
                label, sym, width, role = key
                btn = Gtk.Button()
                btn.set_can_focus(False)
                btn.get_style_context().add_class('tk')
                btn.set_size_request(int(self.key_height * 1.15 * width), self.key_height)
                btn.add(Gtk.Label(label=label))
                if role == 'mod':
                    btn.connect('clicked', self._on_mod, btn, sym)
                elif role == 'layer':
                    if label == 'Fn':
                        btn.connect('clicked', self._on_fn, btn)
                    else:
                        btn.connect('clicked', self._on_layer, btn)
                else:
                    btn.connect('clicked', self._on_key_click, sym)
                hb.pack_start(btn, False, False, 0)
            self.grid_holder.pack_start(hb, False, False, 0)
        self.grid_holder.show_all()
"""
new_fill = """        for row in self._rows():
            hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            hb.set_homogeneous(True)          # every key shares the row equally
            for cell in row:
                # HK cell: (label, keysym, role, shift_label, width_pct, popup)
                label, sym, width, role, shift_label, popup = cell
                shown = label
                if self.shift_locked and shift_label:
                    shown = shift_label
                btn = Gtk.Button()
                btn.set_can_focus(False)
                btn.get_style_context().add_class('tk')
                btn.set_size_request(max(18, int(width * 3)), self.key_height)
                btn.add(Gtk.Label(label=shown))
                if popup:
                    btn.set_tooltip_text(popup)
                    btn.connect('button-press-event', self._on_key_long_press,
                                sym, popup)
                if role == 'mod':
                    btn.connect('clicked', self._on_mod, btn, sym)
                elif role == 'layer':
                    if label == 'Fn':
                        btn.connect('clicked', self._on_fn, btn)
                    else:
                        btn.connect('clicked', self._on_layer, btn)
                else:
                    btn.connect('clicked', self._on_key_click, sym)
                hb.pack_start(btn, True, True, 0)
            self.grid_holder.pack_start(hb, False, False, 0)
        self.grid_holder.show_all()
"""
assert old_fill in src, "_fill_grid body not found"
src = src.replace(old_fill, new_fill, 1)

# ------------------------------------------- 4. Shift toggles shift_locked
old_mod = """    def _on_mod(self, btn, sym):
        kc = keycode(keysym(sym))
        if kc in self.mod_keys:
            self.mod_keys.remove(kc)
            fake(kc, False)
            btn.get_style_context().remove_class('mod-on')
        else:
            self.mod_keys.append(kc)
            fake(kc, True)
            btn.get_style_context().add_class('mod-on')
"""
new_mod = """    def _on_mod(self, btn, sym):
        kc = keycode(keysym(sym))
        if kc in self.mod_keys:
            self.mod_keys.remove(kc)
            fake(kc, False)
            btn.get_style_context().remove_class('mod-on')
        else:
            self.mod_keys.append(kc)
            fake(kc, True)
            btn.get_style_context().add_class('mod-on')
        # HK shows the shifted legends while Shift is latched.
        if sym in ('Shift_L', 'Shift_R'):
            self.shift_locked = kc in self.mod_keys
            self._fill_grid()
"""
assert old_mod in src, "_on_mod not found"
src = src.replace(old_mod, new_mod, 1)

# ------------------------------------- 5. long-press sends popup character
old_keyclick = "    def _on_key_click(self, _btn, sym):"
new_longpress = '''    def _on_key_long_press(self, _btn, event, sym, popup):
        """HK puts secondary characters on a long-press; mirror that here."""
        if event.type != Gdk.EventType.BUTTON_PRESS or event.button != 1:
            return False
        ch = (popup or ' ')[0]
        if ch and ch != ' ':
            s = keysym(CHAR_KEYSYM.get(ch, ch))
            if s:
                tap_sym(s)
            return True
        return False

    def _on_key_click(self, _btn, sym):'''
assert old_keyclick in src, "_on_key_click not found"
src = src.replace(old_keyclick, new_longpress, 1)

# ------------------------------------- 6. CHAR_KEYSYM table near the keysyms
anchor = "def keysym(name):"
table = '''CHAR_KEYSYM = {
    '`': 'grave', '~': 'asciitilde', '!': 'exclam', '@': 'at',
    '#': 'numbersign', '$': 'dollar', '%': 'percent', '^': 'asciicircum',
    '&': 'ampersand', '*': 'asterisk', '(': 'parenleft', ')': 'parenright',
    '-': 'minus', '_': 'underscore', '=': 'equal', '+': 'plus',
    '[': 'bracketleft', '{': 'braceleft', ']': 'bracketright',
    '}': 'braceright', '\\\\': 'backslash', '|': 'bar', ';': 'semicolon',
    ':': 'colon', "'": 'apostrophe', '"': 'quotedbl', ',': 'comma',
    '<': 'less', '.': 'period', '>': 'greater', '/': 'slash',
    '?': 'question', ' ': 'space',
}


def keysym(name):'''
assert anchor in src
src = src.replace(anchor, table, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("ok, %d bytes" % len(src))
for needle in ("self._hk_rows()", "shift_locked", "_on_key_long_press", "CHAR_KEYSYM"):
    print(" ", needle, "->", src.count(needle))
