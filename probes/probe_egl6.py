#!/usr/bin/env python3
"""probe_egl6.py - raw EGL, win32u's internal-context pattern, isolated:
fresh platform-X11 display, NO prior config/surface. Create config-less
contexts: root (profile from env ROOTP) then a second config-less
context sharing it (profile SECP). Report create success + errors.
This is exactly egldrv_context_create's call shape."""
import ctypes, os, sys

log = open("probe_egl6.log", "w")
def out(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

EGL = ctypes.CDLL("libEGL.so.1")
X11 = ctypes.CDLL("libX11.so.6")
EGL.eglGetPlatformDisplay.restype = ctypes.c_void_p
EGL.eglCreateContext.restype = ctypes.c_void_p
EGL.eglGetError.restype = ctypes.c_int

disp = X11.XOpenDisplay(None)
dpy = EGL.eglGetPlatformDisplay(0x31D5, ctypes.c_void_p(disp), None)
maj, mnr = ctypes.c_int(0), ctypes.c_int(0)
if not EGL.eglInitialize(ctypes.c_void_p(dpy), ctypes.byref(maj), ctypes.byref(mnr)):
    out(f"FAIL init err={EGL.eglGetError():#x}"); sys.exit(1)
ext = EGL.eglQueryString(ctypes.c_void_p(dpy), 0x3055)  # EGL_EXTENSIONS
EGL.eglQueryString.restype = ctypes.c_char_p
ext = EGL.eglQueryString(ctypes.c_void_p(dpy), 0x3055)
out(f"EGL {maj.value}.{mnr.value} no_config_ext={'no_config_context' in (ext.decode() if ext else '')}")
EGL.eglBindAPI(0x30A0)

def attribs_for(prof, ver):
    a = []
    if ver:
        a += [0x3098, 3, 0x30FB, 3]
    if prof == "core":
        a += [0x30FD, 0x0001]
    elif prof == "compat":
        a += [0x30FD, 0x0002]
    a += [0x3038]
    return (ctypes.c_int * len(a))(*a)

rootp = os.environ.get("ROOTP", "compat")
secp = os.environ.get("SECP", "core")
root = EGL.eglCreateContext(ctypes.c_void_p(dpy), None, None, attribs_for(rootp, False))
out(f"root (noconfig, profile={rootp}) = {root} err={EGL.eglGetError():#x}")
sec = EGL.eglCreateContext(ctypes.c_void_p(dpy), None, ctypes.c_void_p(root),
                           attribs_for(secp, False))
out(f"second (noconfig, profile={secp}, shared) = {sec} err={EGL.eglGetError():#x}")
third = EGL.eglCreateContext(ctypes.c_void_p(dpy), None, ctypes.c_void_p(root),
                             attribs_for(secp, True))
out(f"third (noconfig, profile={secp}, ver 3.3, shared) = {third} err={EGL.eglGetError():#x}")
out("DONE")
