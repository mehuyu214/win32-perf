#!/usr/bin/env python3
"""X11 frame grabber via ctypes/libX11 (XGetImage).

ffmpeg x11grab hangs in this environment (blocks on an extension
probe against the systemd-lineage X server); libX11 XGetImage works.
Written 2026-11-14 during the :116 recovery.

Usage:
  grab.py shot  <display> <out.png>            one frame -> PNG (via ffmpeg rawvideo filter)
  grab.py stream <display> <fps> <seconds>     raw BGRA frames -> stdout (pipe to ffmpeg)
"""
import ctypes, os, subprocess, sys, time

def open_display(name):
    X = ctypes.CDLL('libX11.so.6')
    X.XOpenDisplay.restype = ctypes.c_void_p
    X.XGetImage.restype = ctypes.c_void_p
    X.XDefaultRootWindow.restype = ctypes.c_ulong
    dpy = X.XOpenDisplay(name.encode())
    if not dpy:
        raise SystemExit(f'cannot open display {name}')
    root = X.XDefaultRootWindow(ctypes.c_void_p(dpy))
    return X, dpy, root

class XImage(ctypes.Structure):
    _fields_ = [('width', ctypes.c_int), ('height', ctypes.c_int), ('xoffset', ctypes.c_int),
                ('format', ctypes.c_int), ('data', ctypes.c_void_p), ('byte_order', ctypes.c_int),
                ('bitmap_unit', ctypes.c_int), ('bitmap_bit_order', ctypes.c_int), ('bitmap_pad', ctypes.c_int),
                ('depth', ctypes.c_int), ('bytes_per_line', ctypes.c_int), ('bits_per_pixel', ctypes.c_int),
                ('red_mask', ctypes.c_ulong), ('green_mask', ctypes.c_ulong), ('blue_mask', ctypes.c_ulong)]

def grab_frame(X, dpy, root, w=1280, h=720):
    img_p = X.XGetImage(ctypes.c_void_p(dpy), ctypes.c_ulong(root), 0, 0, w, h, ctypes.c_ulong(~0), 2)
    if not img_p:
        return None
    img = XImage.from_address(img_p)
    buf = ctypes.string_at(img.data, img.bytes_per_line * img.height)
    X.XDestroyImage(ctypes.c_void_p(img_p))
    return buf

def main():
    mode = sys.argv[1]
    if mode == 'shot':
        disp, out = sys.argv[2], sys.argv[3]
        X, dpy, root = open_display(disp)
        buf = grab_frame(X, dpy, root)
        if buf is None:
            raise SystemExit('XGetImage failed')
        p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                            '-video_size', '1280x720', '-i', '-', '-frames:v', '1', '-y', out],
                           input=buf)
        raise SystemExit(p.returncode)
    if mode == 'stream':
        disp, fps, secs = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        X, dpy, root = open_display(disp)
        out = os.fdopen(sys.stdout.fileno(), 'wb', buffering=0)
        period = 1.0 / fps
        t0 = time.monotonic()
        n = int(fps * secs)
        dropped = 0
        for i in range(n):
            target = t0 + i * period
            buf = grab_frame(X, dpy, root)
            if buf is None:
                buf = bytes(1280 * 720 * 4)
                dropped += 1
            out.write(buf)
            delay = target + period - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            elif delay < -period:
                dropped += 1
        print(f'grab-stream done frames={n} dropped={dropped}', file=sys.stderr)
        return
    raise SystemExit('unknown mode')

if __name__ == '__main__':
    main()
