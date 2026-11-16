/*
 * Copyright (c) 2025  Gaurav Ujjwal.
 *
 * SPDX-License-Identifier:  GPL-3.0-or-later
 *
 * See COPYING.txt for more details.
 */

package com.gaurav.avnc.ui.prefs

import android.app.AlertDialog
import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.util.AttributeSet
import android.view.Gravity
import android.view.View
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.Button
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.TextView
import androidx.appcompat.widget.SwitchCompat
import androidx.core.content.withStyledAttributes
import androidx.fragment.app.FragmentActivity
import androidx.preference.Preference
import androidx.preference.PreferenceManager
import androidx.preference.PreferenceViewHolder
import com.gaurav.avnc.R
import com.gaurav.avnc.util.MsgDialog

/**
 * Local fork: preference that lets the user pick a colour.
 *
 * A row of preset swatches (pink first, since that is the most requested colour) is
 * shown on top of a full RGB mixer, so any colour can be produced. Value 0 means
 * "no tint", i.e. the original cursor colours are used.
 *
 * This intentionally does not depend on any third-party colour picker library.
 */
class ColorPreference(context: Context, attrs: AttributeSet) : Preference(context, attrs) {

    private var helpMessage: CharSequence? = null

    private val helpClickListener = View.OnClickListener {
        helpMessage?.let { message ->
            (context as? FragmentActivity)?.let { activity ->
                MsgDialog.show(activity.supportFragmentManager,
                               activity.getString(R.string.desc_help_btn),
                               message)
            }
        }
    }

    init {
        context.withStyledAttributes(attrs, R.styleable.ListPreferenceEx) {
            helpMessage = getText(R.styleable.ListPreferenceEx_helpMessage)
        }
        widgetLayoutResource = R.layout.view_switch_help
    }

    override fun onBindViewHolder(holder: PreferenceViewHolder) {
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


    private fun prefs() = PreferenceManager.getDefaultSharedPreferences(context)

    private fun isTintEnabled(): Boolean = prefs().getBoolean(KEY_TINT_ENABLED, false)

    private fun currentColor(): Int = prefs().getInt(key, 0)

    override fun onClick() {
        val activity = context as? FragmentActivity ?: return
        val initial = currentColor()

        var r = if (initial == 0) 255 else Color.red(initial)
        var g = if (initial == 0) 255 else Color.green(initial)
        var b = if (initial == 0) 255 else Color.blue(initial)

        val root = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            val pad = dp(16)
            setPadding(pad, pad, pad, pad)
        }

        val preview = View(activity).apply {
            layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, dp(48))
        }
        root.addView(preview)

        // Preset swatches, pink first
        val swatchRow = LinearLayout(activity).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT)
        }

        fun refreshPreview() {
            val bg = GradientDrawable().apply {
                setColor(Color.rgb(r, g, b))
                cornerRadius = dp(6).toFloat()
                setStroke(dp(1), Color.GRAY)
            }
            preview.background = bg
        }

        for (preset in PRESET_COLORS) {
            val button = Button(activity).apply {
                text = ""
                minimumWidth = 0
                minimumHeight = 0
                layoutParams = LinearLayout.LayoutParams(0, dp(36), 1f).apply {
                    setMargins(dp(2), 0, dp(2), 0)
                }
                background = GradientDrawable().apply {
                    setColor(preset)
                    cornerRadius = dp(4).toFloat()
                    setStroke(dp(1), Color.GRAY)
                }
                setOnClickListener {
                    r = Color.red(preset)
                    g = Color.green(preset)
                    b = Color.blue(preset)
                    // reflect the preset in the sliders below
                    (root.findViewWithTag<SeekBar>("slider_r"))?.progress = r
                    (root.findViewWithTag<SeekBar>("slider_g"))?.progress = g
                    (root.findViewWithTag<SeekBar>("slider_b"))?.progress = b
                    refreshPreview()
                }
            }
            swatchRow.addView(button)
        }
        root.addView(swatchRow)

        fun addSlider(tag: String, label: String, value: Int, onChanged: (Int) -> Unit) {
            val title = TextView(activity).apply {
                text = "$label: $value"
                setPadding(0, dp(8), 0, 0)
            }
            val bar = SeekBar(activity).apply {
                max = 255
                progress = value
                this.tag = tag
                setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                    override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {
                        title.text = "$label: $p"
                        onChanged(p)
                        refreshPreview()
                    }

                    override fun onStartTrackingTouch(sb: SeekBar?) {}
                    override fun onStopTrackingTouch(sb: SeekBar?) {}
                })
            }
            root.addView(title)
            root.addView(bar)
        }

        addSlider("slider_r", "R", r) { r = it }
        addSlider("slider_g", "G", g) { g = it }
        addSlider("slider_b", "B", b) { b = it }

        refreshPreview()

        AlertDialog.Builder(activity)
            .setTitle(R.string.pref_cursor_tint)
            .setView(root)
            .setPositiveButton(android.R.string.ok) { _, _ ->
                prefs().edit().putInt(key, Color.rgb(r, g, b)).apply()
            }
            .setNeutralButton(R.string.color_picker_reset) { _, _ ->
                prefs().edit().putInt(key, 0).apply()
            }
            .setNegativeButton(android.R.string.cancel, null)
            .show()
    }

    private fun dp(value: Int): Int =
        (value * context.resources.displayMetrics.density).toInt()

    companion object {
        /** Shared with AppPreferences.Input.cursorTintEnabled. */
        const val KEY_TINT_ENABLED = "cursor_tint_enabled"

        /**
         * Presets offered in the picker. Pink comes first because it is the
         * most requested colour for this app.
         */
        val PRESET_COLORS = intArrayOf(
                0xFFFF69B4.toInt(), // hot pink
                0xFFFF1493.toInt(), // deep pink
                0xFFFFC0CB.toInt(), // light pink
                0xFFE91E63.toInt(), // rose
                0xFF2196F3.toInt(), // blue
                0xFF03A9F4.toInt(), // light blue
                0xFF00BCD4.toInt(), // cyan
                0xFF009688.toInt(), // teal
                0xFF4CAF50.toInt(), // green
                0xFF8BC34A.toInt(), // light green
                0xFFFFEB3B.toInt(), // yellow
                0xFFFFC107.toInt(), // amber
                0xFFFF9800.toInt(), // orange
                0xFFF44336.toInt(), // red
                0xFF9C27B0.toInt(), // purple
                0xFF673AB7.toInt(), // deep purple
                0xFF795548.toInt(), // brown
                0xFF9E9E9E.toInt(), // grey
                0xFFFFFFFF.toInt()  // white
        )
    }
}
