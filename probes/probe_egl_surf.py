#!/usr/bin/env python3
"""probe_egl_surf.py - surfaceless-platform EGL: which driver engages,
and swap timing on a pbuffer. Env-driven (GALLIUM_DRIVER etc.)."""
import ctypes, statistics, sys, time

EGL = ctypes.CDLL("libEGL.so.1")
GL = ctypes.CDLL("libGL.so.1")
EGL.eglGetPlatformDisplay.restype = ctypes.c_void_p
EGL.eglCreatePbufferSurface.restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int
EGL.eglQueryString.restype = ctypes.c_char_p
GL.glGetString.restype = ctypes.c_void_p
GL.glClearColor.argtypes = [ctypes.c_float] * 4
GL.glClear.argtypes = [ctypes.c_uint]

dpy = EGL.eglGetPlatformDisplay(0x31DD, None, None)  # SURFACELESS_MESA
if not dpy:
    print(f"FAIL getPlatformDisplay err={EGL.eglGetError():#x}"); sys.exit(1)
mj, mn = ctypes.c_int(0), ctypes.c_int(0)
if not EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(mj), ctypes.byref(mn)):
    print(f"FAIL init err={EGL.eglGetError():#x}"); sys.exit(1)
print("EGL", mj.value, mn.value, EGL.eglQueryString(ctypes.c_void_p(dpy), 0x3053))
EGL.eglBindAPI(0x30A0)
attrs = (ctypes.c_int * 11)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3040, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); n = ctypes.c_int(0)
if not EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg), 1, ctypes.byref(n)) or not cfg:
    print(f"FAIL cfg err={EGL.eglGetError():#x}"); sys.exit(1)
ctx = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, None)
if not ctx:
    print(f"FAIL ctx err={EGL.eglGetError():#x}"); sys.exit(1)
pattr = (ctypes.c_int * 5)(0x3057, 1280, 0x3056, 720, 0x3038)
surf = EGL.eglCreatePbufferSurface(ctypes.c_void_p(dpy), cfg, pattr)
if not surf:
    print(f"FAIL surf err={EGL.eglGetError():#x}"); sys.exit(1)
EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf), ctypes.c_void_p(surf), ctypes.c_void_p(ctx))
ren = GL.glGetString(0x1F01)
print("renderer:", ctypes.cast(ren, ctypes.c_char_p).value)
sw = []
for i in range(30):
    t0 = time.monotonic()
    GL.glClearColor(0.2, 0.4, 0.6, 1.0); GL.glClear(0x4000)
    t1 = time.monotonic()
    EGL.eglSwapBuffers(ctypes.c_void_p(dpy), ctypes.c_void_p(surf))
    t2 = time.monotonic()
    sw.append((t2 - t1) * 1000)
    if i < 3 or i >= 28:
        print(f"{i}: clear={(t1-t0)*1000:.1f} swap={(t2-t1)*1000:.1f}")
print(f"swap_ms med={statistics.median(sw):.1f} max={max(sw):.1f}")
print("DONE")
