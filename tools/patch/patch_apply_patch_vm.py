"""V4: add a data-preserving image update path.

When the built-in image is newer than what the phone has, the user gets two
choices: (1) apply only the overlay patch (keeps all personal data), or
(2) re-import the whole image (wipes the container).

Adds ContainerManageViewModel.applyImagePatch() and the progress state used by
the dialog.
"""
import io
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VM = os.path.join(ROOT, 'build-env-toolchain', 'ws-gradle-build-copy-deletable',
                  'tiny_container', 'app', 'src', 'main', 'java', 'com', 'fct', 'tc4',
                  'ui', 'page', 'ContainerManageViewModel.kt')


def read(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write(path, text, eol):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text if eol == '\n' else text.replace('\n', '\r\n'))


def main():
    src = read(VM)
    if 'fun applyImagePatch' in src:
        print('already patched')
        return

    body = '''
    /**
     * 只把内置镜像里的“系统文件”覆盖到现有容器上，保留用户数据。
     *
     * assets 里除了完整的 rootfs.tar.zst，还带了一个 rootfs.patch.tar.zst：
     * 它只包含我们这次新增/修改的文件（任务栏插件、任务管理器、截图、剪贴板、
     * 悬浮键盘、修好的 export.sh 等）。这里把它解压到已有容器目录上，
     * 不删除 dataDir/<code>，所以个人文件、浏览器配置都还在。
     */
    fun applyImagePatch() {
        viewModelScope.launch(Dispatchers.IO) {
            val app = getApplication<Application>()
            val code = Global.autoLaunch.ifBlank {
                Global.installedContainers.firstOrNull() ?: ""
            }
            if (code.isBlank()) {
                _installState.value = InstallState.Failed(
                    app.getString(R.string.tc4_import_missing_code_builtin))
                return@launch
            }

            _installState.value = InstallState.CopyingToCache
            val cacheFile = File(app.filesDir, "rootfs.patch.tar.zst")
            try {
                app.assets.open("rootfs.patch.tar.zst").use { input ->
                    cacheFile.outputStream().use { output ->
                        input.copyTo(output, bufferSize = 8192)
                    }
                }

                _installState.value = InstallState.Installing(
                    code = code,
                    currentStep = InstallStep.EXTRACTING_ROOTFS,
                    startTimeMillis = System.currentTimeMillis(),
                    containerSizeBytes = cacheFile.length(),
                    webpage = null
                )

                execShell {
                    val patch = $$"""
                        export CONTAINER_DIR=$${app.dataDir}/$$code
                        mkdir -p $CONTAINER_DIR
                        $BIN_DIR/proot --link2symlink $BIN_DIR/tar -xf $CACHE_DIR/rootfs.patch.tar.zst -C $CONTAINER_DIR --delay-directory-restore --preserve-permissions
                        $BIN_DIR/rm -f $CACHE_DIR/rootfs.patch.tar.zst
                    """.trimIndent()
                    Global.setupEnvironment()
                    Global.sendCommand(patch)
                    Global.sendCommand("exit")
                }

                Global.builtInImageStamp = Global.readBuiltInImageStamp()
                Global.installedContainers = Global.installedContainers + code
                _installState.value = InstallState.Completed(
                    launchAfterInstall = false,
                    code = code
                )
            } catch (e: Exception) {
                cacheFile.delete()
                _installState.value = InstallState.Failed(
                    app.getString(R.string.tc4_import_failed, e.message ?: ""))
            }
        }
    }

'''
    anchor = '    /** 从 assets 内置 rootfs.tar.zst 开始导入（用户手动点"安装内置容器"触发） */'
    assert anchor in src, 'startBuiltInImport doc anchor not found'
    src = src.replace(anchor, body.lstrip('\n') + anchor, 1)

    write(VM, src, '\n')
    print('patched ContainerManageViewModel: applyImagePatch()')


if __name__ == '__main__':
    main()
