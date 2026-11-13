/* probe_wgl10.c - what makes a second context able to allocate?
 * Modes (env WGL_MODE):
 *  A: ctx2 = legacy wglCreateContext, same HDC, no share.
 *  B: ctx2 = attribs (wined3d-style: version only), SECOND window HDC,
 *     shared with ctx1.
 *  C: ctx2 = attribs (wined3d-style), same HDC, shared with ctx1. */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
#define GL_ARRAY_BUFFER 0x8892
#define GL_BUFFER_SIZE 0x8764
#define GL_STREAM_DRAW 0x88E0
#define GL_MAP_READ_BIT 0x0001
#define GL_MAP_WRITE_BIT 0x0002
#define GL_MAP_PERSISTENT_BIT 0x0040
#define GL_MAP_COHERENT_BIT 0x0080
#define GL_DYNAMIC_STORAGE_BIT 0x0100

typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferData)(GLenum, GLsizeiptr, const void *, GLenum);
typedef void (APIENTRY *PFN_glBufferStorage)(GLenum, GLsizeiptr, const void *, GLbitfield);
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
static PFN_glBufferData pData; static PFN_glBufferStorage pStor;
static PFN_glGetBufferParameteriv pGetP;

static HDC make_dc(HWND *out_hwnd) {
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe10", WS_OVERLAPPEDWINDOW,
                                0, 0, 640, 480, NULL, NULL, GetModuleHandleA(NULL), NULL);
    ShowWindow(hwnd, SW_SHOW);
    HDC hdc = GetDC(hwnd);
    PIXELFORMATDESCRIPTOR pfd = { sizeof(pfd), 1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        PFD_TYPE_RGBA, 32, 0,0,0,0,0,0, 0,0,0,0,0,0,0, 24, 8, 0,
        PFD_MAIN_PLANE, 0, 0, 0, 0 };
    int fmt = ChoosePixelFormat(hdc, &pfd);
    if (!fmt || !SetPixelFormat(hdc, fmt, &pfd)) { out("PF FAIL\n"); return NULL; }
    *out_hwnd = hwnd;
    return hdc;
}

static void test_allocs(const char *tag) {
    GLuint b = 0; GLint sz = -1; GLenum e;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pData(GL_ARRAY_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  %s BufferData: err=%#x size=%d\n", tag, e, sz);
    GLuint b2 = 0; sz = -1;
    pGen(1, &b2); pBind(GL_ARRAY_BUFFER, b2);
    pStor(GL_ARRAY_BUFFER, 16777216, NULL,
          GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT |
          GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT);
    e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  %s BufferStorage: err=%#x size=%d\n", tag, e, sz);
    pBind(GL_ARRAY_BUFFER, 0);
}

int main(void) {
    lg = fopen("probe_wgl10.log", "w");
    if (!lg) lg = stdout;
    const char *mode = getenv("WGL_MODE");
    if (!mode) mode = "C";
    out("probe_wgl10 mode=%s\n", mode);
    HWND hw1, hw2;
    HDC hdc1 = make_dc(&hw1);
    if (!hdc1) return 1;
    HGLRC c1 = wglCreateContext(hdc1);
    if (!c1) { out("ctx1 FAIL\n"); return 1; }
    wglMakeCurrent(hdc1, c1);
    PFN_wglCreateContextAttribsARB pAttribs = getp("wglCreateContextAttribsARB");
    pGen = getp("glGenBuffers"); pBind = getp("glBindBuffer");
    pData = getp("glBufferData"); pStor = getp("glBufferStorage");
    pGetP = getp("glGetBufferParameteriv");
    if (!pGen || !pData || !pStor) { out("ABORT procs\n"); return 1; }

    HGLRC c2 = NULL; HDC hdc2 = hdc1;
    const int wined3d_attribs[] = { 0x2091, 3, 0x2092, 2, 0 };
    if (mode[0] == 'A') {
        c2 = wglCreateContext(hdc1);
    } else if (mode[0] == 'B') {
        hdc2 = make_dc(&hw2);
        c2 = pAttribs(hdc2, c1, wined3d_attribs);
    } else {
        c2 = pAttribs(hdc1, c1, wined3d_attribs);
    }
    out("ctx2 created: %p (mode %s)\n", (void *)c2, mode);
    if (!c2) { out("DONE\n"); return 0; }
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc2, c2)) { out("ctx2 current FAIL\n"); return 1; }
    out("ctx2: renderer=%s version=%s\n",
        (const char *)glGetString(GL_RENDERER), (const char *)glGetString(GL_VERSION));
    test_allocs("ctx2");
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
