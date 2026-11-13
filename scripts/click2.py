#!/usr/bin/env python3
"""click2.py WINID X Y [DISPLAY] - XSendEvent click to an explicit window id,
with step prints (no XQueryTree walk)."""
import ctypes, sys, time
X11 = ctypes.CDLL("libX11.so.6")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XSendEvent.restype = ctypes.c_int
X11.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int,
                           ctypes.c_long, ctypes.c_void_p]
X11.XFlush.restype = ctypes.c_int
X11.XFlush.argtypes = [ctypes.c_void_p]

class XButtonEvent(ctypes.Structure):
    _fields_ = [("type", ctypes.c_int), ("serial", ctypes.c_ulong),
                ("send_event", ctypes.c_int), ("display", ctypes.c_void_p),
                ("window", ctypes.c_ulong), ("root", ctypes.c_ulong),
                ("subwindow", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("x", ctypes.c_int), ("y", ctypes.c_int),
                ("x_root", ctypes.c_int), ("y_root", ctypes.c_int),
                ("state", ctypes.c_uint), ("button", ctypes.c_uint),
                ("same_screen", ctypes.c_int)]
class XEvent(ctypes.Union):
    _fields_ = [("xbutton", XButtonEvent), ("pad", ctypes.c_long * 24)]

win = int(sys.argv[1], 0); x, y = int(sys.argv[2]), int(sys.argv[3])
disp = sys.argv[4] if len(sys.argv) > 4 else ":115"
dpy = X11.XOpenDisplay(disp.encode())
assert dpy, "XOpenDisplay failed"
print(f"opened {disp}, target win {win:#x}, click {x},{y}", flush=True)
for evtype, state, mask in ((4, 0, 0x100), (5, 0x100, 0x200)):
    ev = XEvent()
    ev.xbutton.type = evtype; ev.xbutton.display = dpy
    ev.xbutton.window = win; ev.xbutton.subwindow = 0; ev.xbutton.time = 0
    ev.xbutton.x = x; ev.xbutton.y = y; ev.xbutton.x_root = x; ev.xbutton.y_root = y
    ev.xbutton.state = state; ev.xbutton.button = 1; ev.xbutton.same_screen = 1
    r = X11.XSendEvent(ctypes.c_void_p(dpy), ctypes.c_ulong(win), 0, mask, ctypes.byref(ev))
    X11.XFlush(ctypes.c_void_p(dpy))
    print(f"sent type={evtype} ret={r}", flush=True)
    time.sleep(0.15)
print("clicked", flush=True)
