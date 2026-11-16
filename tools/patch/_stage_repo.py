import os, shutil, re, sys, json

R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
S = os.path.join(R, "_gh-staging", "mobile-linux-pc")
if os.path.isdir(S):
    shutil.rmtree(S)
os.makedirs(S)

def cp_tree(src, dst, skip_dirs=(), skip_ext=(), skip_names=(), skip_pred=None):
    n = 0
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        if skip_pred and skip_pred(rel):
            dirs[:] = []
            continue
        for f in files:
            if os.path.splitext(f)[1].lower() in skip_ext: continue
            if f in skip_names: continue
            s = os.path.join(root, f)
            if skip_pred:
                sr = os.path.relpath(s, src)
                if skip_pred(sr): continue
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            n += 1
    return n

tot = {}

# 1) upstream app source (clean reference copy, 2.8 MB, no assets/jniLibs)
tot["source/app"] = cp_tree(os.path.join(R, "apps-tiny-container-v423-source"),
                            os.path.join(S, "source", "app"))

# 2) AVNC fork source (our patched version) - skip heavy/derived dirs
tot["source/avnc"] = cp_tree(os.path.join(R, "avnc-upstream-fork-deletable"),
    os.path.join(S, "source", "avnc"),
    skip_dirs={".git", "build", ".gradle", ".kotlin", ".idea", "extern", "jniLibs", ".gradle-cache"},
    skip_ext={".so", ".aar", ".jar", ".apk"},
    skip_names={"local.properties"})

# 3) build scripts
os.makedirs(os.path.join(S, "tools", "build"), exist_ok=True)
n = 0
for f in ["build-apk.ps1", "build-avnc.ps1", "env.ps1", "install-sdk35.ps1"]:
    p = os.path.join(R, "build-env-toolchain", f)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(S, "tools", "build", f)); n += 1
tot["tools/build"] = n

# 4) patch / probe scripts (source only: no wheels, pkl, pyd, logs, big dumps)
def skip_tools(rel):
    low = rel.lower()
    if low.startswith("pyz2" + os.sep) or low.startswith("osk" + os.sep + "__"): return True
    if low.endswith((".pkl", ".pyd", ".whl", ".log", ".zip", ".tar", ".zst", ".dex", ".png", ".jpg")): return True
    if "__pycache__" in low: return True
    return False
tot["tools/patch"] = cp_tree(os.path.join(R, "tools-probe-scripts-deletable"),
    os.path.join(S, "tools", "patch"),
    skip_dirs={"pyz2", "__pycache__"},
    skip_ext={".pkl", ".pyd", ".whl", ".log", ".zip", ".tar", ".zst", ".dex", ".png", ".jpg", ".exe", ".txt"},
    skip_names={"_tok.txt"},
    skip_pred=skip_tools)

# 5) handover docs
tot["docs"] = cp_tree(os.path.join(R, "docs-project-notes-keep-forever"),
                      os.path.join(S, "docs"))

# 6) release notes
os.makedirs(os.path.join(S, "release"), exist_ok=True)
n = 0
for srcf, dstf in [(os.path.join(R, "build-env-toolchain", "apks-archive-keep-forever", "readme-versions-zh.md"), "readme-versions-zh.md"),
                   (os.path.join(R, "build-env-toolchain", "out-apk-keep-forever", "guide-usage-zh.md"), "guide-usage-zh.md")]:
    if os.path.exists(srcf):
        shutil.copy2(srcf, os.path.join(S, "release", dstf)); n += 1
tot["release"] = n

for k, v in tot.items():
    print(f"{k}: {v} files")

sz = 0; cnt = 0
for root, _, files in os.walk(S):
    for f in files:
        cnt += 1; sz += os.path.getsize(os.path.join(root, f))
print(f"TOTAL {cnt} files {sz/1024/1024:.2f} MB")
big = []
for root, _, files in os.walk(S):
    for f in files:
        p = os.path.join(root, f)
        if os.path.getsize(p) > 200_000:
            big.append((os.path.getsize(p), os.path.relpath(p, S)))
for s, p in sorted(big, reverse=True)[:15]:
    print(f"  BIG {s:>9} {p}")
