"""Add a settings dialog (设置) to tiny_osk.py.

Loads/saves ~/.config/tiny-osk.conf and exposes:
  * default layout (full / hackers)
  * default placement (docked / floating)
  * key height (32..64 px)
  * window opacity (60..100 %)
"""
import io
import sys

PATH = sys.argv[1]

with io.open(PATH, 'r', encoding='utf-8', newline='') as f:
    src = f.read()

EOL = '\r\n' if '\r\n' in src else '\n'


def conv(block):
    return block.replace('\n', EOL)


# ---------------------------------------------------------------- 1. config helpers
old_trigger = "TRIGGER_FILE = os.environ.get('TINY_OSK_TRIGGER', '/tmp/.tiny_osk_toggle')\n"
assert old_trigger in src, 'trigger line not found'

new_trigger = old_trigger + conv('''
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
            f.write('%s=%s\\n' % (key, data[key]))
''')

src = src.replace(old_trigger, new_trigger, 1)

# ---------------------------------------------------------------- 2. __init__ state
old_init = """        self.layout_name = os.environ.get('TINY_OSK_LAYOUT', 'full')
        self.symbol_mode = False
        self.fn_mode = False
"""
assert old_init in src, 'init block not found'
new_init = """        self.settings = load_settings()
        env_layout = os.environ.get('TINY_OSK_LAYOUT')
        self.layout_name = env_layout or self.settings['layout']
        if self.layout_name not in ('full', 'hackers'):
            self.layout_name = 'full'
        self.key_height = self._int_setting('key_height', 40, 32, 64)
        self.opacity_pct = self._int_setting('opacity', 96, 60, 100)
        self.symbol_mode = False
        self.fn_mode = False
"""
src = src.replace(old_init, new_init, 1)

# put the startup docked flag before _build() so geometry is right the first time
old_build_call = """        self._build()
        self.connect('delete-event', lambda *a: (self.hide(), True)[1])
"""
assert old_build_call in src, 'build call not found'
new_build_call = """        env_docked = os.environ.get('TINY_OSK_DOCKED')
        if env_docked is not None:
            self.docked = env_docked == '1'
        else:
            self.docked = self.settings['placement'] == 'dock'

        self._build()
        self.set_opacity(self.opacity_pct / 100.0)
        self.connect('delete-event', lambda *a: (self.hide(), True)[1])
"""
src = src.replace(old_build_call, new_build_call, 1)

# ---------------------------------------------------------------- 3. helpers + settings dialog
old_rows = """    # ------------------------------------------------------------------ building

    def _rows(self):
"""
assert old_rows in src, 'building marker not found'
new_rows = """    # ------------------------------------------------------------------ settings helpers

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
            sys.stderr.write('tiny_osk: cannot save settings: %s\\n' % exc)

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
        cb_layout.append('hackers', '精简键盘（Hacker\\'s 风格）')
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

    def _rows(self):
"""
src = src.replace(old_rows, new_rows, 1)

# ---------------------------------------------------------------- 4. settings button in top bar
old_button = """        b_dock = Gtk.Button(label='停靠')
        b_dock.get_style_context().add_class('tool')
        b_dock.set_can_focus(False)
        b_dock.connect('clicked', self._toggle_dock)
        top.pack_start(b_dock, False, False, 0)
"""
assert old_button in src, 'dock button block not found'
new_button = old_button + conv("""
        b_settings = Gtk.Button(label='设置')
        b_settings.get_style_context().add_class('tool')
        b_settings.set_can_focus(False)
        b_settings.connect('clicked', self._open_settings)
        top.pack_start(b_settings, False, False, 0)
""")
src = src.replace(old_button, new_button, 1)

# ---------------------------------------------------------------- 5. use key_height
old_size = "                btn.set_size_request(int(46 * width), 40)\n"
assert old_size in src, 'size request not found'
src = src.replace(old_size, "                btn.set_size_request(int(self.key_height * 1.15 * width), self.key_height)\n", 1)

# ---------------------------------------------------------------- 6. remove late docked override
old_late = """        self.docked = os.environ.get('TINY_OSK_DOCKED', '0') == '1'
        self._apply_geometry()
"""
assert old_late in src, 'late docked assignment not found'
src = src.replace(old_late, "        self._apply_geometry()\n", 1)

with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
    f.write(src)

print('patched OK, eol=%r' % EOL)
