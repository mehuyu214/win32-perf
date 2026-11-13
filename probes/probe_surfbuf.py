#!/usr/bin/env python3
"""probe_surfbuf.py - buffer ops on a SURFACELESS-platform EGL context
(the context class winex11 uses for wined3d's CS/backup contexts).
Cases: transient PBO map (in-game burst), BufferStorage persistent map."""
import ctypes

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
EGL.eglGetPlatformDisplay.restype = ctypes.c_void_p
EGL.eglCreateContext.restype = ctypes.c_void_p
EGL.eglCreatePbufferSurface.restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int
EGL.eglQueryString.restype = ctypes.c_char_p
GL.glGetString.restype = ctypes.c_void_p
GL.glGenBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
GL.glBindBuffer.argtypes = [ctypes.c_uint, ctypes.c_uint]
GL.glBufferData.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint]
GL.glBufferStorage.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint]
GL.glMapBufferRange.restype = ctypes.c_void_p
GL.glMapBufferRange.argtypes = [ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_uint]
GL.glGetBufferParameteriv.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int)]
GL.glGetError.restype = ctypes.c_uint

dpy = EGL.eglGetPlatformDisplay(0x31DD, None, None)  # EGL_PLATFORM_SURFACELESS_MESA
assert dpy, "no surfaceless display"
mj, mn = ctypes.c_int(0), ctypes.c_int(0)
assert EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(mj), ctypes.byref(mn)), hex(EGL.eglGetError())
EGL.eglBindAPI(0x30A2)
ncfg = ctypes.c_int(0)
EGL.eglGetConfigs(ctypes.c_void_p(dpy), None, 0, ctypes.byref(ncfg))
print("surfaceless configs:", ncfg.value)
cfgs = (ctypes.c_void_p * max(ncfg.value, 1))()
EGL.eglGetConfigs(ctypes.c_void_p(dpy), cfgs, ncfg.value, ctypes.byref(ncfg))
cfg = cfgs[0]
ctx = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, None)
assert ctx, hex(EGL.eglGetError())
pattr = (ctypes.c_int * 5)(0x3057, 640, 0x3056, 480, 0x3038)
surf = EGL.eglCreatePbufferSurface(ctypes.c_void_p(dpy), cfg, pattr)
assert surf, hex(EGL.eglGetError())
assert EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf), ctypes.c_void_p(surf), ctypes.c_void_p(ctx))
print("renderer:", ctypes.cast(GL.glGetString(0x1F01), ctypes.c_char_p).value)
GL.glGetError()

PUB = 0x88EC; STREAM_DRAW = 0x88E0; AB = 0x8892
# case A: transient burst
buf = ctypes.c_uint(0)
GL.glGenBuffers(1, ctypes.byref(buf)); GL.glBindBuffer(PUB, buf.value)
GL.glBufferData(PUB, 3686400, None, STREAM_DRAW)
e1 = GL.glGetError()
sz = ctypes.c_int(-1); GL.glGetBufferParameteriv(PUB, 0x8764, ctypes.byref(sz))
p = GL.glMapBufferRange(PUB, 0, 3686400, 0x22)
print(f"case A transient: bufdata_err={e1:#x} BUFFER_SIZE={sz.value} map={p} err={GL.glGetError():#x} ->",
      "PASS" if p else "FAIL(NULL)")
if p: GL.glUnmapBuffer(PUB)
GL.glBindBuffer(PUB, 0)
# case B: BufferStorage 64MB + persistent map
b2 = ctypes.c_uint(0)
GL.glGenBuffers(1, ctypes.byref(b2)); GL.glBindBuffer(AB, b2.value)
GL.glBufferStorage(AB, 67108864, None, 0x01 | 0x02 | 0x40 | 0x80 | 0x100)
e2 = GL.glGetError()
sz2 = ctypes.c_int(-1); GL.glGetBufferParameteriv(AB, 0x8764, ctypes.byref(sz2))
q = GL.glMapBufferRange(AB, 0, 67108864, 0xD3)
print(f"case B storage: storage_err={e2:#x} BUFFER_SIZE={sz2.value} map={q} err={GL.glGetError():#x} ->",
      "PASS" if q else "FAIL(NULL)")
print("DONE")
