import zipfile
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
apk = R + r"\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\build\outputs\apk\release\app-release.apk"
z = zipfile.ZipFile(apk)
names = [n for n in z.namelist() if n.startswith("res/")]
print("total res entries:", len(names))
print("res/xml:", [n for n in names if n.startswith("res/xml")][:20])
print("sample:", names[:15])
