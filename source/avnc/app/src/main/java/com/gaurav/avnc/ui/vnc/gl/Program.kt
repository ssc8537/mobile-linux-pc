/*
 * Copyright (c) 2020  Gaurav Ujjwal.
 *
 * SPDX-License-Identifier:  GPL-3.0-or-later
 *
 * See COPYING.txt for more details.
 */

package com.gaurav.avnc.ui.vnc.gl

import android.opengl.GLES20.GL_TEXTURE0
import android.opengl.GLES20.glActiveTexture
import android.opengl.GLES20.glGetAttribLocation
import android.opengl.GLES20.glGetUniformLocation
import android.opengl.GLES20.glUniform1i
import android.opengl.GLES20.glUniform4f
import android.opengl.GLES20.glUniformMatrix4fv
import android.opengl.GLES20.glUseProgram
import com.gaurav.avnc.BuildConfig

/**
 * Represents the GL program used for Frame rendering.
 */
class Program {

    companion object {
        // Attribute constants
        const val A_POSITION = "a_Position"
        const val A_TEXTURE_COORDINATES = "a_TextureCoordinates"

        // Uniform constants
        const val U_PROJECTION = "u_Projection"
        const val U_TEXTURE_UNIT = "u_TextureUnit"
        const val U_TINT = "u_Tint"
    }

    val program = ShaderCompiler.buildProgram(Shaders.VERTEX_SHADER, Shaders.FRAGMENT_SHADER)
    val aPositionLocation = glGetAttribLocation(program, A_POSITION)
    val aTextureCoordinatesLocation = glGetAttribLocation(program, A_TEXTURE_COORDINATES)
    private val uProjectionLocation = glGetUniformLocation(program, U_PROJECTION)
    private val uTexUnitLocation = glGetUniformLocation(program, U_TEXTURE_UNIT)
    private val uTintLocation = glGetUniformLocation(program, U_TINT)
    private var validated = false


    fun setUniforms(projectionMatrix: FloatArray) {
        glUniformMatrix4fv(uProjectionLocation, 1, false, projectionMatrix, 0)
        glActiveTexture(GL_TEXTURE0)
        glUniform1i(uTexUnitLocation, 0)
    }

    /**
     * Local fork: used to colour the remotely rendered cursor.
     * [enabled] = false leaves the texture untouched (used for the framebuffer).
     */
    fun setTint(r: Float, g: Float, b: Float, enabled: Boolean) {
        glUniform4f(uTintLocation, r, g, b, if (enabled) 1f else 0f)
    }

    fun validate() {
        if (BuildConfig.DEBUG && !validated) {
            ShaderCompiler.validateProgram(program)
            validated = true
        }
    }

    fun useProgram() {
        glUseProgram(program)
    }
}