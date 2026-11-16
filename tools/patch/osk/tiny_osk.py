#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tiny_osk.py -- floating pink on-screen keyboard for the Tiny Container desktop.

Runs inside the Debian proot container (python3 + GTK3 + libXtst are all present
in the shipped image).  Keys are delivered to whatever window has focus through
the X server's XTEST extension, so it works with every application.

Trigger:
  * XF86XK_Launch0 (fired by the Android side when the user taps the keyboard
    button in the VNC overlay) toggles the keyboard.
  * F9 is grabbed as a fallback / desktop shortcut.

Layouts:
  * "hackers" -- compact, modelled on Hacker's Keyboard.
  * "full"    -- full 87-key layout with a numeric keypad.

The window is undecorated, always on top, and can be dragged by its top handle.
"""

import ctypes
import ctypes.util
import os
import signal
import sys
import threading

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

# Layout data ported from klausw/hackerskeyboard (see hk_layout.py).
try:
    from hk_layout import (HK_FULL, HK_COMPACT, HK_SYMBOLS,
                           HK_SYMBOLS_SHIFT)
except ImportError:  # pragma: no cover - hk_layout.py ships next to this file
    HK_FULL = HK_COMPACT = HK_SYMBOLS = HK_SYMBOLS_SHIFT = []

# --------------------------------------------------------------------------- X11

x11 = ctypes.CDLL(ctypes.util.find_library('X11') or 'libX11.so.6')
xtst = ctypes.CDLL(ctypes.util.find_library('Xtst') or 'libXtst.so.6')

x11.XOpenDisplay.restype = ctypes.c_void_p
x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
x11.XDefaultRootWindow.restype = ctypes.c_ulong
x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
x11.XStringToKeysym.restype = ctypes.c_ulong
x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
x11.XKeysymToKeycode.restype = ctypes.c_ubyte
x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
x11.XkbKeycodeToKeysym.restype = ctypes.c_ulong
x11.XkbKeycodeToKeysym.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_int, ctypes.c_int]
x11.XGrabKey.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_ulong,
                         ctypes.c_int, ctypes.c_int, ctypes.c_int]
x11.XSelectInput.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_long]
x11.XFlush.argtypes = [ctypes.c_void_p]
x11.XPending.argtypes = [ctypes.c_void_p]
x11.XNextEvent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]

DISPLAY = x11.XOpenDisplay(None)
if not DISPLAY:
    sys.stderr.write('tiny_osk: cannot open X display\n')
    sys.exit(1)

ROOT = x11.XDefaultRootWindow(DISPLAY)

TRIGGER_FILE = os.environ.get('TINY_OSK_TRIGGER', '/tmp/.tiny_osk_toggle')

CONFIG_FILE = os.environ.get('TINY_OSK_CONFIG',
                             os.path.expanduser('~/.config/tiny-osk.conf'))

DEFAULT_SETTINGS = {
    'layout': 'full',        # full | hackers
    'placement': 'float',    # float | dock
    'key_height': '40',      # px
    'opacity': '96',         # percent
}


def load_settings():
    data = dict(DEFAULT_SETTINGS)
    try:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key, value = key.strip(), value.strip()
                if key in data:
                    data[key] = value
    except OSError:
        pass
    return data


def save_settings(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        for key in sorted(data):
            f.write('%s=%s\n' % (key, data[key]))


# --------------------------------------------------------------------------- keysyms

XK_Shift_L = 0xFFE1
XK_Control_L = 0xFFE3
XK_Alt_L = 0xFFE9
XK_Super_L = 0xFFEB
XK_Caps_Lock = 0xFFE5

AnyModifier = 1 << 15
KeyPress = 2
GrabModeAsync = 1


CHAR_KEYSYM = {
    '`': 'grave', '~': 'asciitilde', '!': 'exclam', '@': 'at',
    '#': 'numbersign', '$': 'dollar', '%': 'percent', '^': 'asciicircum',
    '&': 'ampersand', '*': 'asterisk', '(': 'parenleft', ')': 'parenright',
    '-': 'minus', '_': 'underscore', '=': 'equal', '+': 'plus',
    '[': 'bracketleft', '{': 'braceleft', ']': 'bracketright',
    '}': 'braceright', '\\': 'backslash', '|': 'bar', ';': 'semicolon',
    ':': 'colon', "'": 'apostrophe', '"': 'quotedbl', ',': 'comma',
    '<': 'less', '.': 'period', '>': 'greater', '/': 'slash',
    '?': 'question', ' ': 'space',
}


def keysym(name):
    return x11.XStringToKeysym(name.encode())


def keycode(sym):
    return x11.XKeysymToKeycode(DISPLAY, sym)


def fake(kc, down):
    xtst.XTestFakeKeyEvent(DISPLAY, kc, 1 if down else 0, 0)
    x11.XFlush(DISPLAY)


def tap_keycode(kc):
    fake(kc, True)
    fake(kc, False)


def tap_sym(sym):
    """Type one keysym, adding Shift automatically when the symbol lives on
    the shifted level of that physical key."""
    kc = keycode(sym)
    if kc == 0:
        return
    base = x11.XkbKeycodeToKeysym(DISPLAY, kc, 0, 0)
    shift_kc = keycode(XK_Shift_L)
    need_shift = base != sym
    if need_shift:
        fake(shift_kc, True)
    tap_keycode(kc)
    if need_shift:
        fake(shift_kc, False)


# --------------------------------------------------------------------------- layouts
# Each cell: (label, keysym, role, shift_label, width_units, popup)
#   role: 'key' = normal, 'mod' = sticky modifier, 'layer' = switch layer
#
# The tables below are generated by gen_hk_layout.py from Hacker's Keyboard's
# own res/xml/kbd_*.xml, so key order, widths and shift labels are HK's.

def k(label, sym, w=1.0, role=None):
    return (label, sym, w, role)


def _norm_row(cells):
    """Scale one HK row so its cells fill the whole keyboard width.

    HK gives every key a percentage of the *row*; our grid is percentages of
    the panel width, so each row is normalised independently.
    """
    total = sum(c[4] for c in cells) or 1.0
    return [(c[0], c[1], c[4] * 100.0 / total, c[2], c[3], c[5]) for c in cells]


def _rows(cells_rows):
    return [_norm_row(r) for r in cells_rows if r]


HK_FULL_ROWS = _rows(HK_FULL)
HK_COMPACT_ROWS = _rows(HK_COMPACT)
HK_SYMBOL_ROWS = _rows(HK_SYMBOLS)
HK_SYMBOL_SHIFT_ROWS = _rows(HK_SYMBOLS_SHIFT)

# Fallbacks in case hk_layout.py is missing from the image.
if not HK_FULL_ROWS:
    HK_FULL_ROWS = [[k('Esc', 'Escape'), k('Tab', 'Tab'), k('Ctrl', 'Control_L', 1.0, 'mod'),
                     k('Space', 'space', 6.0), k('Bksp', 'BackSpace')]]
    HK_COMPACT_ROWS = HK_FULL_ROWS
    HK_SYMBOL_ROWS = [[k('1', '1'), k('2', '2'), k('3', '3')]]
    HK_SYMBOL_SHIFT_ROWS = HK_SYMBOL_ROWS

# --------------------------------------------------------------------------- CSS

PINK_CSS = b"""
window.tinyosk {
    background-color: rgba(255, 240, 246, 0.96);
    border: 2px solid #ff9ec4;
    border-radius: 14px;
}
button.tk {
    background-image: none;
    background-color: #ffe3ee;
    color: #7a2b4d;
    border: 1px solid #ffb6d0;
    border-radius: 9px;
    font-weight: 600;
    padding: 4px 2px;
    min-height: 34px;
}
button.tk:hover { background-color: #ffd0e2; }
button.tk:active { background-color: #ff9ec4; color: #ffffff; }
button.tk.mod-on {
    background-color: #ff6fa8;
    color: #ffffff;
    border-color: #e04f88;
}
button.tk.fn-on {
    background-color: #ffc2d8;
    color: #6b2443;
}
label.handle {
    color: #b0557d;
    font-size: 13pt;
    background-color: rgba(255, 200, 220, 0.55);
    border-radius: 6px;
    padding: 0px 10px;
}
button.tool {
    background-image: none;
    background-color: #ffd7e6;
    color: #7a2b4d;
    border: 1px solid #ffb6d0;
    border-radius: 8px;
    padding: 2px 8px;
}
"""

# --------------------------------------------------------------------------- window


class TinyOsk(Gtk.Window):

    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_name('tinyosk')
        self.get_style_context().add_class('tinyosk')
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_resizable(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.sticky(True)

        self.settings = load_settings()
        env_layout = os.environ.get('TINY_OSK_LAYOUT')
        self.layout_name = env_layout or self.settings['layout']
        if self.layout_name not in ('full', 'hackers'):
            self.layout_name = 'full'
        self.key_height = self._int_setting('key_height', 40, 32, 64)
        self.opacity_pct = self._int_setting('opacity', 96, 60, 100)
        self.symbol_mode = False
        self.fn_mode = False
        self.shift_locked = False
        self.mod_keys = []           # pressed sticky keycodes
        self.mod_buttons = {}

        env_docked = os.environ.get('TINY_OSK_DOCKED')
        if env_docked is not None:
            self.docked = env_docked == '1'
        else:
            self.docked = self.settings['placement'] == 'dock'

        self._build()
        self.set_opacity(self.opacity_pct / 100.0)
        self.connect('delete-event', lambda *a: (self.hide(), True)[1])
        self.connect('key-press-event', self._on_key)

    # ------------------------------------------------------------------ settings helpers

    def _int_setting(self, key, fallback, low, high):
        try:
            value = int(self.settings.get(key, fallback))
        except (TypeError, ValueError):
            value = fallback
        return max(low, min(high, value))

    def _persist(self, **changes):
        self.settings.update({k: str(v) for k, v in changes.items()})
        try:
            save_settings(self.settings)
        except OSError as exc:
            sys.stderr.write('tiny_osk: cannot save settings: %s\n' % exc)

    def _open_settings(self, *_):
        dlg = Gtk.Dialog(title='悬浮键盘设置', transient_for=self, modal=True)
        dlg.set_default_size(360, -1)
        area = dlg.get_content_area()
        area.set_spacing(8)
        area.set_border_width(12)

        grid = Gtk.Grid(row_spacing=8, column_spacing=10)
        area.add(grid)

        # layout
        lbl_layout = Gtk.Label(label='默认布局', xalign=0)
        grid.attach(lbl_layout, 0, 0, 1, 1)
        cb_layout = Gtk.ComboBoxText()
        cb_layout.append('full', '全键盘（87 键）')
        cb_layout.append('hackers', '精简键盘（Hacker\'s 风格）')
        cb_layout.set_active_id(self.layout_name)
        grid.attach(cb_layout, 1, 0, 1, 1)

        # placement
        lbl_place = Gtk.Label(label='默认位置', xalign=0)
        grid.attach(lbl_place, 0, 1, 1, 1)
        cb_place = Gtk.ComboBoxText()
        cb_place.append('float', '悬浮（可拖动）')
        cb_place.append('dock', '停靠（占下方 2/5）')
        cb_place.set_active_id('dock' if self.docked else 'float')
        grid.attach(cb_place, 1, 1, 1, 1)

        # key height
        lbl_height = Gtk.Label(label='按键高度', xalign=0)
        grid.attach(lbl_height, 0, 2, 1, 1)
        adj_h = Gtk.Adjustment(value=self.key_height, lower=32, upper=64, step_increment=2)
        spin_h = Gtk.SpinButton(adjustment=adj_h, climb_rate=1, digits=0)
        grid.attach(spin_h, 1, 2, 1, 1)

        # opacity
        lbl_opacity = Gtk.Label(label='不透明度（%）', xalign=0)
        grid.attach(lbl_opacity, 0, 3, 1, 1)
        adj_o = Gtk.Adjustment(value=self.opacity_pct, lower=60, upper=100, step_increment=2)
        spin_o = Gtk.SpinButton(adjustment=adj_o, climb_rate=1, digits=0)
        grid.attach(spin_o, 1, 3, 1, 1)

        hint = Gtk.Label()
        hint.set_markup('<small>拖动键盘顶部横杠即可移动；'
                        '停靠模式下键盘占满屏幕宽度。</small>')
        hint.set_xalign(0)
        area.pack_start(hint, False, False, 0)

        dlg.add_button('取消', Gtk.ResponseType.CANCEL)
        dlg.add_button('保存', Gtk.ResponseType.OK)
        dlg.show_all()

        response = dlg.run()
        layout_id = cb_layout.get_active_id()
        place_id = cb_place.get_active_id()
        new_height = int(spin_h.get_value())
        new_opacity = int(spin_o.get_value())
        dlg.destroy()

        if response != Gtk.ResponseType.OK:
            return

        self.layout_name = layout_id or self.layout_name
        self.docked = (place_id == 'dock')
        self.key_height = max(32, min(64, new_height))
        self.opacity_pct = max(60, min(100, new_opacity))

        self._persist(layout=self.layout_name,
                      placement=place_id or 'float',
                      key_height=self.key_height,
                      opacity=self.opacity_pct)

        self.set_opacity(self.opacity_pct / 100.0)
        self._fill_grid()
        self._apply_geometry()

    # ------------------------------------------------------------------ building

    def _hk_rows(self):
        if self.fn_mode:
            return HK_COMPACT_ROWS
        if self.symbol_mode:
            return HK_SYMBOL_SHIFT_ROWS if self.shift_locked else HK_SYMBOL_ROWS
        if self.layout_name == 'hackers':
            return HK_COMPACT_ROWS
        return HK_FULL_ROWS

    def _rows(self):
        return self._hk_rows()

    def _build(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        outer.set_border_width(6)
        self.add(outer)

        # ---- top bar: drag handle + tools
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        handle = Gtk.EventBox()
        handle.set_visible_window(False)
        lbl = Gtk.Label(label='═══  拖动移动键盘  ═══')
        lbl.get_style_context().add_class('handle')
        handle.add(lbl)
        handle.connect('button-press-event', self._start_drag)
        top.pack_start(handle, True, True, 0)

        b_layout = Gtk.Button(label='布局')
        b_layout.get_style_context().add_class('tool')
        b_layout.set_can_focus(False)
        b_layout.connect('clicked', self._toggle_layout)
        top.pack_start(b_layout, False, False, 0)

        b_dock = Gtk.Button(label='停靠')
        b_dock.get_style_context().add_class('tool')
        b_dock.set_can_focus(False)
        b_dock.connect('clicked', self._toggle_dock)
        top.pack_start(b_dock, False, False, 0)

        b_settings = Gtk.Button(label='设置')
        b_settings.get_style_context().add_class('tool')
        b_settings.set_can_focus(False)
        b_settings.connect('clicked', self._open_settings)
        top.pack_start(b_settings, False, False, 0)

        b_hide = Gtk.Button(label='收起')
        b_hide.get_style_context().add_class('tool')
        b_hide.set_can_focus(False)
        b_hide.connect('clicked', lambda *a: self.hide())
        top.pack_start(b_hide, False, False, 0)

        b_quit = Gtk.Button(label='×')
        b_quit.get_style_context().add_class('tool')
        b_quit.set_can_focus(False)
        b_quit.connect('clicked', lambda *a: Gtk.main_quit())
        top.pack_start(b_quit, False, False, 0)
        outer.pack_start(top, False, False, 0)

        # ---- key grid
        self.grid_holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        outer.pack_start(self.grid_holder, True, True, 0)
        self._fill_grid()

        self._apply_geometry()

    def _fill_grid(self):
        for child in self.grid_holder.get_children():
            self.grid_holder.remove(child)

        for row in self._rows():
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

    def _apply_geometry(self):
        screen = Gdk.Screen.get_default()
        sw = screen.get_width()
        sh = screen.get_height()
        if self.docked:
            self.resize(sw, int(sh * 0.40))
            self.move(0, sh - int(sh * 0.40))
        else:
            self.resize(int(sw * 0.92), -1)
            self.move(int(sw * 0.04), sh - int(sh * 0.42))

    # ------------------------------------------------------------------ actions

    def _start_drag(self, widget, event):
        if event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
            return True
        return False

    def _toggle_layout(self, *_):
        self.layout_name = 'hackers' if self.layout_name == 'full' else 'full'
        self.fn_mode = False
        self.symbol_mode = False
        self._fill_grid()
        self._apply_geometry()

    def _toggle_dock(self, *_):
        self.docked = not self.docked
        self._apply_geometry()

    def _on_layer(self, _btn):
        label = _btn.get_child().get_text()
        if label == 'Fn':
            self.fn_mode = not self.fn_mode
            if self.fn_mode:
                self.symbol_mode = False
        else:
            self.symbol_mode = not self.symbol_mode
        self._fill_grid()

    def _on_fn(self, _btn):
        self.fn_mode = not self.fn_mode
        if self.fn_mode:
            self.symbol_mode = False
        self._fill_grid()

    def _on_mod(self, btn, sym):
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

    def _release_mods(self):
        for kc in list(self.mod_keys):
            fake(kc, False)
        self.mod_keys.clear()

    def _on_key_long_press(self, _btn, event, sym, popup):
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

    def _on_key_click(self, _btn, sym):
        name = sym
        if name is None:
            return
        s = keysym(name)
        if s == 0:
            return
        tap_sym(s)
        if self.mod_keys:
            self._release_mods()
            for b in self.mod_buttons.values():
                b.get_style_context().remove_class('mod-on')
        if self.symbol_mode:
            self.symbol_mode = False
            self._fill_grid()

    def _on_key(self, _w, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False

    # ------------------------------------------------------------------ toggle

    def toggle(self):
        if self.get_visible():
            self.hide()
        else:
            self._apply_geometry()
            self.show_all()
            self._release_mods()


# --------------------------------------------------------------------------- hotkey

def start_hotkey_listener(win):
    """Grab XF86XK_Launch0 (sent by the Android overlay button) and F9."""
    grabs = [keysym('XF86Launch0'), keysym('F9')]
    for sym in grabs:
        if not sym:
            continue
        kc = keycode(sym)
        if kc == 0:
            continue
        for mods in (0, 2, 1, 4):     # plain, caps, shift, ctrl
            x11.XGrabKey(DISPLAY, kc, mods, ROOT, True, GrabModeAsync, GrabModeAsync)
    x11.XSelectInput(DISPLAY, ROOT, 1)      # KeyPressMask
    x11.XFlush(DISPLAY)

    class XEvent(ctypes.Structure):
        _fields_ = [('type', ctypes.c_int),
                    ('pad', ctypes.c_long * 24)]

    def loop():
        ev = XEvent()
        while True:
            x11.XNextEvent(DISPLAY, ctypes.byref(ev))
            if ev.type == KeyPress:
                GLib.idle_add(win.toggle)

    t = threading.Thread(target=loop, daemon=True)
    t.start()


def _ensure_display():
    """GTK dies with an unhelpful message when DISPLAY is missing. XFCE sessions
    normally export it, but autostart entries can lose it, so guess from the
    sockets in /tmp/.X11-unix before giving up."""
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
            f.write('[tiny_osk] ' + str(msg) + '\n')
    except OSError:
        pass


def main():
    disp = _ensure_display()
    _log('main start, DISPLAY=%s, pid=%d' % (disp, os.getpid()))
    provider = Gtk.CssProvider()
    provider.load_from_data(PINK_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    win = TinyOsk()
    win.show_all()
    win.hide()
    _log('window created, hidden, layout=%s docked=%s' % (win.layout_name, win.docked))

    try:
        start_hotkey_listener(win)
        _log('hotkey listener installed (XF86Launch0 / F9)')
    except Exception as exc:      # never let the hotkey break the keyboard
        _log('hotkey listener failed: %r' % (exc,))

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

    if os.environ.get('TINY_OSK_START_VISIBLE', '0') == '1':
        win.show_all()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    _log('entering Gtk.main()')
    Gtk.main()


if __name__ == '__main__':
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
        _log('FATAL:\n' + traceback.format_exc())
        raise
