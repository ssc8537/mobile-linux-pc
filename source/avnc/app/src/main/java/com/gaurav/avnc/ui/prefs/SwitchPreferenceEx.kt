/*
 * Copyright (c) 2022  Gaurav Ujjwal.
 *
 * SPDX-License-Identifier:  GPL-3.0-or-later
 *
 * See COPYING.txt for more details.
 */

package com.gaurav.avnc.ui.prefs

import android.content.Context
import android.util.AttributeSet
import android.view.View
import android.widget.ImageButton
import androidx.core.content.withStyledAttributes
import androidx.fragment.app.FragmentActivity
import androidx.preference.PreferenceViewHolder
import androidx.preference.SwitchPreferenceCompat
import com.gaurav.avnc.R
import com.gaurav.avnc.util.MsgDialog

/**
 * Switch preference with an optional help button.
 *
 * Local fork: stock [SwitchPreferenceCompat] cannot host `@layout/help_btn`,
 * so this subclass adds the same help affordance that [ListPreferenceEx] has.
 */
class SwitchPreferenceEx(context: Context, attrs: AttributeSet) : SwitchPreferenceCompat(context, attrs) {

    /**
     * Message shown in a dialog, when help button of the preference is clicked.
     * This will only work if [R.layout.help_btn] is used as widget layout.
     */
    private var helpMessage: CharSequence? = null

    private val helpClickListener = View.OnClickListener {
        helpMessage?.let { helpMessage ->
            (context as? FragmentActivity)?.let { fragmentActivity ->
                MsgDialog.show(fragmentActivity.supportFragmentManager,
                               fragmentActivity.getString(R.string.desc_help_btn),
                               helpMessage)
            }
        }
    }

    init {
        context.withStyledAttributes(attrs, R.styleable.ListPreferenceEx) {
            helpMessage = getText(R.styleable.ListPreferenceEx_helpMessage)
        }
    }

    override fun onBindViewHolder(holder: PreferenceViewHolder) {
        super.onBindViewHolder(holder)
        (holder.findViewById(R.id.help_btn) as? ImageButton)?.setOnClickListener(helpClickListener)
    }
}
