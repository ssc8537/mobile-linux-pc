import io
import os

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

p = os.path.join(WS, 'build-env-toolchain', 'ws-gradle-build-copy-deletable', 'tiny_container', 'app', 'src', 'main', 'java', 'com', 'fct', 'tc4', 'ui', 'misc', 'Global.kt')
s = io.open(p, encoding='utf-8', newline='').read()
anchor = """    /** 检查 assets 中是否内置了 rootfs.tar.zst */"""
assert anchor in s, 'anchor missing'
add = """    /**
     * 内置镜像的版本戳。APK 换了镜像就必须重新导入，
     * 否则覆盖安装后旧容器会一直沿用旧镜像（新功能全部不生效）。
     */
    var builtInImageStamp: String
        get() = sharedPrefs.getString("built_in_image_stamp", "") ?: ""
        set(value) = sharedPrefs.edit { putString("built_in_image_stamp", value) }

    /** 读取 assets/rootfs.stamp 里的镜像版本戳 */
    fun readBuiltInImageStamp(): String {
        return try {
            appContext.assets.open("rootfs.stamp").bufferedReader().use { it.readText().trim() }
        } catch (_: Exception) {
            ""
        }
    }

    /** 内置镜像是否和已导入的容器不一致 */
    fun isBuiltInImageOutdated(): Boolean {
        val stamp = readBuiltInImageStamp()
        return stamp.isNotEmpty() && stamp != builtInImageStamp
    }

"""
s = s.replace(anchor, add + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('Global.kt patched')
