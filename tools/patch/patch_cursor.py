import io, sys, os

J = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\gl'

def rd(p):
    return io.open(p, 'r', encoding='utf-8', newline='').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', os.path.basename(p))

# ---------------------------------------------------------------- Shaders.kt
p = os.path.join(J, 'Shaders.kt')
s = rd(p)
old = ('    //language=GLSL\r\n'
       '    const val FRAGMENT_SHADER = """\r\n'
       '            precision mediump float;\r\n'
       '            uniform sampler2D u_TextureUnit;\r\n'
       '            varying vec2 v_TextureCoordinates;\r\n'
       '            void main()\r\n'
       '            {\r\n'
       '               gl_FragColor = texture2D(u_TextureUnit, v_TextureCoordinates).bgra;\r\n'
       '            }"""\r\n')
new = ('    //language=GLSL\r\n'
       '    const val FRAGMENT_SHADER = """\r\n'
       '            precision mediump float;\r\n'
       '            uniform sampler2D u_TextureUnit;\r\n'
       '            uniform vec4 u_Tint;\r\n'
       '            varying vec2 v_TextureCoordinates;\r\n'
       '            void main()\r\n'
       '            {\r\n'
       '               vec4 color = texture2D(u_TextureUnit, v_TextureCoordinates).bgra;\r\n'
       '               if (u_Tint.a > 0.5) {\r\n'
       '                   color.rgb = color.rgb * u_Tint.rgb;\r\n'
       '               }\r\n'
       '               gl_FragColor = color;\r\n'
       '            }"""\r\n')
assert old in s, 'fragment shader not found'
wr(p, s.replace(old, new))

# ---------------------------------------------------------------- Program.kt
p = os.path.join(J, 'Program.kt')
s = rd(p)
s = s.replace('import android.opengl.GLES20.glUniform1i\r\n',
              'import android.opengl.GLES20.glUniform1i\r\nimport android.opengl.GLES20.glUniform4f\r\n')
s = s.replace('        const val U_TEXTURE_UNIT = "u_TextureUnit"\r\n',
              '        const val U_TEXTURE_UNIT = "u_TextureUnit"\r\n'
              '        const val U_TINT = "u_Tint"\r\n')
s = s.replace('    private val uTexUnitLocation = glGetUniformLocation(program, U_TEXTURE_UNIT)\r\n',
              '    private val uTexUnitLocation = glGetUniformLocation(program, U_TEXTURE_UNIT)\r\n'
              '    private val uTintLocation = glGetUniformLocation(program, U_TINT)\r\n')
old = ('    fun validate() {\r\n')
new = ('    /**\r\n'
       '     * Local fork: used to colour the remotely rendered cursor.\r\n'
       '     * [enabled] = false leaves the texture untouched (used for the framebuffer).\r\n'
       '     */\r\n'
       '    fun setTint(r: Float, g: Float, b: Float, enabled: Boolean) {\r\n'
       '        glUniform4f(uTintLocation, r, g, b, if (enabled) 1f else 0f)\r\n'
       '    }\r\n'
       '\r\n'
       '    fun validate() {\r\n')
assert old in s
s = s.replace(old, new, 1)
wr(p, s)

# ---------------------------------------------------------------- Cursor.kt
p = os.path.join(J, 'Cursor.kt')
s = rd(p)
old = ('    /**\r\n'
       '     * Updates position/geometry of the cursor\r\n'
       '     */\r\n'
       '    fun update(x: Float, y: Float, ci: CursorInfo, frame: Frame) {\r\n'
       '        val width = ci.width\r\n'
       '        val height = ci.height\r\n')
new = ('    /**\r\n'
       '     * Local fork: user configurable scale factor, derived from the\r\n'
       '     * "cursor_size" preference (percentage, 100 = original size).\r\n'
       '     *\r\n'
       '     * The texture is upscaled by GL_LINEAR filtering, and the hotspot is scaled\r\n'
       '     * by the same factor so the pointer tip stays on the hotspot.\r\n'
       '     */\r\n'
       '    var scale = 1f\r\n'
       '\r\n'
       '    /**\r\n'
       '     * Updates position/geometry of the cursor\r\n'
       '     */\r\n'
       '    fun update(x: Float, y: Float, ci: CursorInfo, frame: Frame) {\r\n'
       '        val width = ci.width * scale\r\n'
       '        val height = ci.height * scale\r\n')
assert old in s, 'cursor update head not found'
s = s.replace(old, new)
old = '        val normalDrawRect = RectF(cursorRect).apply { offset(-ci.xHot.toFloat(), -ci.yHot.toFloat()) }\r\n'
new = '        val normalDrawRect = RectF(cursorRect).apply { offset(-ci.xHot * scale, -ci.yHot * scale) }\r\n'
assert old in s, 'hotspot line not found'
s = s.replace(old, new)
wr(p, s)

# ---------------------------------------------------------------- Renderer.kt
p = os.path.join(J, 'Renderer.kt')
s = rd(p)
s = s.replace('import android.opengl.GLES20.GL_BLEND\r\n',
              'import android.graphics.Color\r\nimport android.opengl.GLES20.GL_BLEND\r\n')
old = ('            val ci = client.cursorInfo\r\n'
       '\r\n'
       '            cursor.update(client.pointerX.toFloat(), client.pointerY.toFloat(), ci, frame)\r\n'
       '            cursor.bind(program)\r\n'
       '            client.uploadCursorTexture()\r\n'
       '            cursor.draw()\r\n'
       '\r\n'
       '            glDisable(GL_BLEND)\r\n')
new = ('            val ci = client.cursorInfo\r\n'
       '\r\n'
       '            // Local fork: user configurable cursor size and colour\r\n'
       '            cursor.scale = viewModel.pref.input.cursorSize / 100f\r\n'
       '            val tint = viewModel.pref.input.cursorTint\r\n'
       '            if (tint == 0)\r\n'
       '                program.setTint(0f, 0f, 0f, false)\r\n'
       '            else\r\n'
       '                program.setTint(\r\n'
       '                        Color.red(tint) / 255f,\r\n'
       '                        Color.green(tint) / 255f,\r\n'
       '                        Color.blue(tint) / 255f,\r\n'
       '                        true\r\n'
       '                )\r\n'
       '\r\n'
       '            cursor.update(client.pointerX.toFloat(), client.pointerY.toFloat(), ci, frame)\r\n'
       '            cursor.bind(program)\r\n'
       '            client.uploadCursorTexture()\r\n'
       '            cursor.draw()\r\n'
       '\r\n'
       '            // Restore the pass-through state for the next framebuffer draw\r\n'
       '            program.setTint(0f, 0f, 0f, false)\r\n'
       '            glDisable(GL_BLEND)\r\n')
assert old in s, 'renderer cursor block not found'
s = s.replace(old, new)
wr(p, s)

print('ALL OK')
