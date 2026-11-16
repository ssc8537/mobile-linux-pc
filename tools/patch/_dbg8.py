import re, zipfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
blob = b"".join(z.read(n) for n in z.namelist() if n.startswith("classes") and n.endswith(".dex"))
text = blob.decode("latin-1")
for m in re.finditer(r"tiny[-_]osk", text):
    s = max(0, m.start() - 120)
    frag = text[s:m.start() + 160]
    frag = re.sub(r"[^\x20-\x7e]", ".", frag)
    print("...", frag, "...")
    print("-" * 40)
