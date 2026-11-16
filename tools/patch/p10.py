import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\build.gradle'
b = open(p,'rb').read()
assert b[:3] != b'\xef\xbb\xbf'
s = b.decode('utf-8')
assert "version = '3.2.2-tc4v3'" in s
s = s.replace("version = '3.2.2-tc4v3'", "version = '3.2.2-tc4v4'", 1)
open(p,'wb').write(s.encode('utf-8'))
print('avnc version -> tc4v4')

p2 = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\gradle\libs.versions.toml'
b2 = open(p2,'rb').read()
s2 = b2.decode('utf-8')
assert 'avnc = "3.2.2-tc4v3"' in s2
s2 = s2.replace('avnc = "3.2.2-tc4v3"', 'avnc = "3.2.2-tc4v4"', 1)
open(p2,'wb').write(s2.encode('utf-8'))
print('consumer -> tc4v4')
