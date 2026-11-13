#!/usr/bin/env python3
"""probe_egl.py - pure EGL/GLES-layer swap timing under qemu-i386 (no Wine).

Runs with the sysroot's python3.12 + ctypes against the sysroot's
libEGL/libGLESv2/libX11 (same libs Wine's winex11 uses).
Modes:
  win   - X11 window surface 1280x720: loop { glClear; eglSwapBuffers },
          per-swap ms logged.
  pbuf  - 1280x720 pbuffer surface: same loop (no X presentation leg).
Usage: probe_egl.py [win|pbuf] [frames]
Writes probe_egl_<mode>.log in CWD and prints summary.
"""
import ctypes, os, statistics, sys, time

MODE = sys.argv[1] if len(sys.argv) > 1 else "win"
FRAMES = int(sys.argv[2]) if len(sys.argv) > 2 else 40
log = open(f"probe_egl_{MODE}.log", "w")
def out(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

EGL = ctypes.CDLL("libEGL.so.1")
GLES = ctypes.CDLL("libGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
EGL.eglGetDisplay.restype = ctypes.c_void_p
EGL.eglCreateWindowSurface.restype = ctypes.c_void_p
EGL.eglCreatePbufferSurface.restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XCreateSimpleWindow.restype = ctypes.c_ulong

disp = X11.XOpenDisplay(None)
if not disp:
    out("FAIL XOpenDisplay"); sys.exit(1)
root = X11.XDefaultRootWindow(ctypes.c_void_p(disp))
win = X11.XCreateSimpleWindow(ctypes.c_void_p(disp), ctypes.c_ulong(root),
                              0, 0, 1280, 720, 0, 0, 0)
X11.XMapWindow(ctypes.c_void_p(disp), ctypes.c_ulong(win))
X11.XSync(ctypes.c_void_p(disp), 0)

dpy = EGL.eglGetDisplay(ctypes.c_void_p(disp))
if not dpy:
    out("FAIL eglGetDisplay"); sys.exit(1)
maj, mnr = ctypes.c_int(0), ctypes.c_int(0)
if not EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(maj), ctypes.byref(mnr)):
    out(f"FAIL eglInitialize err={EGL.eglGetError():#x}"); sys.exit(1)
out(f"EGL {maj.value}.{mnr.value}")
EGL.eglBindAPI(0x30A0)  # EGL_OPENGL_API... use ES below if fails
attrs = (ctypes.c_int * 13)(0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8,
                           0x3040, 0x0004, 0x3033, 0x0004, 0x3038)
cfg = ctypes.c_void_p(0); ncfg = ctypes.c_int(0)
if not EGL.eglChooseConfig(ctypes.c_void_p(dpy), attrs, ctypes.byref(cfg),
                           1, ctypes.byref(ncfg)) or not cfg:
    out(f"FAIL chooseConfig err={EGL.eglGetError():#x}"); sys.exit(1)
EGL.eglBindAPI(0x30A0)
cattr = (ctypes.c_int * 3)(0x3098, 2, 0x3038)  # CONTEXT_CLIENT_VERSION, 2
ctx = EGL.eglCreateContext(ctypes.c_void_p(dpy), cfg, None, cattr)
if not ctx:
    out(f"FAIL createContext err={EGL.eglGetError():#x}"); sys.exit(1)
if MODE == "win":
    surf = EGL.eglCreateWindowSurface(ctypes.c_void_p(dpy), cfg,
                                      ctypes.c_ulong(win), None)
else:
    pattr = (ctypes.c_int * 5)(0x3057, 1280, 0x3056, 720, 0x3038)
    surf = EGL.eglCreatePbufferSurface(ctypes.c_void_p(dpy), cfg, pattr)
if not surf:
    out(f"FAIL createSurface({MODE}) err={EGL.eglGetError():#x}"); sys.exit(1)
if not EGL.eglMakeCurrent(ctypes.c_void_p(dpy), ctypes.c_void_p(surf),
                          ctypes.c_void_p(surf), ctypes.c_void_p(ctx)):
    out(f"FAIL makeCurrent err={EGL.eglGetError():#x}"); sys.exit(1)
GLES.glClearColor.argtypes = [ctypes.c_float]*4; GLES.glClear.argtypes = [ctypes.c_uint]; GLES.glGetString.restype = ctypes.c_void_p
ren = GLES.glGetString(0x1F01)
EGL.eglSwapInterval(ctypes.c_void_p(dpy), 0)
out(f"renderer: {ctypes.cast(ren, ctypes.c_char_p).value}")
out(f"mode={MODE} frames={FRAMES}: per-swap ms (clear;swap;frame)")
swaps = []
for i in range(FRAMES):
    t0 = time.monotonic()
    GLES.glClearColor(0.2, 0.4, 0.6, 1.0)
    GLES.glClear(0x00004000)
    t1 = time.monotonic()
    EGL.eglSwapBuffers(ctypes.c_void_p(dpy), ctypes.c_void_p(surf))
    t2 = time.monotonic()
    swaps.append((t2 - t1) * 1000)
    out(f"{i}: clear={(t1-t0)*1000:.1f} swap={(t2-t1)*1000:.1f} total={(t2-t0)*1000:.1f}")
sv = sorted(swaps)
out(f"swap_ms med={statistics.median(swaps):.1f} p90={sv[int(len(sv)*0.9)]:.1f} max={sv[-1]:.1f}")
out("DONE")
log.close()
