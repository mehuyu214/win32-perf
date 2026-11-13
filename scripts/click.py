#!/usr/bin/env python3
"""click.py X Y [DISPLAY] - send a synthetic left click at window-relative
coords of the game window (largest 1280x720 child of root) via XSendEvent."""
import ctypes, sys, time

X11 = ctypes.CDLL("libX11.so.6")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XDefaultRootWindow.restype = ctypes.c_ulong
X11.XQueryTree.restype = ctypes.c_int
X11.XQueryTree.argtypes = [ctypes.c_void_p, ctypes.c_ulong,
                           ctypes.POINTER(ctypes.c_ulong),
                           ctypes.POINTER(ctypes.c_ulong),
                           ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)),
                           ctypes.POINTER(ctypes.c_uint)]
X11.XGetWindowAttributes.restype = ctypes.c_int
X11.XGetWindowAttributes.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]
X11.XSendEvent.restype = ctypes.c_int
X11.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int,
                           ctypes.c_long, ctypes.c_void_p]
X11.XFlush.restype = ctypes.c_int
X11.XFlush.argtypes = [ctypes.c_void_p]

class XWindowAttributes(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int),
                ("width", ctypes.c_int), ("height", ctypes.c_int),
                ("border_width", ctypes.c_int), ("depth", ctypes.c_int),
                ("visual", ctypes.c_void_p), ("root", ctypes.c_ulong),
                ("class_", ctypes.c_int), ("bit_gravity", ctypes.c_int),
                ("win_gravity", ctypes.c_int), ("backing_store", ctypes.c_int),
                ("backing_planes", ctypes.c_ulong), ("backing_pixel", ctypes.c_ulong),
                ("save_under", ctypes.c_int), ("colormap", ctypes.c_ulong),
                ("map_installed", ctypes.c_int), ("map_state", ctypes.c_int),
                ("all_event_masks", ctypes.c_long), ("your_event_mask", ctypes.c_long),
                ("do_not_propagate_mask", ctypes.c_long), ("override_redirect", ctypes.c_int)]

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

def find_game_window(dpy, root):
    dummy = ctypes.c_ulong(0); children = ctypes.POINTER(ctypes.c_ulong)()
    n = ctypes.c_uint(0)
    X11.XQueryTree(ctypes.c_void_p(dpy), ctypes.c_ulong(root), ctypes.byref(dummy),
                   ctypes.byref(dummy), ctypes.byref(children), ctypes.byref(n))
    best, bestarea = None, 0
    for i in range(n.value):
        w = children[i]
        attr = XWindowAttributes()
        X11.XGetWindowAttributes(ctypes.c_void_p(dpy), ctypes.c_ulong(w), ctypes.byref(attr))
        area = attr.width * attr.height
        if attr.map_state == 2 and area > bestarea:
            best, bestarea = w, area
    return best

def main():
    x, y = int(sys.argv[1]), int(sys.argv[2])
    disp_name = sys.argv[3] if len(sys.argv) > 3 else ":115"
    dpy = X11.XOpenDisplay(disp_name.encode())
    if not dpy:
        print("FAIL XOpenDisplay"); return 1
    root = X11.XDefaultRootWindow(ctypes.c_void_p(dpy))
    win = find_game_window(dpy, root)
    if not win:
        print("FAIL no window"); return 1
    attr = XWindowAttributes()
    X11.XGetWindowAttributes(ctypes.c_void_p(dpy), ctypes.c_ulong(win), ctypes.byref(attr))
    print(f"window {win:#x} at {attr.x},{attr.y} size {attr.width}x{attr.height}; click {x},{y}")
    for evtype, state in ((4, 0), (5, 0x100)):  # ButtonPress, ButtonRelease
        ev = XEvent()
        ev.xbutton.type = evtype
        ev.xbutton.display = dpy
        ev.xbutton.window = win
        ev.xbutton.root = root
        ev.xbutton.subwindow = 0
        ev.xbutton.time = 0
        ev.xbutton.x = x; ev.xbutton.y = y
        ev.xbutton.x_root = attr.x + x; ev.xbutton.y_root = attr.y + y
        ev.xbutton.state = state
        ev.xbutton.button = 1
        ev.xbutton.same_screen = 1
        mask = 0x100 if evtype == 4 else 0x200  # ButtonPressMask / ButtonReleaseMask
        X11.XSendEvent(ctypes.c_void_p(dpy), ctypes.c_ulong(win), 0, mask, ctypes.byref(ev))
        X11.XFlush(ctypes.c_void_p(dpy))
        time.sleep(0.12)
    print("clicked")
    return 0

sys.exit(main())
