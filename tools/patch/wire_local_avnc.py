import io, os


def _find_ws():
    env = os.environ.get('TC_ROOT')
    if env:
        return env
    _d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(_d, 'build-env-toolchain')) or os.path.isdir(
            os.path.join(_d, 'source', 'app')
        ):
            return _d
        _p = os.path.dirname(_d)
        if _p == _d:
            return os.path.dirname(os.path.abspath(__file__))
        _d = _p


WS = _find_ws()
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT = WS
MAVEN_LOCAL_URL = 'file:///' + os.path.join(
    ROOT, 'refs-reference-assets-deletable', 'maven-local'
).replace('\\', '/')
P = os.path.join(ROOT, 'avnc-upstream-fork-deletable', 'app', 'build.gradle')
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
           "            url = uri('" + MAVEN_LOCAL_URL + "')" + eol +
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
            '            url = uri("' + MAVEN_LOCAL_URL + '")\n'
            '            metadataSources { mavenPom(); artifact() }\n'
            '        }')
assert old_repo in s3
s3 = s3.replace(old_repo, new_repo, 1)
io.open(P3, 'w', encoding='utf-8', newline='').write(s3)
print('patched settings.gradle.kts')
