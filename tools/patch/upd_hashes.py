import io
paths = [
 r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md',
 r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\docs-project-notes-keep-forever\log-version-history.md',
]
for p in paths:
    s = io.open(p, encoding='utf-8', newline='').read()
    s = s.replace('761,268,661', '761,288,905')
    s = s.replace('732,820,293', '732,840,538')
    s = s.replace('913041ADCB3A683978330A305DFDB79084AB0F0B8AB90354A1CFA34D8D2935D6',
                  '3EEE8A5CCD85C635BF636152D87D1F64F1DED0F607A45602867A4ABD74455AD4')
    s = s.replace('490CB010F333BE55176342F89DE4D997E15D212E294D90B5754F671D84AB611D',
                  'CDCA41CDE1CFC8CF683A9FCC8D42119F917FC99E34367BF00C0C6BD6A166C0E3')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('updated', p.rsplit(chr(92),1)[-1])
