#!/usr/bin/env python3
"""probe_glx.py - raw GLX (no Wine): legacy ctx1 vs AttribsARB ctx2
(winex11's exact split). Attribs for ctx2 selectable via GLX2 env:
core | compat | nomask. Allocations tested in each context."""
import ctypes, os, sys

log = open("probe_glxS.log", "w")
def out(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

GL = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
GL.glGetString.restype = ctypes.c_char_p
GL.glGetError.restype = ctypes.c_int
GL.glXGetCurrentDisplay.restype = ctypes.c_void_p
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XCreateColormap.restype = ctypes.c_ulong
X11.XCreateWindow.restype = ctypes.c_ulong

disp = X11.XOpenDisplay(None)
if not disp:
    out("FAIL XOpenDisplay"); sys.exit(1)
dpy = ctypes.c_void_p(disp)
screen = X11.XDefaultScreen(dpy)
fbattrs = (ctypes.c_int * 13)(0, 1,          # GLX_X_RENDERABLE, True
                             8, 0x0001,    # GLX_DRAWABLE_TYPE, WINDOW_BIT
                             0x8002, 0x0001,  # GLX_RENDER_TYPE, RGBA_BIT
                             5, 8, 6, 8, 7, 8)  # RGBA sizes (terminated below)
fbattrs = (ctypes.c_int * 19)(0, 1, 8, 0x0001, 0x8002, 0x0001,
                              5, 8, 6, 8, 7, 8, 4, 8, 20, 24, 19, 8, 0)
nfb = ctypes.c_int(0)
GL.glXChooseFBConfig.restype = ctypes.POINTER(ctypes.c_void_p)
fbs = GL.glXChooseFBConfig(dpy, screen, fbattrs, ctypes.byref(nfb))
if not fbs or nfb.value < 1:
    out("FAIL ChooseFBConfig"); sys.exit(1)
fbc = fbs[0]
GL.glXGetFBConfigAttrib.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                    ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
vis_id = ctypes.c_int(0)
GL.glXGetFBConfigAttrib(dpy, ctypes.c_void_p(fbc), 0x800B, ctypes.byref(vis_id))  # VISUAL_ID
GL.glXGetVisualFromFBConfig.restype = ctypes.c_void_p
vis = GL.glXGetVisualFromFBConfig(dpy, ctypes.c_void_p(fbc))
if not vis:
    out("FAIL visual"); sys.exit(1)
class XVisualInfo(ctypes.Structure):
    _fields_ = [("visual", ctypes.c_void_p), ("visualid", ctypes.c_ulong),
                ("screen", ctypes.c_int), ("depth", ctypes.c_int),
                ("c_class", ctypes.c_int), ("red_mask", ctypes.c_ulong),
                ("green_mask", ctypes.c_ulong), ("blue_mask", ctypes.c_ulong),
                ("colormap_size", ctypes.c_int), ("bits_per_rgb", ctypes.c_int)]
vi = ctypes.cast(vis, ctypes.POINTER(XVisualInfo)).contents
root = X11.XDefaultRootWindow(dpy)
cmap = X11.XCreateColormap(dpy, ctypes.c_ulong(root), ctypes.c_void_p(vi.visual), 0)
class XSetWindowAttributes(ctypes.Structure):
    _fields_ = [("background_pixmap", ctypes.c_ulong),
                ("background_pixel", ctypes.c_ulong),
                ("border_pixmap", ctypes.c_ulong),
                ("border_pixel", ctypes.c_ulong),
                ("bit_gravity", ctypes.c_int), ("win_gravity", ctypes.c_int),
                ("backing_store", ctypes.c_int), ("backing_planes", ctypes.c_ulong),
                ("backing_pixel", ctypes.c_ulong), ("save_under", ctypes.c_int),
                ("event_mask", ctypes.c_long), ("do_not_propagate_mask", ctypes.c_long),
                ("override_redirect", ctypes.c_int), ("colormap", ctypes.c_ulong),
                ("cursor", ctypes.c_ulong)]
swa = XSetWindowAttributes()
swa.colormap = cmap; swa.event_mask = 0
win = X11.XCreateWindow(dpy, ctypes.c_ulong(root), 0, 0, 640, 480, 0,
                        vi.depth, 1, ctypes.c_void_p(vi.visual),
                        (1 << 13) | (1 << 3), ctypes.byref(swa))  # CWColormap|CWEventMask
X11.XMapWindow(dpy, ctypes.c_ulong(win))
X11.XSync(dpy, 0)
out(f"window ok visualid={vi.visualid:#x} depth={vi.depth}")

GL.glXCreateContext.restype = ctypes.c_void_p
GL.glXCreateContextAttribsARB.restype = ctypes.c_void_p
ctx1 = GL.glXCreateContext(dpy, vis, None, 1)
out(f"ctx1 (legacy) = {ctx1}")
mode = os.environ.get("GLX2", "core")
if mode == "core":
    att = (ctypes.c_int * 7)(0x2091, 3, 0x2092, 3, 0x9126, 0x00000001, 0)
elif mode == "compat":
    att = (ctypes.c_int * 7)(0x2091, 3, 0x2092, 3, 0x9126, 0x00000002, 0)
else:
    att = (ctypes.c_int * 5)(0x2091, 3, 0x2092, 3, 0)
ctx2 = GL.glXCreateContextAttribsARB(dpy, ctypes.c_void_p(fbc),
                                     ctypes.c_void_p(ctx1), 1, att)
out(f"ctx2 (attribs {mode}) = {ctx2}")
if not ctx1 or not ctx2:
    out("FAIL create"); sys.exit(1)

EGL = ctypes.CDLL("libEGL.so.1")
EGL.eglGetProcAddress.restype = ctypes.c_void_p
def getproc(name):
    p = EGL.eglGetProcAddress(name.encode())
    if not p:
        p = ctypes.cast(getattr(GL, name, None), ctypes.c_void_p).value
    return p
glGenBuffers = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.POINTER(ctypes.c_uint))(getproc("glGenBuffers"))
glBindBuffer = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint)(getproc("glBindBuffer"))
glBufferData = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint)(getproc("glBufferData"))
glBufferStorage = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint)(getproc("glBufferStorage"))
glGetBufferParameteriv = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int))(getproc("glGetBufferParameteriv"))

def test_allocs(tag):
    b = ctypes.c_uint(0)
    glGenBuffers(1, ctypes.byref(b)); glBindBuffer(0x8892, b)
    glBufferData(0x8892, 3686400, None, 0x88E0)
    e = GL.glGetError(); sz = ctypes.c_int(-1)
    glGetBufferParameteriv(0x8892, 0x8764, ctypes.byref(sz))
    out(f"  {tag} BufferData: err={e:#x} size={sz.value}")
    b2 = ctypes.c_uint(0)
    glGenBuffers(1, ctypes.byref(b2)); glBindBuffer(0x8892, b2)
    glBufferStorage(0x8892, 16777216, None, 0x0001 | 0x0002 | 0x0040 | 0x0080 | 0x0100)
    e = GL.glGetError(); sz = ctypes.c_int(-1)
    glGetBufferParameteriv(0x8892, 0x8764, ctypes.byref(sz))
    out(f"  {tag} BufferStorage: err={e:#x} size={sz.value}")
    glBindBuffer(0x8892, 0)

if not GL.glXMakeCurrent(dpy, ctypes.c_ulong(win), ctypes.c_void_p(ctx1)):
    out("FAIL makeCurrent1"); sys.exit(1)
out(f"ctx1 renderer={GL.glGetString(0x1F01)} version={GL.glGetString(0x1F02)}")
test_allocs("ctx1")
GL.glXMakeCurrent(dpy, 0, None)
if not GL.glXMakeCurrent(dpy, ctypes.c_ulong(win), ctypes.c_void_p(ctx2)):
    out("FAIL makeCurrent2"); sys.exit(1)
out(f"ctx2 renderer={GL.glGetString(0x1F01)} version={GL.glGetString(0x1F02)}")
test_allocs("ctx2")
GL.glXMakeCurrent(dpy, 0, None)
out("DONE")
