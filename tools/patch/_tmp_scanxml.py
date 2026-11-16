import zipfile, re
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
hits = {}
for n in z.namelist():
    if not n.startswith("res/") or not n.endswith(".xml"):
        continue
    d = z.read(n)
    plain = re.sub(r"[^\x20-\x7e]", "", d.decode("utf-16-le", "ignore"))
    for k in ("cursor_tint", "mouse_acceleration_strength", "zoom_mis_touch_guard", "osk_pointer_button"):
        if k in plain:
            hits.setdefault(k, []).append(n)
for k in ("cursor_tint", "mouse_acceleration_strength", "zoom_mis_touch_guard", "osk_pointer_button"):
    print(k, "->", hits.get(k))
