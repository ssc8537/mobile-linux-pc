#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tiny-osk-caret — publish the text caret position for the Android side.

Runs inside the container (XFCE on X11, displayed through VNC). It writes a
small file that the AVNC viewer on the Android side reads, so the floating
keyboard button can be placed next to the *typing caret* instead of next to
the mouse pointer.

Output file (default /tmp/.tiny_osk_caret), one line, space separated:

    <visible> <x> <y> <w> <h>

`visible` is 1 when a caret / focused text widget is known, 0 otherwise.
Coordinates are root-window pixels of the remote desktop, exactly the space
libvncserver reports pointer positions in.

How the position is obtained, most accurate first:
  1. AT-SPI (libatspi via ctypes): the focused text widget reports the caret
     offset, and the character extents give a precise rectangle. Works for
     GTK3 apps (Thunar, Mousepad, xfce4-terminal) and for Firefox once
     accessibility is enabled, which the image does via env vars.
  2. Fallback: the active window rectangle (`_NET_ACTIVE_WINDOW`), placing the
     button at the window's right edge, vertically at 1/3 height. This is
     where typing usually happens when no accessible caret is exposed.

No third-party dependencies: only libX11/libatspi through ctypes.
"""

import ctypes
import ctypes.util
import os
import sys
import time

OUT = os.environ.get('TINY_OSK_CARET_FILE', '/tmp/.tiny_osk_caret')
LOG = '/tmp/.tiny_osk_caret.log'
POLL_MS = int(os.environ.get('TINY_OSK_CARET_POLL_MS', '180'))

# AtspiStateType order from at-spi2-core/atspi-constants.h
ST_EDITABLE = 7
ST_FOCUSED = 12
ST_SHOWING = 25
ST_SUPPORTS_AUTOCOMPLETION = 37
ST_SELECTABLE_TEXT = 38

# AtspiCoordType
COORD_SCREEN = 0
COORD_WINDOW = 1


def log(msg):
    try:
        with open(LOG, 'a') as f:
            f.write('%s %s\n' % (time.strftime('%H:%M:%S'), msg))
    except OSError:
        pass


# --------------------------------------------------------------------- X11 part

class X11(object):
    def __init__(self):
        self.x = ctypes.CDLL('libX11.so.6')
        self.x.XOpenDisplay.restype = ctypes.c_void_p
        self.dpy = self.x.XOpenDisplay(None)
        if not self.dpy:
            raise RuntimeError('cannot open X display')

    def intern(self, name):
        self.x.XInternAtom.restype = ctypes.c_ulong
        self.x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                       ctypes.c_int]
        return self.x.XInternAtom(self.dpy, name.encode(), 0)

    def active_window(self):
        """_NET_ACTIVE_WINDOW of the root window, or 0."""
        root = self.x.XDefaultRootWindow(self.dpy)
        atom = self.intern('_NET_ACTIVE_WINDOW')
        actual_type = ctypes.c_ulong(0)
        actual_format = ctypes.c_int(0)
        nitems = ctypes.c_ulong(0)
        data = ctypes.POINTER(ctypes.c_ubyte)()
        self.x.XGetWindowProperty.restype = ctypes.c_int
        self.x.XGetWindowProperty.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong,
            ctypes.c_long, ctypes.c_long, ctypes.c_int, ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_void_p)]
        status = self.x.XGetWindowProperty(
            self.dpy, root, atom, 0, 1, 0, 33,  # XA_WINDOW == 33
            ctypes.byref(actual_type), ctypes.byref(actual_format),
            ctypes.byref(nitems), ctypes.byref(data))
        if status != 0 or nitems.value == 0:
            return 0
        win = ctypes.cast(data, ctypes.POINTER(ctypes.c_ulong))[0]
        return int(win)

    def window_rect(self, win):
        """Root-relative geometry of win."""
        if not win:
            return None
        rx = ctypes.c_int(0)
        ry = ctypes.c_int(0)
        self.x.XGetWindowAttributes.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]
        attr = ctypes.create_string_buffer(256)
        if self.x.XGetWindowAttributes(self.dpy, win, attr) == 0:
            return None
        self.x.XTranslateCoordinates.restype = ctypes.c_int
        self.x.XTranslateCoordinates.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong,
            ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ulong)]
        child = ctypes.c_ulong(0)
        ok = self.x.XTranslateCoordinates(self.dpy, win,
                                          self.x.XDefaultRootWindow(self.dpy),
                                          0, 0, ctypes.byref(rx),
                                          ctypes.byref(ry), ctypes.byref(child))
        if ok == 0:
            return None
        # struct _XWindowAttributes: x,y at offset 0,0 -> width,height later;
        # instead ask for geometry which is stable across versions.
        self.x.XGetGeometry.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
        root_ret = ctypes.c_ulong(0)
        gx = ctypes.c_int(0)
        gy = ctypes.c_int(0)
        gw = ctypes.c_uint(0)
        gh = ctypes.c_uint(0)
        bw = ctypes.c_uint(0)
        depth = ctypes.c_uint(0)
        if self.x.XGetGeometry(self.dpy, win, ctypes.byref(root_ret),
                               ctypes.byref(gx), ctypes.byref(gy),
                               ctypes.byref(gw), ctypes.byref(gh),
                               ctypes.byref(bw), ctypes.byref(depth)) == 0:
            return None
        return (int(rx.value), int(ry.value), int(gw.value), int(gh.value))


# ------------------------------------------------------------------ AT-SPI part

class AtSpi(object):
    """Minimal ctypes binding: find the focused text object and its caret."""

    def __init__(self):
        self.lib = None
        for name in ('libatspi.so.0', 'libatspi-2.so.0'):
            try:
                self.lib = ctypes.CDLL(name)
                break
            except OSError:
                continue
        if self.lib is None:
            path = ctypes.util.find_library('atspi-2.0')
            if path:
                try:
                    self.lib = ctypes.CDLL(path)
                except OSError:
                    self.lib = None
        if self.lib is None:
            raise RuntimeError('libatspi not found')
        self.lib.atspi_init()
        self._obj_restype()
        self.err = ctypes.c_void_p(0)

    def _obj_restype(self):
        for fn in ('atspi_get_desktop', 'atspi_accessible_get_child_at_index',
                   'atspi_accessible_get_state_set'):
            getattr(self.lib, fn).restype = ctypes.c_void_p

    def desktop(self):
        return self.lib.atspi_get_desktop(0)

    def children(self, obj, limit=64):
        out = []
        n = self.lib.atspi_accessible_get_child_count(obj, None)
        if n is None or n <= 0:
            return out
        for i in range(min(int(n), limit)):
            c = self.lib.atspi_accessible_get_child_at_index(
                obj, ctypes.c_int(i), None)
            if c:
                out.append(c)
        return out

    def has_state(self, obj, state):
        ss = self.lib.atspi_accessible_get_state_set(obj)
        if not ss:
            return False
        return bool(self.lib.atspi_state_set_contains(
            ctypes.c_void_p(ss), ctypes.c_int(state)))

    def text_caret(self, obj):
        """(x, y, w, h) in screen coordinates, or None."""
        try:
            off = self.lib.atspi_text_get_caret_offset(
                ctypes.c_void_p(obj), None)
        except AttributeError:
            return None
        if off is None or off < 0:
            return None
        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        w = ctypes.c_int(0)
        h = ctypes.c_int(0)
        ok = self.lib.atspi_text_get_character_extents(
            ctypes.c_void_p(obj), ctypes.c_int(off),
            ctypes.c_int(COORD_SCREEN), ctypes.c_int(0),
            ctypes.byref(x), ctypes.byref(y),
            ctypes.byref(w), ctypes.byref(h), None)
        if not ok:
            return None
        return (x.value, y.value, max(1, w.value), max(4, h.value))

    def find_focused_text(self, obj, depth=0):
        if obj is None or depth > 24:
            return None
        focused = self.has_state(obj, ST_FOCUSED)
        if focused and (self.has_state(obj, ST_EDITABLE)
                        or self.has_state(obj, ST_SUPPORTS_AUTOCOMPLETION)
                        or self.has_state(obj, ST_SELECTABLE_TEXT)):
            return obj
        for child in self.children(obj):
            found = self.find_focused_text(child, depth + 1)
            if found is not None:
                return found
        return None

    def caret_rect(self):
        desk = self.desktop()
        if not desk:
            return None
        # The focused widget lives inside one of the desktop's children
        # (applications); walking them one level at a time keeps it cheap.
        for app in self.children(desk, limit=32):
            try:
                node = self.find_focused_text(app)
            except Exception:
                continue
            if node is not None:
                rect = self.text_caret(node)
                if rect:
                    return rect
        return None


def write_rect(visible, rect):
    payload = '0 0 0 0 0\n'
    if visible and rect:
        payload = '1 %d %d %d %d\n' % rect
    tmp = OUT + '.tmp'
    try:
        with open(tmp, 'w') as f:
            f.write(payload)
        os.replace(tmp, OUT)
    except OSError:
        pass


def main():
    x11 = None
    try:
        x11 = X11()
    except Exception as exc:                        # pragma: no cover
        log('no X11: %s' % exc)
    atspi = None
    try:
        atspi = AtSpi()
        log('AT-SPI ready')
    except Exception as exc:
        log('no AT-SPI: %s (falling back to active window)' % exc)

    log('started, out=%s poll=%dms' % (OUT, POLL_MS))
    while True:
        rect = None
        if atspi is not None:
            try:
                rect = atspi.caret_rect()
            except Exception as exc:
                log('atspi error: %s' % exc)
                atspi = None
        if rect is None and x11 is not None:
            try:
                win = x11.window_rect(x11.active_window())
                if win:
                    wx, wy, ww, wh = win
                    # right edge, one third down: where a caret usually sits
                    rect = (wx + ww - 8, wy + max(24, wh // 3), 2, 18)
            except Exception:
                rect = None
        write_rect(rect is not None, rect)
        time.sleep(POLL_MS / 1000.0)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        import traceback
        log('fatal: ' + traceback.format_exc())
        sys.exit(1)
