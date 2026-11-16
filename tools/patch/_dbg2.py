import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt"
raw = io.open(p, encoding="utf-8", newline="").read()
lines = raw.splitlines(True)
drop = ("import android.view.Gravity", "import android.widget.ImageButton")
kept = [l for l in lines if l.strip() not in drop]
print("before", len(lines), "after", len(kept))
io.open(p, "w", encoding="utf-8", newline="").write("".join(kept))
