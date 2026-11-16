import io, os

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
P = ROOT + r'\avnc-upstream-fork-deletable\app\build.gradle'
s = io.open(P, 'r', encoding='utf-8', newline='').read()
eol = '\r\n' if '\r\n' in s else '\n'

old_ver = "            version = '3.2.2'"
new_ver = "            version = '3.2.2-tc4v2'"
assert old_ver in s, 'version line not found'
s = s.replace(old_ver, new_ver, 1)

# add a local file repository next to the publication so tiny_container can consume it offline
old_pub = "publishing {" + eol + "    publications {"
new_pub = ("publishing {" + eol +
           "    repositories {" + eol +
           "        maven {" + eol +
           "            name = 'localFork'" + eol +
           "            url = uri('file:///C:/Users/Administrator/Desktop/1-test/1-linux-\u5c0f\u5c0f\u5bb9\u5668/refs-reference-assets-deletable/maven-local')" + eol +
           "        }" + eol +
           "    }" + eol +
           "    publications {")
assert old_pub in s, 'publishing block not found'
s = s.replace(old_pub, new_pub, 1)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched avnc build.gradle')

# ---- tiny_container: point the avnc version at the locally published fork
T = ROOT + r'\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container'
P2 = T + r'\gradle\libs.versions.toml'
s2 = io.open(P2, 'r', encoding='utf-8', newline='').read()
assert 'avnc = "030e6c032e"' in s2
s2 = s2.replace('avnc = "030e6c032e"', 'avnc = "3.2.2-tc4v2"')
io.open(P2, 'w', encoding='utf-8', newline='').write(s2)
print('patched libs.versions.toml')

P3 = T + r'\settings.gradle.kts'
s3 = io.open(P3, 'r', encoding='utf-8', newline='').read()
old_repo = '        maven { url = uri("https://jitpack.io") }'
new_repo = ('        maven { url = uri("https://jitpack.io") }\n'
            '        // Local fork: patched AVNC AAR (zoom lock, pointer tuning, cursor, OSK helpers)\n'
            '        maven {\n'
            '            url = uri("file:///C:/Users/Administrator/Desktop/1-test/1-linux-\u5c0f\u5c0f\u5bb9\u5668/refs-reference-assets-deletable/maven-local")\n'
            '            metadataSources { mavenPom(); artifact() }\n'
            '        }')
assert old_repo in s3
s3 = s3.replace(old_repo, new_repo, 1)
io.open(P3, 'w', encoding='utf-8', newline='').write(s3)
print('patched settings.gradle.kts')
