/*
 * Copyright (c) 2020  Gaurav Ujjwal.
 *
 * SPDX-License-Identifier:  GPL-3.0-or-later
 *
 * See COPYING.txt for more details.
 */

package com.gaurav.avnc.ui.vnc.gl

/**
 * Shaders used for rendering framebuffer
 */
object Shaders {
    //language=GLSL
    const val VERTEX_SHADER = """
            uniform mat4 u_Projection;
            attribute vec2 a_Position;
            attribute vec2 a_TextureCoordinates;
            varying vec2 v_TextureCoordinates;
            void main()
            {
               v_TextureCoordinates = a_TextureCoordinates;
               gl_Position = u_Projection * vec4(a_Position, 0, 1);
            }"""

    //language=GLSL
    const val FRAGMENT_SHADER = """
            precision mediump float;
            uniform sampler2D u_TextureUnit;
            uniform vec4 u_Tint;
            varying vec2 v_TextureCoordinates;
            void main()
            {
               vec4 color = texture2D(u_TextureUnit, v_TextureCoordinates).bgra;
               if (u_Tint.a > 0.5) {
                   // Keep the cursor shape readable: darken/lighten the tint by the
                   // source luminance instead of multiplying, so the black parts of
                   // the pointer turn into a darker shade of the chosen colour
                   // rather than staying black.
                   float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                   color.rgb = u_Tint.rgb * mix(0.30, 1.15, luma);
                   color.rgb = clamp(color.rgb, 0.0, 1.0);
               }
               gl_FragColor = color;
            }"""
}