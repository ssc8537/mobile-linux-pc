import io
p = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\avnc-upstream-fork-deletable\app\src\main\java\com\gaurav\avnc\ui\vnc\VncActivity.kt'
raw = io.open(p, encoding='utf-8', newline='').read()
s = raw.replace('\r\n', '\n')

s = s.replace('    private var oskRing: android.view.View? = null\n', '', 1)
assert 'oskRing' not in s

s = s.replace('if (client == null || viewModel.state.value != VncViewModel.State.Connected) {',
              'if (client == null || !viewModel.connected) {', 1)

s = s.replace('''    override fun onStart() {
        super.onStart()
        binding.frameView.onResume()
        applyOskPrefs()''', '''    override fun onStart() {
        super.onStart()
        binding.frameView.onResume()
        applyOskPrefs()''', 1)

s = s.replace('''    override fun onStop() {
        super.onStop()
        virtualKeys.releaseMetaKeys()''', '''    override fun onStop() {
        super.onStop()
        binding.frameContainer.removeCallbacks(oskFollowTick)
        virtualKeys.releaseMetaKeys()''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('fixed')
