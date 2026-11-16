import io
R = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器"
lay = R + r"\avnc-upstream-fork-deletable\app\src\main\res\layout\view_switch_help.xml"
xml = """<?xml version="1.0" encoding="utf-8"?>
<!--
  Local fork: widget area of a preference that needs BOTH a toggle and a help button
  on the same row (used by the cursor colour row). The switch must carry the id
  android:id/switch_widget so SwitchPreference-style binding finds it, and help_btn
  is the same id the rest of the app uses.
-->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <androidx.appcompat.widget.SwitchCompat
        android:id="@android:id/switch_widget"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        android:focusable="false" />

    <ImageButton
        android:id="@+id/help_btn"
        style="@style/ImageButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:contentDescription="@string/desc_help_btn"
        android:src="@drawable/ic_help"
        app:tint="?colorControlNormal" />
</LinearLayout>
"""
io.open(lay, "w", encoding="utf-8", newline="\n").write(xml)
print("wrote", lay, len(xml))
