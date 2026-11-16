import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\gl\Shaders.kt"
s = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in s else "\n"
t = s.replace("\r\n", "\n")
old = """               vec4 color = texture2D(u_TextureUnit, v_TextureCoordinates).bgra;
               if (u_Tint.a > 0.5) {
                   color.rgb = color.rgb * u_Tint.rgb;
               }
               gl_FragColor = color;"""
new = """               vec4 color = texture2D(u_TextureUnit, v_TextureCoordinates).bgra;
               if (u_Tint.a > 0.5) {
                   // Keep the cursor shape readable: darken/lighten the tint by the
                   // source luminance instead of multiplying, so the black parts of
                   // the pointer turn into a darker shade of the chosen colour
                   // rather than staying black.
                   float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                   color.rgb = u_Tint.rgb * mix(0.30, 1.15, luma);
                   color.rgb = clamp(color.rgb, 0.0, 1.0);
               }
               gl_FragColor = color;"""
assert old in t, "shader tint block not found"
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t if eol == "\n" else t.replace("\n", "\r\n"))
print("shader rewritten", repr(eol))
