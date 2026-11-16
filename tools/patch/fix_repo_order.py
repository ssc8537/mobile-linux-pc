import io

P = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\settings.gradle.kts'
s = io.open(P, 'r', encoding='utf-8', newline='').read()
eol = '\r\n' if '\r\n' in s else '\n'

old = ('        maven { url = uri("https://jitpack.io") }' + eol +
       '        // Local fork: patched AVNC AAR (zoom lock, pointer tuning, cursor, OSK helpers)' + eol +
       '        maven {' + eol +
       '            url = uri("file:///C:/Users/Administrator/Desktop/1-test/1-linux-\u5c0f\u5c0f\u5bb9\u5668/refs-reference-assets-deletable/maven-local")' + eol +
       '            metadataSources { mavenPom(); artifact() }' + eol +
       '        }')
new = ('        // Local fork: patched AVNC AAR (zoom lock, pointer tuning, cursor, OSK helpers).' + eol +
       '        // Must come BEFORE jitpack so the local artifact wins the lookup.' + eol +
       '        maven {' + eol +
       '            url = uri("file:///C:/Users/Administrator/Desktop/1-test/1-linux-\u5c0f\u5c0f\u5bb9\u5668/refs-reference-assets-deletable/maven-local")' + eol +
       '            metadataSources { mavenPom(); artifact() }' + eol +
       '        }' + eol +
       '        maven { url = uri("https://jitpack.io") }')
assert old in s, 'repo block not found'
s = s.replace(old, new, 1)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('reordered')
