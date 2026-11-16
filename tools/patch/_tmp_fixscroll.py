import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
p = R + r"\build-env-toolchain\out-apk-keep-forever\guide-usage-zh.md"
s = io.open(p, encoding="utf-8", newline="").read()
pairs = [
 ("| 滚轮要能更慢 | 范围从 1~5 扩到 **1~9**，档位 1 比原来最慢还慢 2.5 倍 |",
  "| 滚轮要能更慢 | 范围从 1~5 扩到 **1~9**；档位 9 = 74 像素才滚一格，比官方原值慢 3.7 倍 |"),
 ("| 滚轮速度 | 档位 3 | 1~9 | 3 = 官方原值（20 像素 = 1 格）；1 = 8 像素，比原来慢 2.5 倍 |",
  "| 滚轮速度 | 档位 3 | 1~9 | 3 = 官方原值（20 像素 = 1 格）。要更慢就往右调到 9（74 像素 = 1 格，慢 3.7 倍）；往左调更快 |"),
]
for a, b in pairs:
    assert a in s, a[:30]
    s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("guide scroll wording fixed", len(s))

p2 = R + r"\build-env-toolchain\apks-archive-keep-forever\readme-versions-zh.md"
s2 = io.open(p2, encoding="utf-8", newline="").read()
old = """- 滚轮速度范围 1~5 → **1~9**，`deltaPerScroll` 档位 3=20px 保持不变、9=74px：
 档位 3 = 20（上游原值），档位 1 = 8（比上游慢 2.5 倍，用户要的"再慢一点"）。"""
new = """- 滚轮速度范围 1~5 → **1~9**。`deltaPerScroll` 分段计算：
  档位 1~3 用 `8 + 档位*4`（12/16/20 px），档位 3 = 20 px = 上游原值；
  档位 4~9 用 `20 + (档位-3)*9`（29/38/47/56/65/74 px）。
  也就是档位 9 比官方原值慢 3.7 倍（用户要的"再慢一点"），档位 3 保持原样不动。"""
if old in s2:
    s2 = s2.replace(old, new, 1)
    io.open(p2, "w", encoding="utf-8", newline="").write(s2)
    print("readme scroll wording fixed", len(s2))
else:
    print("readme pattern not found; manual check needed")
