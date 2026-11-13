#!/usr/bin/env python3
"""wininfo.py [DISPLAY] - list top-level windows: id, name, geometry, map state."""
import ctypes, sys
X11 = ctypes.CDLL("libX11.so.6")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XDefaultRootWindow.restype = ctypes.c_ulong
X11.XQueryTree.restype = ctypes.c_int
X11.XQueryTree.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)), ctypes.POINTER(ctypes.c_uint)]
X11.XGetWindowAttributes.restype = ctypes.c_int
X11.XFetchName.restype = ctypes.c_int
X11.XFetchName.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_char_p)]
class Attr(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int), ("width", ctypes.c_int), ("height", ctypes.c_int), ("border_width", ctypes.c_int), ("depth", ctypes.c_int), ("visual", ctypes.c_void_p), ("root", ctypes.c_ulong), ("class_", ctypes.c_int), ("bit_gravity", ctypes.c_int), ("win_gravity", ctypes.c_int), ("backing_store", ctypes.c_int), ("backing_planes", ctypes.c_ulong), ("backing_pixel", ctypes.c_ulong), ("save_under", ctypes.c_int), ("colormap", ctypes.c_ulong), ("map_installed", ctypes.c_int), ("map_state", ctypes.c_int), ("all_event_masks", ctypes.c_long), ("your_event_mask", ctypes.c_long), ("do_not_propagate_mask", ctypes.c_long), ("override_redirect", ctypes.c_int)]
disp = sys.argv[1] if len(sys.argv) > 1 else ":115"
dpy = X11.XOpenDisplay(disp.encode()); assert dpy
root = X11.XDefaultRootWindow(ctypes.c_void_p(dpy))
r = ctypes.c_ulong(0); p = ctypes.c_ulong(0); ch = ctypes.POINTER(ctypes.c_ulong)(); n = ctypes.c_uint(0)
X11.XQueryTree(ctypes.c_void_p(dpy), ctypes.c_ulong(root), ctypes.byref(r), ctypes.byref(p), ctypes.byref(ch), ctypes.byref(n))
for i in range(n.value):
    w = ch[i]; a = Attr(); X11.XGetWindowAttributes(ctypes.c_void_p(dpy), ctypes.c_ulong(w), ctypes.byref(a))
    nm = ctypes.c_char_p(); X11.XFetchName(ctypes.c_void_p(dpy), ctypes.c_ulong(w), ctypes.byref(nm))
    name = nm.value.decode('utf-8', 'replace') if nm.value else ''
    print(f"{w:#x} {a.x},{a.y} {a.width}x{a.height} map={a.map_state} {name}")
