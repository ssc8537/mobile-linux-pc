import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\main\MainActivity.kt'
s = io.open(p, encoding='utf-8', newline='').read()

old = """        if (!Global.isFirstLaunchDone && Global.hasBuiltInRootfs() && Global.installedContainers.isEmpty()) {
            val containerViewModel: ContainerManageViewModel by viewModels()
            containerViewModel.autoInstallBuiltInContainer()
            viewModel.navigateTo(MainViewModel.Screen.ContainerManage)
            return
        }
"""
assert old in s, 'launch anchor missing'
new = """        if (!Global.isFirstLaunchDone && Global.hasBuiltInRootfs() && Global.installedContainers.isEmpty()) {
            val containerViewModel: ContainerManageViewModel by viewModels()
            containerViewModel.autoInstallBuiltInContainer()
            viewModel.navigateTo(MainViewModel.Screen.ContainerManage)
            return
        }

        // 覆盖安装的新 APK 往往带了新镜像；旧容器还在的话，新镜像根本不会导入，
        // 桌面端新功能就全都不生效。这里检测版本戳并提示用户重新导入。
        if (Global.installedContainers.isNotEmpty() && Global.isBuiltInImageOutdated()) {
            askReimportImage()
            return
        }
"""
s = s.replace(old, new, 1)

# add the dialog helper right after onNormalLaunch's closing brace: insert before onImportFile
anchor2 = "    private fun onImportFile(intent: Intent) {"
assert anchor2 in s, 'onImportFile anchor missing'
helper = """    private var reimportPrompted = false

    /** 提示用户重新导入内置镜像（旧容器的数据会被清空） */
    private fun askReimportImage() {
        if (reimportPrompted) return
        reimportPrompted = true
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.tc4_reimport_title)
            .setMessage(R.string.tc4_reimport_message)
            .setCancelable(false)
            .setPositiveButton(R.string.tc4_reimport_confirm) { _, _ ->
                val containerViewModel: ContainerManageViewModel by viewModels()
                containerViewModel.autoInstallBuiltInContainer()
                viewModel.navigateTo(MainViewModel.Screen.ContainerManage)
            }
            .setNegativeButton(R.string.tc4_reimport_later) { _, _ ->
                Global.builtInImageStamp = Global.readBuiltInImageStamp()
                onNormalLaunchContinue()
            }
            .show()
    }

    private fun onNormalLaunchContinue() {
        val autoCode = Global.autoLaunch
        if (autoCode.isNotEmpty() && autoCode in Global.installedContainers) {
            viewModel.navigateTo(MainViewModel.Screen.ContainerMain(autoCode))
        } else {
            if (autoCode.isNotEmpty()) {
                Global.autoLaunch = ""
            }
            viewModel.navigateTo(MainViewModel.Screen.ContainerManage)
        }
    }

"""
s = s.replace(anchor2, helper + anchor2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('MainActivity patched')
