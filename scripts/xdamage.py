#!/usr/bin/env python3
"""Count XDamage events on the game window for DUR seconds.

DamageNotify (DeltaRectangles) fires when the X server receives new
content for the window — i.e. presents that actually LAND. Compare with
the guest's swap rate (GALLIUM_HUD) to separate case A from B/C.
Usage: xdamage.py DURATION_SEC [DISPLAY]  -> prints JSON summary.
"""
import ctypes, json, os, sys, time

X11 = ctypes.CDLL("libX11.so.6")
XD = ctypes.CDLL("libXdamage.so.1")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XInternAtom.restype = ctypes.c_ulong

class XWindowAttributes(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int),
                ("width", ctypes.c_int), ("height", ctypes.c_int),
                ("border_width", ctypes.c_int), ("depth", ctypes.c_int),
                ("visual", ctypes.c_void_p), ("root", ctypes.c_ulong),
                ("class_", ctypes.c_int), ("bit_gravity", ctypes.c_int),
                ("win_gravity", ctypes.c_int), ("backing_store", ctypes.c_int),
                ("backing_planes", ctypes.c_ulong), ("backing_pixel", ctypes.c_ulong),
                ("save_under", ctypes.c_int), ("colormap", ctypes.c_ulong),
                ("map_installed", ctypes.c_int), ("map_state", ctypes.c_int),
                ("all_event_masks", ctypes.c_long), ("your_event_mask", ctypes.c_long),
                ("do_not_propagate_mask", ctypes.c_long), ("override_redirect", ctypes.c_int),
                ("screen", ctypes.c_void_p)]

def find_game_window(dpy):
    root = X11.XDefaultRootWindow(ctypes.c_void_p(dpy))
    best = [None]
    def walk(win, depth=0):
        attr = XWindowAttributes()
        if not X11.XGetWindowAttributes(ctypes.c_void_p(dpy), ctypes.c_ulong(win), ctypes.byref(attr)):
            return
        if attr.map_state == 2 and attr.width >= 1000 and attr.height >= 600:
            best[0] = win
        if depth > 6:
            return
        n = ctypes.c_uint(0); children = ctypes.POINTER(ctypes.c_ulong)(); dummy = ctypes.c_ulong(0)
        if X11.XQueryTree(ctypes.c_void_p(dpy), ctypes.c_ulong(win), ctypes.byref(dummy),
                          ctypes.byref(dummy), ctypes.byref(children), ctypes.byref(n)):
            for i in range(n.value):
                walk(children[i], depth + 1)
            if children: X11.XFree(children)
    walk(root)
    return best[0]

def main():
    dur = float(sys.argv[1])
    disp = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("DISPLAY", ":115")
    dpy = X11.XOpenDisplay(disp.encode())
    if not dpy:
        print(json.dumps({"error": "no display"})); return 2
    ev_base = ctypes.c_int(0); err_base = ctypes.c_int(0)
    if not XD.XDamageQueryExtension(ctypes.c_void_p(dpy), ctypes.byref(ev_base), ctypes.byref(err_base)):
        print(json.dumps({"error": "no XDamage extension"})); return 3
    win = find_game_window(dpy)
    if not win:
        print(json.dumps({"error": "game window not found"})); return 4
    dmg = XD.XDamageCreate(ctypes.c_void_p(dpy), ctypes.c_ulong(win), 1)  # DeltaRectangles
    if not dmg:
        print(json.dumps({"error": "XDamageCreate failed"})); return 5
    XD.XDamageSubtract(ctypes.c_void_p(dpy), ctypes.c_ulong(dmg), None, None)  # arm
    X11.XSync(ctypes.c_void_p(dpy), 0)
    buf = ctypes.create_string_buffer(256)
    count = 0; t0 = time.monotonic(); times = []
    while time.monotonic() - t0 < dur:
        while X11.XPending(ctypes.c_void_p(dpy)):
            X11.XNextEvent(ctypes.c_void_p(dpy), buf)
            etype = ctypes.c_int.from_address(ctypes.addressof(buf)).value
            if etype == ev_base.value:  # XDamageNotify
                count += 1; times.append(round(time.monotonic() - t0, 3))
                # re-arm: without Subtract, same-area damage never re-fires
                XD.XDamageSubtract(ctypes.c_void_p(dpy), ctypes.c_ulong(dmg), None, None)
        time.sleep(0.002)
    per_s = [0] * int(dur)
    for t in times:
        if int(t) < len(per_s): per_s[int(t)] += 1
    print(json.dumps({"damage_events": count, "per_s": round(count / dur, 3),
                      "events_per_sec": per_s}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
