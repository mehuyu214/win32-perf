/* probe_wgl12.c - order/path/coexistence bisection inside winex11.
 * WGL_SEQ=A: attribs ctx only -> alloc.
 * WGL_SEQ=B: legacy ctx, destroy, attribs ctx -> alloc.
 * WGL_SEQ=C: attribs ctx1 -> alloc; attribs ctx2 (shared) -> alloc. */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
#define GL_ARRAY_BUFFER 0x8892
#define GL_BUFFER_SIZE 0x8764
#define GL_STREAM_DRAW 0x88E0

typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferData)(GLenum, GLsizeiptr, const void *, GLenum);
typedef void (APIENTRY *PFN_glGetBufferParameteriv)(GLenum, GLenum, GLint *);
typedef HGLRC (WINAPI *PFN_wglCreateContextAttribsARB)(HDC, HGLRC, const int *);

static FILE *lg;
static void out(const char *fmt, ...) {
    char buf[1024]; va_list ap; va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap); va_end(ap);
    fputs(buf, lg); fflush(lg); printf("%s", buf); fflush(stdout);
}
static void *getp(const char *n) { return (void *)wglGetProcAddress(n); }
static PFN_glGenBuffers pGen; static PFN_glBindBuffer pBind;
static PFN_glBufferData pData; static PFN_glGetBufferParameteriv pGetP;
static PFN_wglCreateContextAttribsARB pAttribs;
static HDC hdc;

static void load_procs(void) {
    pAttribs = getp("wglCreateContextAttribsARB");
    pGen = getp("glGenBuffers"); pBind = getp("glBindBuffer");
    pData = getp("glBufferData"); pGetP = getp("glGetBufferParameteriv");
}
static void test_allocs(HGLRC ctx, const char *tag) {
    if (!ctx) { out("  %s: NO CONTEXT\n", tag); return; }
    if (!wglMakeCurrent(hdc, ctx)) { out("  %s: MAKECURRENT FAIL\n", tag); return; }
    GLuint b = 0; GLint sz = -1;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pData(GL_ARRAY_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    GLenum e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  %s BufferData: err=%#x size=%d (renderer %s)\n", tag, e, sz,
        (const char *)glGetString(GL_RENDERER));
    pBind(GL_ARRAY_BUFFER, 0);
    wglMakeCurrent(NULL, NULL);
}

int main(void) {
    lg = fopen("probe_wgl12.log", "w");
    if (!lg) lg = stdout;
    const char *seq = getenv("WGL_SEQ");
    if (!seq) seq = "A";
    out("probe_wgl12 seq=%s\n", seq);
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe12", WS_OVERLAPPEDWINDOW,
                                0, 0, 640, 480, NULL, NULL, GetModuleHandleA(NULL), NULL);
    ShowWindow(hwnd, SW_SHOW);
    hdc = GetDC(hwnd);
    PIXELFORMATDESCRIPTOR pfd = { sizeof(pfd), 1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        PFD_TYPE_RGBA, 32, 0,0,0,0,0,0, 0,0,0,0,0,0,0, 24, 8, 0,
        PFD_MAIN_PLANE, 0, 0, 0, 0 };
    int fmt = ChoosePixelFormat(hdc, &pfd);
    if (!fmt || !SetPixelFormat(hdc, fmt, &pfd)) { out("PF FAIL\n"); return 1; }
    const int attribs[] = { 0x2091, 3, 0x2092, 2, 0 };
    HGLRC tmp = wglCreateContext(hdc);
    if (!tmp) { out("tmp ctx FAIL\n"); return 1; }
    wglMakeCurrent(hdc, tmp);
    load_procs();
    wglMakeCurrent(NULL, NULL);
    wglDeleteContext(tmp);
    if (!pAttribs || !pGen || !pData) { out("ABORT procs\n"); return 1; }

    if (seq[0] == 'A') {
        HGLRC a = pAttribs(hdc, NULL, attribs);
        test_allocs(a, "A-attribs-only");
    } else if (seq[0] == 'B') {
        HGLRC l = wglCreateContext(hdc);
        test_allocs(l, "B-legacy");
        if (l) wglDeleteContext(l);
        HGLRC a = pAttribs(hdc, NULL, attribs);
        test_allocs(a, "B-attribs-after-legacy-destroyed");
    } else {
        HGLRC a1 = pAttribs(hdc, NULL, attribs);
        test_allocs(a1, "C-attribs1");
        HGLRC a2 = pAttribs(hdc, a1, attribs);
        test_allocs(a2, "C-attribs2-shared");
    }
    out("DONE\n");
    fclose(lg);
    return 0;
}
