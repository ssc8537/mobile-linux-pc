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

p = os.path.join(WS, 'build-env-toolchain', 'ws-gradle-build-copy-deletable', 'tiny_container', 'app', 'src', 'main', 'java', 'com', 'fct', 'tc4', 'ui', 'page', 'ContainerManageViewModel.kt')
s = io.open(p, encoding='utf-8', newline='').read()
old = """                Global.autoLaunch = code
                Global.isFirstLaunchDone = true
"""
assert old in s, 'auto install anchor missing'
new = """                Global.autoLaunch = code
                Global.isFirstLaunchDone = true
                Global.builtInImageStamp = Global.readBuiltInImageStamp()
                Global.installedContainers = Global.installedContainers + code
"""
s = s.replace(old, new, 1)

old2 = """            try {
                performInstall(code, rawConfig)
                _installState.value = InstallState.Completed(
                    launchAfterInstall = launchAfterInstall,
                    code = code
                )"""
assert old2 in s, 'confirm install anchor missing'
new2 = """            try {
                performInstall(code, rawConfig)
                Global.builtInImageStamp = Global.readBuiltInImageStamp()
                _installState.value = InstallState.Completed(
                    launchAfterInstall = launchAfterInstall,
                    code = code
                )"""
s = s.replace(old2, new2, 1)

old3 = """                processCachedRootfs()
            } catch (e: Exception) {
                cleanCacheFiles()
                _installState.value = InstallState.Failed(
                    app.getString(R.string.tc4_import_builtin_failed, e.message ?: ""))"""
assert old3 in s, 'startBuiltInImport anchor missing'
new3 = """                Global.installedContainers = Global.installedContainers - "xfce"
                processCachedRootfs()
            } catch (e: Exception) {
                cleanCacheFiles()
                _installState.value = InstallState.Failed(
                    app.getString(R.string.tc4_import_builtin_failed, e.message ?: ""))"""
s = s.replace(old3, new3, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ContainerManageViewModel patched')
