#!/usr/bin/env python3
"""xtest.py MODE ARGS [DISPLAY] - XTEST input via libXtst (xdotool replacement).
Modes: click X Y | key KEYSYM_NAME | move X Y | focus WINID"""
import ctypes, sys, time
X11 = ctypes.CDLL("libX11.so.6")
import os
XT = ctypes.CDLL(os.environ.get("XTST_LIB", "libXtst.so.6"))
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XDefaultRootWindow.restype = ctypes.c_ulong
X11.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
X11.XFlush.argtypes = [ctypes.c_void_p]
X11.XKeysymToKeycode.restype = ctypes.c_ubyte
X11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XStringToKeysym.restype = ctypes.c_ulong
X11.XStringToKeysym.argtypes = [ctypes.c_char_p]
XT.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
XT.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
XT.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
disp = sys.argv[-1] if sys.argv[-1].startswith(":") else ":115"
args = sys.argv[1:-1] if sys.argv[-1].startswith(":") else sys.argv[1:]
dpy = X11.XOpenDisplay(disp.encode()); assert dpy, "no display"
mode = args[0]
if mode == "click":
    x, y = int(args[1]), int(args[2])
    XT.XTestFakeMotionEvent(ctypes.c_void_p(dpy), -1, x, y, 0)
    X11.XFlush(ctypes.c_void_p(dpy)); time.sleep(0.05)
    XT.XTestFakeButtonEvent(ctypes.c_void_p(dpy), 1, 1, 0); X11.XFlush(ctypes.c_void_p(dpy))
    time.sleep(0.1)
    XT.XTestFakeButtonEvent(ctypes.c_void_p(dpy), 1, 0, 0); X11.XFlush(ctypes.c_void_p(dpy))
    print(f"xtest click {x},{y} on {disp}", flush=True)
elif mode == "holdclick":
    x, y, secs = int(args[1]), int(args[2]), float(args[3])
    XT.XTestFakeMotionEvent(ctypes.c_void_p(dpy), -1, x, y, 0); X11.XFlush(ctypes.c_void_p(dpy))
    XT.XTestFakeButtonEvent(ctypes.c_void_p(dpy), 1, 1, 0); X11.XFlush(ctypes.c_void_p(dpy))
    time.sleep(secs)
    XT.XTestFakeButtonEvent(ctypes.c_void_p(dpy), 1, 0, 0); X11.XFlush(ctypes.c_void_p(dpy))
    print(f"xtest hold-click {x},{y} {secs}s on {disp}", flush=True)
elif mode == "move":
    XT.XTestFakeMotionEvent(ctypes.c_void_p(dpy), -1, int(args[1]), int(args[2]), 0); X11.XFlush(ctypes.c_void_p(dpy))
    print(f"xtest move {args[1]},{args[2]} on {disp}", flush=True)
elif mode == "key":
    ks = X11.XStringToKeysym(args[1].encode())
    kc = X11.XKeysymToKeycode(ctypes.c_void_p(dpy), ks)
    XT.XTestFakeKeyEvent(ctypes.c_void_p(dpy), kc, 1, 0); X11.XFlush(ctypes.c_void_p(dpy))
    time.sleep(0.08)
    XT.XTestFakeKeyEvent(ctypes.c_void_p(dpy), kc, 0, 0); X11.XFlush(ctypes.c_void_p(dpy))
    print(f"xtest key {args[1]} kc={kc} on {disp}", flush=True)
elif mode == "focus":
    X11.XSetInputFocus(ctypes.c_void_p(dpy), int(args[1], 0), 0, 0); X11.XFlush(ctypes.c_void_p(dpy))
    print(f"focus {args[1]} on {disp}", flush=True)
