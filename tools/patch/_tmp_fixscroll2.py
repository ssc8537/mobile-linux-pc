import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md"
s = io.open(p, encoding="utf-8", newline="").read()
old = """  - 滚轮速度范围 1~5 → **1~9**，`deltaPerScroll` 档位 3=20px 保持不变、9=74px：
    档位 3 = 20（上游原值），档位 1 = 8（比上游慢 2.5 倍，用户要的"再慢一点"）。"""
new = """  - 滚轮速度范围 1~5 → **1~9**。`deltaPerScroll` 分段计算：
    档位 1~3 用 `8 + 档位*4`（12 / 16 / 20 px），档位 3 = 20 px = 上游原值不动；
    档位 4~9 用 `20 + (档位-3)*9`（29 / 38 / 47 / 56 / 65 / 74 px）。
    也就是档位 9 比官方原值慢 3.7 倍（用户要的"再慢一点"），档位 3 保持原样。"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("readme scroll fixed", len(s))
