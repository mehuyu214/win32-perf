#!/usr/bin/env python3
"""probe_egl4.py - raw EGL replicating win32u's egldrv_context_create:
eglGetPlatformDisplay(X11), contexts created with EGL_NO_CONFIG_KHR,
ctx1 with EMPTY attribs (wglCreateContext equivalent), ctx2 shared
with [MAJOR 3, MINOR 3, PROFILE_MASK=CORE] (wined3d CS equivalent).
Window surface from a chosen config. Allocations in each."""
import ctypes, sys

log = open("probe_egl4.log", "w")
def out(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
for f, r in [(EGL.eglGetPlatformDisplay, ctypes.c_void_p),
             (EGL.eglCreateWindowSurface, ctypes.c_void_p),
             (EGL.eglCreateContext, ctypes.c_void_p),
             (EGL.eglGetProcAddress, ctypes.c_void_p),
             (GL.glGetString, ctypes.c_void_p),
             (X11.XOpenDisplay, ctypes.c_void_p),
             (X11.XCreateSimpleWindow, ctypes.c_ulong)]:
    f.restype = r
EGL.eglGetError.restype = ctypes.c_int
GL.glGetError.restype = ctypes.c_int

disp = X11.XOpenDisplay(None)
root = X11.XDefaultRootWindow(ctypes.c_void_p(disp))
win = X11.XCreateSimpleWindow(ctypes.c_void_p(disp), ctypes.c_ulong(root),
                              0, 0, 640, 480, 0, 0, 0)
X11.XMapWindow(ctypes.c_void_p(disp), ctypes.c_ulong(win))
X11.XSync(ctypes.c_void_p(disp), 0)
dpy = EGL.eglGetPlatformDisplay(0x31D5, ctypes.c_void_p(disp), None)  # X11
maj, mnr = ctypes.c_int(0), ctypes.c_int(0)
if not EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(maj), ctypes.byref(mnr)):
    out(f"FAIL init err={EGL.eglGetError():#x}"); sys.exit(1)
out(f"EGL platform-x11 {maj.value}.{mnr.value}")
EGL.eglBindAPI(0x30A0)
attrs = (ctypes.c_int * 15)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8,
                           0x3025, 24, 0x3028, 8, 0x3040, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); ncfg = ctypes.c_int(0)
if not EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg),
                           1, ctypes.byref(ncfg)) or not cfg:
    out(f"FAIL cfg err={EGL.eglGetError():#x}"); sys.exit(1)
surf = EGL.eglCreateWindowSurface(ctypes.c_void_p(dpy), cfg,
                                  ctypes.c_ulong(win), None)
if not surf:
    out(f"FAIL surf err={EGL.eglGetError():#x}"); sys.exit(1)

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

empty = (ctypes.c_int * 1)(0x3038)
ctx1 = EGL.eglCreateContext(ctypes.c_void_p(dpy), None, None, empty)
out(f"ctx1 (no-config, empty attribs) = {ctx1} err={EGL.eglGetError():#x}")
cs = (ctypes.c_int * 7)(0x3098, 3, 0x30FB, 3, 0x30FD, 0x0001, 0x3038)
ctx2 = EGL.eglCreateContext(ctypes.c_void_p(dpy), None, ctypes.c_void_p(ctx1), cs)
out(f"ctx2 (no-config, 3.3 core, shared) = {ctx2} err={EGL.eglGetError():#x}")
if not ctx1 or not ctx2:
    out("FAIL create"); sys.exit(1)
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                   ctypes.c_void_p(surf), ctypes.c_void_p(ctx1))
out(f"ctx1 renderer={ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value} version={ctypes.cast(GL.glGetString(0x1F02), ctypes.c_char_p).value}")
test_allocs("ctx1")
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), None, None, None)
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                   ctypes.c_void_p(surf), ctypes.c_void_p(ctx2))
out(f"ctx2 renderer={ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value} version={ctypes.cast(GL.glGetString(0x1F02), ctypes.c_char_p).value}")
test_allocs("ctx2")
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), None, None, None)
out("DONE")
