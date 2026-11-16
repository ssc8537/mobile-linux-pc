import zipfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
want = ("zoom_mis_touch_guard", "cursor_tint_enabled", "mouse_acceleration_strength",
        "osk_pointer_button", "osk_pointer_button", "cursor_tint")
hits = {}
for n in z.namelist():
    if not (n.startswith("res/") and n.endswith(".xml")):
        continue
    d = z.read(n)
    for enc in ("utf-8", "utf-16-le"):
        try:
            s = d.decode(enc, "ignore")
        except Exception:
            continue
        for k in want:
            if k in s:
                hits.setdefault(k, set()).add(n)
for k in want:
    print("%-28s %s" % (k, sorted(hits.get(k, []))[:4]))
