#!/usr/bin/env python3
"""probe_glbuf4.py - does guest VA pressure break the exact in-game map?
Reserves PROT_NONE VA in 256 MiB steps (no RSS cost), re-running the
crash-parameter map (PBO 3686400 STREAM_DRAW, access 0x22) after each
step. Prints the step at which the map starts returning NULL, if ever."""
import ctypes

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
LIBC = ctypes.CDLL("libc.so.6")
for f in ("eglGetDisplay", "eglCreateContext", "eglCreateWindowSurface"):
    getattr(EGL, f).restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int
GL.glGetString.restype = ctypes.c_void_p
GL.glGenBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
GL.glBindBuffer.argtypes = [ctypes.c_uint, ctypes.c_uint]
GL.glBufferData.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint]
GL.glMapBufferRange.restype = ctypes.c_void_p
GL.glMapBufferRange.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_uint]
GL.glGetError.restype = ctypes.c_uint
LIBC.mmap.restype = ctypes.c_void_p
LIBC.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                      ctypes.c_int, ctypes.c_int, ctypes.c_long]
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
GL.glGetError()

PUB = 0x88EC; STREAM_DRAW = 0x88E0
def try_map(tag):
    buf = ctypes.c_uint(0)
    GL.glGenBuffers(1, ctypes.byref(buf))
    GL.glBindBuffer(PUB, buf.value)
    GL.glBufferData(PUB, 3686400, None, STREAM_DRAW)
    e1 = GL.glGetError()
    p = GL.glMapBufferRange(PUB, 0, 3686400, 0x22)
    e2 = GL.glGetError()
    print(f"{tag}: bufdata_err={e1:#x} map={'OK' if p else 'NULL'} map_err={e2:#x}")
    if p:
        GL.glUnmapBuffer(PUB)
    GL.glBindBuffer(PUB, 0)
    GL.glDeleteBuffers(1, ctypes.byref(buf))
    return bool(p)

try_map("step 0 (no pressure)")
PROT_NONE, MAP_PRIVATE, MAP_ANON = 0x0, 0x02, 0x20
STEP = 256 * 1024 * 1024
reserved = 0
for i in range(1, 13):
    r = LIBC.mmap(None, STEP, PROT_NONE, MAP_PRIVATE | MAP_ANON, -1, 0)
    if r in (None, 0xFFFFFFFF):
        print(f"reserve step {i}: mmap FAILED after {reserved} MiB reserved")
        break
    reserved += 256
    if not try_map(f"step {i} ({reserved} MiB reserved)"):
        print(f"MAP BREAKS at {reserved} MiB reserved")
        break
print("DONE")
