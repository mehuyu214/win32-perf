#!/usr/bin/env python3
"""drag.py X1 Y1 X2 Y2 [DISPLAY] - XTEST drag: press at (X1,Y1),
stepped motion to (X2,Y2), release. For config-UI sliders."""
import ctypes, os, sys, time
X11 = ctypes.CDLL("libX11.so.6")
XT = ctypes.CDLL(os.environ.get("XTST_LIB", "libXtst.so.6"))
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XFlush.argtypes = [ctypes.c_void_p]
XT.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
XT.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
disp = sys.argv[-1] if sys.argv[-1].startswith(":") else ":116"
args = sys.argv[1:-1] if sys.argv[-1].startswith(":") else sys.argv[1:]
x1, y1, x2, y2 = (int(a) for a in args[:4])
dpy = X11.XOpenDisplay(disp.encode()); assert dpy, "no display"
vp = ctypes.c_void_p(dpy)
XT.XTestFakeMotionEvent(vp, -1, x1, y1, 0); X11.XFlush(vp); time.sleep(0.15)
XT.XTestFakeButtonEvent(vp, 1, 1, 0); X11.XFlush(vp); time.sleep(0.25)
steps = 12
for i in range(1, steps + 1):
    x = x1 + (x2 - x1) * i // steps
    y = y1 + (y2 - y1) * i // steps
    XT.XTestFakeMotionEvent(vp, -1, x, y, 0); X11.XFlush(vp); time.sleep(0.06)
time.sleep(0.2)
XT.XTestFakeButtonEvent(vp, 1, 0, 0); X11.XFlush(vp)
print(f"drag {x1},{y1} -> {x2},{y2} on {disp}", flush=True)
