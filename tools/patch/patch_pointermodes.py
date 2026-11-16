import io, sys

path = sys.argv[1]
src = io.open(path, 'r', encoding='utf-8', newline='').read()
assert '\r\n' in src
orig = src

# 1) scroll speed becomes user tunable
old = "    private val deltaPerScroll = 20F //For how much dx/dy, one scroll event will be sent\r\n"
new = ("\r\n"
       "    /**\r\n"
       "     * For how much dx/dy, one scroll event will be sent.\r\n"
       "     *\r\n"
       "     * Local fork: this used to be a hardcoded 20F. It is now derived from the\r\n"
       "     * 'scroll_speed' preference (1..5); 3 (the default) evaluates to the original 20F.\r\n"
       "     * A larger value means more finger travel per wheel click, i.e. slower scrolling.\r\n"
       "     */\r\n"
       "    private val deltaPerScroll: Float\r\n"
       "        get() = 12F + (viewModel.pref.input.scrollSpeed - 1) * 4F\r\n")
assert old in src, "deltaPerScroll not found"
src = src.replace(old, new)

# 2) respect the mouse acceleration switch
old2 = ("        if (accelerate) {\r\n"
        "            accelerator.compute()\r\n")
new2 = ("        // Local fork: acceleration can be disabled by the user\r\n"
        "        if (accelerate && viewModel.pref.input.mouseAcceleration) {\r\n"
        "            accelerator.compute()\r\n")
assert old2 in src, "accelerate block not found"
src = src.replace(old2, new2)

io.open(path, 'w', encoding='utf-8', newline='').write(src)
print('patched', path, 'changed' if src != orig else 'UNCHANGED')
