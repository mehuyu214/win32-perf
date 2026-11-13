#!/usr/bin/env python3
"""probe_glbuf.py - glMapBufferRange behaviour in isolation (guest GL).
Replicates the failing call from the game crash log: PIXEL_UNPACK_BUFFER,
BufferData(3686400, NULL, STREAM_DRAW), MapBufferRange(0, 3686400, 0x22),
plus variants. Prints PASS/FAIL per case with glGetError."""
import ctypes, os, sys

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
EGL.eglGetDisplay.restype = ctypes.c_void_p
EGL.eglCreateContext.restype = ctypes.c_void_p
EGL.eglCreateWindowSurface.restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int
EGL.eglQueryString.restype = ctypes.c_char_p
GL.glGetString.restype = ctypes.c_void_p
GL.glGenBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
GL.glBindBuffer.argtypes = [ctypes.c_uint, ctypes.c_uint]
GL.glBufferData.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint]
GL.glMapBufferRange.restype = ctypes.c_void_p
GL.glMapBufferRange.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_uint]
GL.glMapBuffer.restype = ctypes.c_void_p
GL.glMapBuffer.argtypes = [ctypes.c_uint, ctypes.c_uint]
GL.glGetError.restype = ctypes.c_uint
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XCreateSimpleWindow.restype = ctypes.c_ulong
X11.XDefaultRootWindow.restype = ctypes.c_ulong

disp = X11.XOpenDisplay(b":115")
root = X11.XDefaultRootWindow(ctypes.c_void_p(disp))
win = X11.XCreateSimpleWindow(ctypes.c_void_p(disp), root, 0, 0, 640, 480, 0, 0, 0)
X11.XMapWindow(ctypes.c_void_p(disp), ctypes.c_ulong(win))
X11.XSync(ctypes.c_void_p(disp), 0)
dpy = EGL.eglGetDisplay(ctypes.c_void_p(disp))
mj, mn = ctypes.c_int(0), ctypes.c_int(0)
assert EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(mj), ctypes.byref(mn)), hex(EGL.eglGetError())
EGL.eglBindAPI(0x30A2)  # EGL_OPENGL_API (desktop GL, like winex11)
attrs = (ctypes.c_int * 13)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8, 0x3040, 0x0004, 0x3033, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); n = ctypes.c_int(0)
assert EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg), 1, ctypes.byref(n))
ctx = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, None)
surf = EGL.eglCreateWindowSurface(ctypes.c_void_p(dpy), cfg, ctypes.c_ulong(win), None)
assert EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf), ctypes.c_void_p(surf), ctypes.c_void_p(ctx))
print("renderer:", ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value)
GL.glGetError()

GL_PIXEL_UNPACK_BUFFER = 0x88EC
GL_ARRAY_BUFFER = 0x8892
GL_STREAM_DRAW = 0x88E0
GL_DYNAMIC_DRAW = 0x88E8

def case(name, target, size, usage, access):
    buf = ctypes.c_uint(0)
    GL.glGenBuffers(1, ctypes.byref(buf))
    GL.glBindBuffer(target, buf.value)
    GL.glBufferData(target, size, None, usage)
    e1 = GL.glGetError()
    p = GL.glMapBufferRange(target, 0, size, access)
    e2 = GL.glGetError()
    print(f"case {name}: bufdata_err={e1:#x} map_ptr={p} map_err={e2:#x} ->",
          "PASS" if p else "FAIL(NULL)")
    if p:
        ctypes.memset(ctypes.c_void_p(p), 0x41, min(size, 4096))
        GL.glUnmapBuffer(target)
    GL.glBindBuffer(target, 0)

case("exact-crash-params", GL_PIXEL_UNPACK_BUFFER, 3686400, GL_STREAM_DRAW, 0x22)
case("write-only", GL_PIXEL_UNPACK_BUFFER, 3686400, GL_STREAM_DRAW, 0x02)
case("write+invalidate-range", GL_PIXEL_UNPACK_BUFFER, 3686400, GL_STREAM_DRAW, 0x12)
case("small-512k", GL_PIXEL_UNPACK_BUFFER, 524288, GL_STREAM_DRAW, 0x22)
case("array-buffer", GL_ARRAY_BUFFER, 3686400, GL_STREAM_DRAW, 0x22)
case("dynamic-draw", GL_PIXEL_UNPACK_BUFFER, 3686400, GL_DYNAMIC_DRAW, 0x22)
# legacy glMapBuffer fallback path
buf = ctypes.c_uint(0)
GL.glGenBuffers(1, ctypes.byref(buf)); GL.glBindBuffer(GL_PIXEL_UNPACK_BUFFER, buf.value)
GL.glBufferData(GL_PIXEL_UNPACK_BUFFER, 3686400, None, GL_STREAM_DRAW); GL.glGetError()
p = GL.glMapBuffer(GL_PIXEL_UNPACK_BUFFER, 0x88B9)  # WRITE_ONLY
print(f"case legacy-glMapBuffer: ptr={p} err={GL.glGetError():#x} ->", "PASS" if p else "FAIL(NULL)")
print("DONE")
