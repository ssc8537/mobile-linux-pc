import hashlib, zipfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
print("entries:", len(z.namelist()))
for n in ("assets/rootfs.tar.zst", "assets/rootfs.patch.tar.zst", "assets/rootfs.stamp"):
    i = z.getinfo(n)
    h = hashlib.sha256(z.read(n)).hexdigest()[:16]
    print("%-28s len=%d clen=%d method=%d sha=%s" % (n, i.file_size, i.compress_size, i.compress_type, h))
print("stamp:", z.read("assets/rootfs.stamp").decode().strip())
dex = [n for n in z.namelist() if n.startswith("classes") and n.endswith(".dex")]
print("dex:", [(d, z.getinfo(d).file_size) for d in dex])
blob = b"".join(z.read(d) for d in dex)
for needle in (b"tiny-osk", b"tiny_osk", b"OskBridge", b"openRemoteKeyboard", b"readCaretRect",
               b"oskPointerButton", b"osk_pointer_button", b"tc4.osk_trigger", b"tc4.osk_caret",
               b"open-osk", b"osk_request_sent",
               b"mouseAcceleration", b"scrollSpeed", b"cursorTintEnabled", b"ValueLabelPreference",
               b"zoomMisTouchGuard", b"showZoomMisTouchHint", b"applyImagePatch", b"setFZoomLocked",
               b"dev_options_phantom", b"battery_unlimited"):
    print("  %-24s %s" % (needle.decode(), needle in blob))
