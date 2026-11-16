import io
p = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\build-env-toolchain\ws-gradle-build-copy-deletable\tiny_container\app\src\main\java\com\fct\tc4\ui\main\MainActivity.kt"
with io.open(p, "r", encoding="utf-8", newline="") as f:
    s = f.read()

old = '''    private fun askReimportImage() {
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
    }'''

new = '''    private fun askReimportImage() {
        if (reimportPrompted) return
        reimportPrompted = true
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.tc4_reimport_title)
            .setMessage(R.string.tc4_reimport_message)
            .setCancelable(false)
            // 推荐：只覆盖系统文件，个人数据和浏览器配置都保留
            .setPositiveButton(R.string.tc4_reimport_patch) { _, _ ->
                val containerViewModel: ContainerManageViewModel by viewModels()
                containerViewModel.applyImagePatch()
                viewModel.navigateTo(MainViewModel.Screen.ContainerManage)
            }
            // 彻底重装：会清空容器里的个人数据
            .setNeutralButton(R.string.tc4_reimport_confirm) { _, _ ->
                val containerViewModel: ContainerManageViewModel by viewModels()
                containerViewModel.autoInstallBuiltInContainer()
                viewModel.navigateTo(MainViewModel.Screen.ContainerManage)
            }
            .setNegativeButton(R.string.tc4_reimport_later) { _, _ ->
                Global.builtInImageStamp = Global.readBuiltInImageStamp()
                onNormalLaunchContinue()
            }
            .show()
    }'''

assert old in s, "askReimportImage block not found"
s = s.replace(old, new, 1)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(s)
print("3-button dialog written")
