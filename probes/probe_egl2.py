#!/usr/bin/env python3
"""probe_egl2.py - raw EGL (no Wine/WGL): do buffer allocations fail in
the SECOND EGL context on the X11 platform, as they do via WGL?
Creates ctx1 and ctx2 (shared) on one window surface; in each, tries
glBufferData(3.6MB) and glBufferStorage(16MiB), prints renderer.
Env: GALLIUM_DRIVER selects softpipe/llvmpipe."""
import ctypes, os, sys

log = open("probe_egl2.log", "w")
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

disp = X11.XOpenDisplay(None)
if not disp:
    out("FAIL XOpenDisplay"); sys.exit(1)
root = X11.XDefaultRootWindow(ctypes.c_void_p(disp))
win = X11.XCreateSimpleWindow(ctypes.c_void_p(disp), ctypes.c_ulong(root),
                              0, 0, 640, 480, 0, 0, 0)
X11.XMapWindow(ctypes.c_void_p(disp), ctypes.c_ulong(win))
X11.XSync(ctypes.c_void_p(disp), 0)

dpy = EGL.eglGetDisplay(ctypes.c_void_p(disp))
maj, mnr = ctypes.c_int(0), ctypes.c_int(0)
if not EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(maj), ctypes.byref(mnr)):
    out(f"FAIL eglInitialize err={EGL.eglGetError():#x}"); sys.exit(1)
out(f"EGL {maj.value}.{mnr.value}")
EGL.eglBindAPI(0x30A0)  # EGL_OPENGL_API
attrs = (ctypes.c_int * 13)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8,
                           0x3040, 0x0004, 0x3033, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); ncfg = ctypes.c_int(0)
if not EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg),
                           1, ctypes.byref(ncfg)) or not cfg:
    out(f"FAIL chooseConfig err={EGL.eglGetError():#x}"); sys.exit(1)
surf = EGL.eglCreateWindowSurface(ctypes.c_void_p(dpy), cfg,
                                  ctypes.c_ulong(win), None)
if not surf:
    out(f"FAIL windowSurface err={EGL.eglGetError():#x}"); sys.exit(1)

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
GL_ARRAY_BUFFER = 0x8892; GL_BUFFER_SIZE = 0x8764; GL_STREAM_DRAW = 0x88E0

def test_allocs(tag):
    b = ctypes.c_uint(0)
    glGenBuffers(1, ctypes.byref(b)); glBindBuffer(GL_ARRAY_BUFFER, b)
    glBufferData(GL_ARRAY_BUFFER, 3686400, None, GL_STREAM_DRAW)
    e = GL.glGetError(); sz = ctypes.c_int(-1)
    glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, ctypes.byref(sz))
    out(f"  {tag} BufferData: err={e:#x} size={sz.value}")
    b2 = ctypes.c_uint(0)
    glGenBuffers(1, ctypes.byref(b2)); glBindBuffer(GL_ARRAY_BUFFER, b2)
    glBufferStorage(GL_ARRAY_BUFFER, 16777216, None, 0x0001 | 0x0002 | 0x0040 | 0x0080 | 0x0100)
    e = GL.glGetError(); sz = ctypes.c_int(-1)
    glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, ctypes.byref(sz))
    out(f"  {tag} BufferStorage: err={e:#x} size={sz.value}")
    glBindBuffer(GL_ARRAY_BUFFER, 0)

cattr = (ctypes.c_int * 3)(0x3098, 3, 0x3038)
ctx1 = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, cattr)
if not ctx1:
    out(f"FAIL ctx1 err={EGL.eglGetError():#x}"); sys.exit(1)
ctx2 = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, ctypes.c_void_p(ctx1), cattr)
if not ctx2:
    out(f"FAIL ctx2 err={EGL.eglGetError():#x}"); sys.exit(1)
out(f"ctx1={ctx1:#x} ctx2={ctx2:#x}")

if not EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                          ctypes.c_void_p(surf), ctypes.c_void_p(ctx1)):
    out(f"FAIL current1 err={EGL.eglGetError():#x}"); sys.exit(1)
out(f"ctx1 renderer={ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value}")
test_allocs("ctx1")
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), None, None, None)
if not EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                          ctypes.c_void_p(surf), ctypes.c_void_p(ctx2)):
    out(f"FAIL current2 err={EGL.eglGetError():#x}"); sys.exit(1)
out(f"ctx2 renderer={ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value}")
test_allocs("ctx2")
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), None, None, None)
out("DONE")
