import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md'
s = io.open(p, encoding='utf-8').read()
reps = [
 ('# 小小容器 —— V2 功能增强版 交付说明', '# 小小容器 —— V3 功能增强版 交付说明'),
 ('apk-v2-tc423-xfce-zh-mouse-cursor-osk.apk', 'apk-v3-tc423-xfce-zh-osk-settings.apk'),
 ('761,267,121 字节（约 726 MB）', '761,268,661 字节（约 726 MB）'),
 ('F964A464EABE6198BBDDF576F825AE4666E1CF3DD8BD9370D36A5C3C0CFEB135', '913041ADCB3A683978330A305DFDB79084AB0F0B8AB90354A1CFA34D8D2935D6'),
 ('| 签名 | v2 方案，证书 `CN=TinyContainer ZoomPatch` |', '| 签名 | v2 方案，证书 `CN=TinyContainer ZoomPatch`（与 V1/V2 同一把） |'),
 ('装上 V2（可覆盖 V1）', '装上 V3（可覆盖 V1/V2）'),
]
for a, b in reps:
    assert a in s, a
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('guide base updated')
