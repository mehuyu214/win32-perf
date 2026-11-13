/* click.c - host X11 clicker: find largest mapped window on the display,
 * send synthetic ButtonPress/Release at window-relative (x, y). */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <X11/Xlib.h>

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: click X Y [display]\n"); return 2; }
    int cx = atoi(argv[1]), cy = atoi(argv[2]);
    const char *dname = argc > 3 ? argv[3] : ":115";
    Display *dpy = XOpenDisplay(dname);
    if (!dpy) { fprintf(stderr, "FAIL XOpenDisplay %s\n", dname); return 1; }
    Window root = DefaultRootWindow(dpy);
    Window rret, pret, *children = NULL;
    unsigned int n = 0;
    XQueryTree(dpy, root, &rret, &pret, &children, &n);
    Window best = 0; unsigned long bestarea = 0; int bx = 0, by = 0;
    for (unsigned int i = 0; i < n; i++) {
        XWindowAttributes a;
        if (XGetWindowAttributes(dpy, children[i], &a) && a.map_state == IsViewable) {
            unsigned long area = (unsigned long)a.width * a.height;
            if (area > bestarea) { bestarea = area; best = children[i]; bx = a.x; by = a.y; }
        }
    }
    if (children) XFree(children);
    if (!best) { fprintf(stderr, "FAIL no window\n"); return 1; }
    printf("window %#lx at %d,%d; click %d,%d\n", best, bx, by, cx, cy);
    for (int t = 0; t < 2; t++) {
        XEvent ev = {0};
        ev.xbutton.type = t == 0 ? ButtonPress : ButtonRelease;
        ev.xbutton.display = dpy;
        ev.xbutton.window = best;
        ev.xbutton.root = root;
        ev.xbutton.subwindow = None;
        ev.xbutton.time = CurrentTime;
        ev.xbutton.x = cx; ev.xbutton.y = cy;
        ev.xbutton.x_root = bx + cx; ev.xbutton.y_root = by + cy;
        ev.xbutton.state = t == 0 ? 0 : Button1Mask;
        ev.xbutton.button = Button1;
        ev.xbutton.same_screen = True;
        XSendEvent(dpy, best, False,
                   t == 0 ? ButtonPressMask : ButtonReleaseMask, &ev);
        XFlush(dpy);
        usleep(120000);
    }
    printf("clicked\n");
    XCloseDisplay(dpy);
    return 0;
}
