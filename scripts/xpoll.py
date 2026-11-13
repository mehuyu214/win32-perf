#!/usr/bin/env python3
"""Poll a game window's pixels from the host X server at ~20 Hz.

For each poll, grabs two window-relative rects (text box, centre) via
XGetImage, subsamples 4x, and records: md5, mean-abs-diff vs previous
poll per rect. This measures the TRUE window-content update rate on the
X front buffer, independent of any in-guest claim.
Usage: xpoll.py DURATION_SEC OUT.csv [DISPLAY]
Prints a JSON summary line at the end.
"""
import ctypes, hashlib, json, os, sys, time
import numpy as np

X11 = ctypes.CDLL("libX11.so.6")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XGetImage.restype = ctypes.c_void_p
X11.XFetchName.restype = ctypes.c_int

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
    best = None
    def walk(win, depth=0):
        nonlocal best
        attr = XWindowAttributes()
        if not X11.XGetWindowAttributes(ctypes.c_void_p(dpy), ctypes.c_ulong(win), ctypes.byref(attr)):
            return
        if attr.map_state == 2 and attr.width >= 1000 and attr.height >= 600:
            best = (win, attr.width, attr.height)
        if depth > 6:
            return
        n = ctypes.c_uint(0)
        children = ctypes.POINTER(ctypes.c_ulong)()
        dummy = ctypes.c_ulong(0)
        if X11.XQueryTree(ctypes.c_void_p(dpy), ctypes.c_ulong(win), ctypes.byref(dummy),
                          ctypes.byref(dummy), ctypes.byref(children), ctypes.byref(n)):
            for i in range(n.value):
                walk(children[i], depth + 1)
            if children:
                X11.XFree(children)
    walk(root)
    return best

class XImage(ctypes.Structure):
    _fields_ = [("width", ctypes.c_int), ("height", ctypes.c_int),
                ("xoffset", ctypes.c_int), ("format", ctypes.c_int),
                ("data", ctypes.c_void_p), ("byte_order", ctypes.c_int),
                ("bitmap_unit", ctypes.c_int), ("bitmap_bit_order", ctypes.c_int),
                ("bitmap_pad", ctypes.c_int), ("depth", ctypes.c_int),
                ("bytes_per_line", ctypes.c_int), ("bits_per_pixel", ctypes.c_int),
                ("red_mask", ctypes.c_ulong), ("green_mask", ctypes.c_ulong),
                ("blue_mask", ctypes.c_ulong), ("obdata", ctypes.c_void_p)]

err_count = [0]
def err_handler(dpy, ev):
    err_count[0] += 1
    return 0
ERRCB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)

def grab(dpy, win, x, y, w, h):
    imgp = X11.XGetImage(ctypes.c_void_p(dpy), ctypes.c_ulong(win), x, y, w, h,
                         ctypes.c_ulong(0xFFFFFFFF), 2)  # AllPlanes, ZPixmap
    if not imgp:
        return None
    img = XImage.from_address(imgp)
    n = img.bytes_per_line * img.height
    buf = ctypes.string_at(img.data, n)
    arr = np.frombuffer(buf, dtype=np.uint8).reshape(img.height, img.bytes_per_line)
    arr = arr[:, :w * 4].reshape(h, w, 4)
    sub = arr[::4, ::4, :3].astype(np.int16)
    X11.XDestroyImage(ctypes.c_void_p(imgp))
    return sub

RECTS = [(60, 520, 1160, 190), (400, 80, 480, 320)]  # text box, centre

def main():
    dur = float(sys.argv[1]); outp = sys.argv[2]
    disp = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("DISPLAY", ":115")
    dpy = X11.XOpenDisplay(disp.encode())
    if not dpy:
        print(json.dumps({"error": f"cannot open display {disp}"})); return 2
    X11.XSetErrorHandler(ERRCB(err_handler))
    found = find_game_window(dpy)
    if not found:
        print(json.dumps({"error": "game window not found"})); return 3
    win, W, H = found
    rows = []
    prev = None
    t0 = time.monotonic(); t_end = t0 + dur; k = 0
    with open(outp, "w") as f:
        f.write("t,diff_text,diff_centre,hashchg\n")
        while True:
            now = time.monotonic()
            if now > t_end:
                break
            subs = [grab(dpy, win, *r) for r in RECTS]
            if any(s is None for s in subs):
                f.write(f"{now-t0:.3f},-1,-1,-1\n"); f.flush()
            else:
                h = hashlib.md5(b"".join(s.tobytes() for s in subs)).hexdigest()
                if prev is None:
                    d = [0.0, 0.0]; chg = 0
                else:
                    d = [float(np.abs(s - p).mean()) for s, p in zip(subs, prev[0])]
                    chg = 1 if h != prev[1] else 0
                prev = (subs, h)
                f.write(f"{now-t0:.3f},{d[0]:.4f},{d[1]:.4f},{chg}\n"); f.flush()
            k += 1
            target = t0 + k * 0.05
            dt = target - time.monotonic()
            if dt > 0:
                time.sleep(dt)
    # summary
    ts, dm = [], []
    with open(outp) as f:
        next(f)
        for line in f:
            p = line.strip().split(",")
            if len(p) == 4 and float(p[1]) >= 0:
                ts.append(float(p[0])); dm.append(max(float(p[1]), float(p[2])))
    n = len(dm)
    res = {"polls": n, "poll_hz": round(n / dur, 2), "xerrors": err_count[0]}
    for th in (0.05, 0.2, 1.0, 5.0):
        c = sum(1 for v in dm if v >= th)
        res[f"chg_per_s_ge_{th}"] = round(c / dur, 3)
    longest = cur = 0.0
    prev_t = 0.0
    for t, v in zip(ts, dm):
        if v < 0.2:
            cur = t - prev_t if cur == 0 else cur
            longest = max(longest, t - (prev_t if False else 0)) if False else longest
        else:
            prev_t = t
    # simpler longest-below-threshold stretch
    longest = 0.0; stretch_start = None; last_t = 0.0
    for t, v in zip(ts, dm):
        last_t = t
        if v < 0.2:
            if stretch_start is None: stretch_start = t
            longest = max(longest, t - stretch_start)
        else:
            stretch_start = None
    res["longest_stretch_below_0.2_s"] = round(longest, 2)
    print(json.dumps(res))
    return 0

if __name__ == "__main__":
    sys.exit(main())
