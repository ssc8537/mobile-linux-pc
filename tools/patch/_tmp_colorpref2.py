import io, re
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\prefs\ColorPreference.kt"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")

# 1) imports
t = t.replace("import androidx.preference.Preference\n",
              "import androidx.preference.Preference\n", 1)
if "androidx.appcompat.widget.SwitchCompat" not in t:
    t = t.replace("import androidx.core.content.withStyledAttributes\n",
                  "import androidx.appcompat.widget.SwitchCompat\nimport androidx.core.content.withStyledAttributes\n", 1)

# 2) widget layout: switch + help on the same row
t = t.replace("        widgetLayoutResource = R.layout.help_btn\n",
              "        widgetLayoutResource = R.layout.view_switch_help\n", 1)

# 3) bind the switch too
old_bind = """    override fun onBindViewHolder(holder: PreferenceViewHolder) {
        super.onBindViewHolder(holder)
        (holder.findViewById(R.id.help_btn) as? ImageButton)?.setOnClickListener(helpClickListener)
    }
"""
new_bind = """    override fun onBindViewHolder(holder: PreferenceViewHolder) {
        super.onBindViewHolder(holder)

        // Local fork: the colour row carries its own enable switch, sitting between the
        // colour preview and the '?' help button, so it is obvious that the colour only
        // applies when the switch is on.
        (holder.findViewById(android.R.id.switch_widget) as? SwitchCompat)?.let { sw ->
            sw.setOnCheckedChangeListener(null)
            sw.isChecked = isTintEnabled()
            sw.setOnCheckedChangeListener { _, checked ->
                prefs().edit().putBoolean(KEY_TINT_ENABLED, checked).apply()
                notifyChanged()
            }
        }

        (holder.findViewById(R.id.help_btn) as? ImageButton)?.setOnClickListener(helpClickListener)
    }
"""
assert old_bind in t
t = t.replace(old_bind, new_bind, 1)

# 4) helpers + companion key
old_helpers = """    private fun prefs() = PreferenceManager.getDefaultSharedPreferences(context)

    private fun currentColor(): Int = prefs().getInt(key, 0)
"""
new_helpers = """    private fun prefs() = PreferenceManager.getDefaultSharedPreferences(context)

    private fun isTintEnabled(): Boolean = prefs().getBoolean(KEY_TINT_ENABLED, false)

    private fun currentColor(): Int = prefs().getInt(key, 0)
"""
assert old_helpers in t
t = t.replace(old_helpers, new_helpers, 1)

if "const val KEY_TINT_ENABLED" not in t:
    t = re.sub(r'(companion object \{\n)',
               r'\1        /** Shared with AppPreferences.Input.cursorTintEnabled. */\n'
               '        const val KEY_TINT_ENABLED = "cursor_tint_enabled"\n\n', t, count=1)

io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("ColorPreference patched eol=%r" % eol)
print("KEY_TINT_ENABLED:", "const val KEY_TINT_ENABLED" in t)
print("switch_widget:", "android.R.id.switch_widget" in t)
