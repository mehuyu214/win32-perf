#!/usr/bin/env python3
"""probe_glbuf2.py - persistent/coherent BO map (the path wined3d uses when
GL_ARB_buffer_storage is available): glBufferStorage + glMapBufferRange
with PERSISTENT|COHERENT access, 64 MiB like wined3d's staging BO."""
import ctypes

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
for f in ("eglGetDisplay", "eglCreateContext", "eglCreateWindowSurface"):
    getattr(EGL, f).restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int
EGL.eglQueryString.restype = ctypes.c_char_p
GL.glGetString.restype = ctypes.c_void_p
GL.glGenBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
GL.glBindBuffer.argtypes = [ctypes.c_uint, ctypes.c_uint]
GL.glBufferStorage.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint]
GL.glMapBufferRange.restype = ctypes.c_void_p
GL.glMapBufferRange.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_uint]
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
assert EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(mj), ctypes.byref(mn))
EGL.eglBindAPI(0x30A2)
attrs = (ctypes.c_int * 13)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8, 0x3040, 0x0004, 0x3033, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); n = ctypes.c_int(0)
assert EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg), 1, ctypes.byref(n))
ctx = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, None)
surf = EGL.eglCreateWindowSurface(ctypes.c_void_p(dpy), cfg, ctypes.c_ulong(win), None)
assert EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf), ctypes.c_void_p(surf), ctypes.c_void_p(ctx))
print("renderer:", ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value)
ext = ctypes.cast(GL.glGetString(0x1F03), ctypes.c_char_p).value.decode()
print("has GL_ARB_buffer_storage:", "GL_ARB_buffer_storage" in ext)
GL.glGetError()

GL_ARRAY_BUFFER = 0x8892
MAP_WRITE = 0x0002
MAP_READ = 0x0001
MAP_PERSISTENT = 0x0040
MAP_COHERENT = 0x0080
DYNAMIC_STORAGE = 0x0100
SIZE = 67108864
buf = ctypes.c_uint(0)
GL.glGenBuffers(1, ctypes.byref(buf))
GL.glBindBuffer(GL_ARRAY_BUFFER, buf.value)
GL.glBufferStorage(GL_ARRAY_BUFFER, SIZE, None,
                   MAP_WRITE | MAP_PERSISTENT | DYNAMIC_STORAGE)
print(f"BufferStorage err={GL.glGetError():#x}")
p = GL.glMapBufferRange(GL_ARRAY_BUFFER, 0, SIZE,
                        MAP_WRITE | MAP_READ | MAP_PERSISTENT | MAP_COHERENT | 0x10)
print(f"persistent map ptr={p} err={GL.glGetError():#x} ->",
      "PASS" if p else "FAIL(NULL)")
if p:
    ctypes.memset(ctypes.c_void_p(p), 0x41, 4096)
print("DONE")
