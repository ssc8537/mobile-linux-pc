# -*- coding: utf-8 -*-
"""
Parse Hacker's Keyboard layout XML (klausw/hackerskeyboard) into a compact
Python table usable by tiny_osk.py.

This is a *port of HK's own layout data*, not a hand-written layout:
the source of truth is res/xml/kbd_full.xml + kbd_symbols.xml + the
keycodes.xml / donottranslate-keymap.xml string tables.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

BASE = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\refs-reference-assets-deletable\hackerskeyboard\app\src\main"
RES = os.path.join(BASE, "res")
OUT = r"C:\Users\Administrator\Desktop\1-test\1-linux-小小容器\tools-probe-scripts-deletable\osk\hk_layout.py"

# HK declares xmlns:android="http://schemas.android.com/apk/res-auto" (its own attrs)
ANDROID = "{http://schemas.android.com/apk/res-auto}"

# ---------------------------------------------------------------- string table
def load_strings(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r'<string\s+name="([^"]+)"\s*>(.*?)</string>', txt, re.S):
        out[m.group(1)] = m.group(2)
    return out

STR = {}
for f in ("donottranslate-keymap.xml", "strings.xml"):
    STR.update(load_strings(os.path.join(RES, "values", f)))

# ------------------------------------------------------------------- integers
INT = {}
ktxt = open(os.path.join(RES, "values", "keycodes.xml"), encoding="utf-8").read()
for m in re.finditer(r'<integer\s+name="([^"]+)"\s*>(-?\d+)</integer>', ktxt):
    INT[m.group(1)] = int(m.group(2))

# HK negative keycodes -> X keysym names
HKCODE_TO_KEYSYM = {
    "key_tab":            ("Tab",       1.0, "key"),
    "key_return":         ("Return",    1.0, "key"),
    "key_space":          ("space",     1.0, "key"),
    "key_shift":          ("Shift_L",   1.0, "mod"),
    "key_delete":         ("BackSpace", 1.0, "key"),
    "key_forward_del":    ("Delete",    1.0, "key"),
    "key_escape":         ("Escape",    1.0, "key"),
    "key_ctrl_left":      ("Control_L", 1.0, "mod"),
    "key_alt_left":       ("Alt_L",     1.0, "mod"),
    "key_meta_left":      ("Super_L",   1.0, "mod"),
    "key_caps_lock":      ("Caps_Lock", 1.0, "mod"),
    "key_num_lock":       ("Num_Lock",  1.0, "mod"),
    "key_fn":             ("Fn",        1.0, "layer"),
    "key_symbol":         ("?123",      1.0, "layer"),
    "key_dpad_up":        ("Up",        1.0, "key"),
    "key_dpad_down":      ("Down",      1.0, "key"),
    "key_dpad_left":      ("Left",      1.0, "key"),
    "key_dpad_right":     ("Right",     1.0, "key"),
    "key_dpad_center":    ("KP_5",      1.0, "key"),
    "key_home":           ("Home",      1.0, "key"),
    "key_end":            ("End",       1.0, "key"),
    "key_insert":         ("Insert",    1.0, "key"),
    "key_page_up":        ("Prior",     1.0, "key"),
    "key_page_down":      ("Next",      1.0, "key"),
}
for i in range(1, 13):
    HKCODE_TO_KEYSYM["key_fkey_f%d" % i] = ("F%d" % i, 1.0, "key")

# plain ASCII label -> X keysym name (punctuation needs names, letters don't)
PUNCT_KEYSYM = {
    "`": "grave", "~": "asciitilde", "!": "exclam", "@": "at", "#": "numbersign",
    "$": "dollar", "%": "percent", "^": "asciicircum", "&": "ampersand",
    "*": "asterisk", "(": "parenleft", ")": "parenright", "-": "minus",
    "_": "underscore", "=": "equal", "+": "plus", "[": "bracketleft",
    "{": "braceleft", "]": "bracketright", "}": "braceright", "\\": "backslash",
    "|": "bar", ";": "semicolon", ":": "colon", "'": "apostrophe",
    '"': "quotedbl", ",": "comma", "<": "less", ".": "period", ">": "greater",
    "/": "slash", "?": "question",
}


def resolve_label(ref):
    """@string/key_ae01_main -> "1";  plain text passes through."""
    if ref is None:
        return None
    if ref.startswith("@string/"):
        return STR.get(ref[len("@string/"):], "")
    return ref


def keysym_for(label):
    if not label:
        return None
    if len(label) == 1:
        ch = label
        if ch.isalnum():
            low = ch.lower()
            return low if ch.islower() or ch.isdigit() else low.upper()
        return PUNCT_KEYSYM.get(ch, ch)
    return label


def parse(path):
    tree = ET.parse(path)
    root = tree.getroot()
    rows = []
    for row in root.findall("Row"):
        cells = []
        for key in row.findall("Key"):
            label = resolve_label(key.get(ANDROID + "keyLabel"))
            shift = resolve_label(key.get(ANDROID + "shiftLabel"))
            popup = resolve_label(key.get(ANDROID + "popupCharacters"))
            codes = key.get(ANDROID + "codes")
            width = key.get(ANDROID + "keyWidth") or ""

            mw = re.match(r"([\d.]+)%p", width)
            # HK uses a 14-column grid: keyWidth 7.142857%p == exactly 1 column
            units = (float(mw.group(1)) / 7.1428571485) if mw else 1.0
            units = max(0.5, round(units, 3))

            sym = None
            role = "key"
            shown = label

            if codes:
                name = codes[len("@integer/"):] if codes.startswith("@integer/") else None
                if name in HKCODE_TO_KEYSYM:
                    ks, _u, r = HKCODE_TO_KEYSYM[name]
                    sym = ks
                    role = r
                    if not shown:
                        shown = {"Return": "Enter", "space": "Space",
                                 "BackSpace": "Bksp", "Shift_L": "Shift",
                                 "Control_L": "Ctrl", "Alt_L": "Alt",
                                 "Super_L": "Win", "Escape": "Esc",
                                 "Num_Lock": "NumLk", "Caps_Lock": "Caps",
                                 "Prior": "PgUp", "Next": "PgDn"}.get(ks, ks)
                elif name and name.startswith("key_fkey_"):
                    sym = "F" + name.split("_")[-1][1:]
                    shown = sym
                elif name:
                    sym = name
                else:
                    try:
                        cp = int(codes)
                        sym = keysym_for(chr(cp))
                        shown = shown or chr(cp)
                    except Exception:
                        sym = None
            else:
                sym = keysym_for(label)
                if label and len(label) > 1 and label not in PUNCT_KEYSYM:
                    sym = label

            if shift and not sym:
                sym = keysym_for(shift)
            if not shown:
                shown = (sym or "").replace("_L", "")

            cells.append({
                "label": shown or "",
                "shift": shift or "",
                "sym": sym,
                "units": units,
                "role": role,
                "popup": popup or "",
            })
        rows.append(cells)
    return rows


def emit(name, rows, fh):
    fh.write("%s = [\n" % name)
    for cells in rows:
        s = sum(c["units"] for c in cells)
        fh.write("    [  # %d keys, sum=%.2f\n" % (len(cells), s))
        for c in cells:
            fh.write("        (%r, %r, %r, %r, %.3f, %r),\n" % (
                c["label"], c["sym"], c["role"], c["shift"],
                c["units"], c["popup"]))
        fh.write("    ],\n")
    fh.write("]\n\n")


full = parse(os.path.join(RES, "xml", "kbd_full.xml"))
sym = parse(os.path.join(RES, "xml", "kbd_symbols.xml"))
sym_shift = parse(os.path.join(RES, "xml", "kbd_symbols_shift.xml"))
compact = parse(os.path.join(RES, "xml", "kbd_compact.xml"))

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("# -*- coding: utf-8 -*-\n")
    fh.write('"""Hacker\'s Keyboard layouts, ported from klausw/hackerskeyboard.\n\n')
    fh.write("Generated by tools-probe-scripts-deletable/gen_hk_layout.py from\n")
    fh.write("app/src/main/res/xml/kbd_{full,compact,symbols,symbols_shift}.xml.\n")
    fh.write("Each cell is (label, keysym, role, shift_label, width_units, popup).\n")
    fh.write('"""\n\n')
    emit("HK_FULL", full, fh)
    emit("HK_COMPACT", compact, fh)
    emit("HK_SYMBOLS", sym, fh)
    emit("HK_SYMBOLS_SHIFT", sym_shift, fh)

print("rows: full=%d compact=%d symbols=%d symbols_shift=%d" %
      (len(full), len(compact), len(sym), len(sym_shift)))
print("keys: full=%d compact=%d symbols=%d symbols_shift=%d" %
      (sum(len(r) for r in full), sum(len(r) for r in compact),
       sum(len(r) for r in sym), sum(len(r) for r in sym_shift)))
print("out:", OUT, os.path.getsize(OUT), "bytes")
