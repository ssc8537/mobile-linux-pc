/*
 * Copyright (c) 2025  Gaurav Ujjwal.
 *
 * SPDX-License-Identifier:  GPL-3.0-or-later
 *
 * See COPYING.txt for more details.
 */

package com.gaurav.avnc.ui.prefs

import android.content.Context
import android.util.AttributeSet
import androidx.core.content.withStyledAttributes
import androidx.preference.PreferenceManager
import androidx.preference.PreferenceViewHolder
import androidx.preference.SeekBarPreference
import com.gaurav.avnc.R

/**
 * Local fork: a seekbar that shows a human readable value instead of a bare number.
 *
 * Upstream's sliders only show "6", which tells the user nothing. With a suffix such as
 * " 倍" the same slider reads "6 倍", so the strength scale is self-explanatory.
 */
class ValueLabelPreference(context: Context, attrs: AttributeSet) : SeekBarPreference(context, attrs) {

    private var valuePrefix: String = ""
    private var valueSuffix: String = ""

    init {
        context.withStyledAttributes(attrs, R.styleable.ValueLabelPreference) {
            valuePrefix = getString(R.styleable.ValueLabelPreference_valuePrefix) ?: ""
            valueSuffix = getString(R.styleable.ValueLabelPreference_valueSuffix) ?: ""
        }
        setOnPreferenceChangeListener { _, newValue ->
            if (newValue is Int)
                summary = format(newValue)
            true
        }
    }

    private fun format(v: Int): String = "$valuePrefix$v$valueSuffix"

    override fun onAttachedToHierarchy(preferenceManager: PreferenceManager) {
        super.onAttachedToHierarchy(preferenceManager)
        summary = format(value)
    }

    override fun onBindViewHolder(holder: PreferenceViewHolder) {
        super.onBindViewHolder(holder)
        summary = format(value)
    }
}
