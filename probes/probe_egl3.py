#!/usr/bin/env python3
"""probe_egl3.py - raw EGL: replicate winex11's ctx2 exactly.
ctx2 created with EGL_CONTEXT_OPENGL_PROFILE_MASK = CORE (winex11's
dedicated contexts are profile 0x1/core per its +opengl log), shared
with ctx1, made current on the same window surface. Do allocations
fail now? Env EGL2_PROFILE=core|compat|none selects the mask."""
import ctypes, os, sys

log = open("probe_egl3.log", "w")
def out(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
for f, r in [(EGL.eglGetDisplay, ctypes.c_void_p),
             (EGL.eglCreateWindowSurface, ctypes.c_void_p),
             (EGL.eglCreateContext, ctypes.c_void_p),
             (EGL.eglGetProcAddress, ctypes.c_void_p),
             (GL.glGetString, ctypes.c_void_p),
             (X11.XOpenDisplay, ctypes.c_void_p),
             (X11.XCreateSimpleWindow, ctypes.c_ulong)]:
    f.restype = r
EGL.eglGetError.restype = ctypes.c_int
GL.glGetError.restype = ctypes.c_int
GL.glGetIntegerv.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_int)]

disp = X11.XOpenDisplay(None)
root = X11.XDefaultRootWindow(ctypes.c_void_p(disp))
win = X11.XCreateSimpleWindow(ctypes.c_void_p(disp), ctypes.c_ulong(root),
                              0, 0, 640, 480, 0, 0, 0)
X11.XMapWindow(ctypes.c_void_p(disp), ctypes.c_ulong(win))
X11.XSync(ctypes.c_void_p(disp), 0)
dpy = EGL.eglGetDisplay(ctypes.c_void_p(disp))
maj, mnr = ctypes.c_int(0), ctypes.c_int(0)
if not EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(maj), ctypes.byref(mnr)):
    out(f"FAIL init err={EGL.eglGetError():#x}"); sys.exit(1)
EGL.eglBindAPI(0x30A0)
attrs = (ctypes.c_int * 13)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8,
                           0x3040, 0x0004, 0x3033, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); ncfg = ctypes.c_int(0)
if not EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg),
                           1, ctypes.byref(ncfg)) or not cfg:
    out(f"FAIL cfg err={EGL.eglGetError():#x}"); sys.exit(1)
surf = EGL.eglCreateWindowSurface(ctypes.c_void_p(dpy), cfg,
                                  ctypes.c_ulong(win), None)

def getproc(name):
    p = EGL.eglGetProcAddress(name.encode())
    if not p:
        p = ctypes.cast(getattr(GL, name, None), ctypes.c_void_p).value
    return p
glGenBuffers = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.POINTER(ctypes.c_uint))(getproc("glGenBuffers"))
glBindBuffer = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint)(getproc("glBindBuffer"))
glBufferData = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint)(getproc("glBufferData"))
glGetBufferParameteriv = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int))(getproc("glGetBufferParameteriv"))

def test_allocs(tag):
    b = ctypes.c_uint(0)
    glGenBuffers(1, ctypes.byref(b)); glBindBuffer(0x8892, b)
    glBufferData(0x8892, 3686400, None, 0x88E0)
    e = GL.glGetError(); sz = ctypes.c_int(-1)
    glGetBufferParameteriv(0x8892, 0x8764, ctypes.byref(sz))
    pm = ctypes.c_int(0); GL.glGetIntegerv(0x9126, ctypes.byref(pm))
    out(f"  {tag} BufferData: err={e:#x} size={sz.value} profile_mask={pm.value:#x}")
    glBindBuffer(0x8892, 0)

cattr = (ctypes.c_int * 3)(0x3098, 3, 0x3038)
ctx1 = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, cattr)
prof = os.environ.get("EGL2_PROFILE", "core")
if prof == "core":
    cattr2 = (ctypes.c_int * 7)(0x3098, 3, 0x30FB, 3, 0x30FD, 0x0001, 0x3038)
elif prof == "compat":
    cattr2 = (ctypes.c_int * 7)(0x3098, 3, 0x30FB, 3, 0x30FD, 0x0002, 0x3038)
else:
    cattr2 = cattr
ctx2 = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, ctypes.c_void_p(ctx1), cattr2)
err2 = EGL.eglGetError()
out(f"profile mode={prof} ctx1={ctx1} ctx2={ctx2} eglErr={err2:#x}")
if not ctx2:
    out("FAIL ctx2 create"); sys.exit(1)
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                   ctypes.c_void_p(surf), ctypes.c_void_p(ctx1))
out(f"ctx1 renderer={ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value}")
test_allocs("ctx1")
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), None, None, None)
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                   ctypes.c_void_p(surf), ctypes.c_void_p(ctx2))
out(f"ctx2 renderer={ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value}")
test_allocs("ctx2")
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), None, None, None)
out("DONE")
