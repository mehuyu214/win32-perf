#!/usr/bin/env python3
"""probe_glxswap.py - raw GLX: window + legacy ctx, clear RED, swap x5
with timestamps; then attribs ctx, clear GREEN, swap x5. Decides whether
the virpipe X11 window-present path works at all."""
import ctypes, time

log = open("probe_glxswap.log", "w")
def out(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

X11 = ctypes.CDLL("libX11.so.6")
GL = ctypes.CDLL("libGL.so.1")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XCreateWindow.restype = ctypes.c_ulong
GL.glXChooseFBConfig.restype = ctypes.POINTER(ctypes.c_void_p)
GL.glXCreateContext.restype = ctypes.c_void_p
GL.glXCreateContextAttribsARB.restype = ctypes.c_void_p
GL.glClearColor.argtypes = [ctypes.c_float]*4
GL.glViewport.argtypes = [ctypes.c_int]*4
GL.glXMakeCurrent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]

dpy = X11.XOpenDisplay(None)
if not dpy: out("FAIL XOpenDisplay"); raise SystemExit(1)
scr = X11.XDefaultScreen(ctypes.c_void_p(dpy))
root = X11.XRootWindow(ctypes.c_void_p(dpy), scr)
fbatt = (ctypes.c_int * 9)(0x2, 4, 0x8015, 0, 0x16, 24, 0x17, 8, 0)
n = ctypes.c_int(0)
cfgs = GL.glXChooseFBConfig(ctypes.c_void_p(dpy), scr, fbatt, ctypes.byref(n))
if n.value == 0: out("FAIL no fbconfig"); raise SystemExit(1)
vi = GL.glXGetVisualFromFBConfig(ctypes.c_void_p(dpy), cfgs[0])
class XVisualInfo(ctypes.Structure):
    _fields_ = [("visual", ctypes.c_void_p), ("visualid", ctypes.c_ulong),
                ("screen", ctypes.c_int), ("depth", ctypes.c_int),
                ("class_", ctypes.c_int), ("red_mask", ctypes.c_ulong),
                ("green_mask", ctypes.c_ulong), ("blue_mask", ctypes.c_ulong),
                ("colormap_size", ctypes.c_int), ("bits_per_rgb", ctypes.c_int),
                ("pad", ctypes.c_int * 4)]
vi = ctypes.cast(vi, ctypes.POINTER(XVisualInfo))[0]
cmap = X11.XCreateColormap(ctypes.c_void_p(dpy), root, ctypes.c_void_p(vi.visual), 0)
class XSetWindowAttributes(ctypes.Structure):
    _fields_ = [("background_pixmap", ctypes.c_ulong), ("background_pixel", ctypes.c_ulong),
                ("border_pixmap", ctypes.c_ulong), ("border_pixel", ctypes.c_ulong),
                ("bit_gravity", ctypes.c_int), ("win_gravity", ctypes.c_int),
                ("backing_store", ctypes.c_int), ("backing_planes", ctypes.c_ulong),
                ("backing_pixel", ctypes.c_ulong), ("save_under", ctypes.c_int),
                ("event_mask", ctypes.c_long), ("do_not_propagate_mask", ctypes.c_long),
                ("override_redirect", ctypes.c_int), ("colormap", ctypes.c_ulong),
                ("cursor", ctypes.c_ulong)]
swa = XSetWindowAttributes()
swa.colormap = cmap; swa.event_mask = 0x20001
win = X11.XCreateWindow(ctypes.c_void_p(dpy), root, 0, 0, 640, 360, 0, vi.depth,
                        1, ctypes.c_void_p(vi.visual), 0x2000 | 0x800, ctypes.byref(swa))
X11.XMapWindow(ctypes.c_void_p(dpy), win)
X11.XFlush(ctypes.c_void_p(dpy))
out(f"window {win:#x} mapped")

def swaps(ctx, r, g, b, tag):
    GL.glXMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_ulong(win), ctypes.c_void_p(ctx))
    GL.glViewport(0, 0, 640, 360)
    for i in range(5):
        t0 = time.time()
        GL.glClearColor(r, g, b, 1.0)
        GL.glClear(0x4000)
        GL.glXSwapBuffers(ctypes.c_void_p(dpy), ctypes.c_ulong(win))
        out(f"{tag} swap{i} {(time.time()-t0)*1000:.1f} ms err={GL.glGetError():#x}")

c1 = GL.glXCreateContext(ctypes.c_void_p(dpy), ctypes.byref(vi), None, 1)
out(f"legacy ctx={c1}")
if c1: swaps(c1, 1.0, 0.0, 0.0, "legacy-red")
GL.glXMakeCurrent(ctypes.c_void_p(dpy), None, None)
att = (ctypes.c_int * 7)(0x2091, 3, 0x2092, 3, 0x9126, 1, 0)
c2 = GL.glXCreateContextAttribsARB(ctypes.c_void_p(dpy), cfgs[0], None, 1, att)
out(f"attribs ctx={c2}")
if c2: swaps(c2, 0.0, 1.0, 0.0, "attribs-green")
out("DONE")
