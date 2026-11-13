/* probe_wgl8.c - which second-context flavour breaks buffer allocation?
 * For each context variant: make current, print renderer/version,
 * try BufferData(3.6MB) + BufferStorage(16MiB), report err/size. */
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

static void test_ctx(HGLRC ctx, HDC hdc, const char *tag) {
    if (!ctx) { out("%s: CREATE FAILED\n", tag); return; }
    if (!wglMakeCurrent(hdc, ctx)) { out("%s: MAKECURRENT FAILED\n", tag); return; }
    out("%s: renderer=%s version=%s\n", tag,
        (const char *)glGetString(GL_RENDERER), (const char *)glGetString(GL_VERSION));
    GLuint b = 0; GLint sz = -1; GLenum e;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pData(GL_ARRAY_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  %s BufferData: err=%#x size=%d\n", tag, e, sz);
    GLuint b2 = 0; sz = -1;
    pGen(1, &b2); pBind(GL_ARRAY_BUFFER, b2);
    if (pStor) {
        pStor(GL_ARRAY_BUFFER, 16777216, NULL,
              GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT |
              GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT);
        e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
        out("  %s BufferStorage: err=%#x size=%d\n", tag, e, sz);
    } else out("  %s BufferStorage: PROC MISSING\n", tag);
    pBind(GL_ARRAY_BUFFER, 0);
    wglMakeCurrent(NULL, NULL);
}

int main(void) {
    lg = fopen("probe_wgl8.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl8 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe8", WS_OVERLAPPEDWINDOW,
                                0, 0, 640, 480, NULL, NULL, GetModuleHandleA(NULL), NULL);
    ShowWindow(hwnd, SW_SHOW);
    HDC hdc = GetDC(hwnd);
    PIXELFORMATDESCRIPTOR pfd = { sizeof(pfd), 1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        PFD_TYPE_RGBA, 32, 0,0,0,0,0,0, 0,0,0,0,0,0,0, 24, 8, 0,
        PFD_MAIN_PLANE, 0, 0, 0, 0 };
    int fmt = ChoosePixelFormat(hdc, &pfd);
    if (!fmt || !SetPixelFormat(hdc, fmt, &pfd)) { out("PF FAIL\n"); return 1; }
    HGLRC c1 = wglCreateContext(hdc);
    if (!c1) { out("ctx1 FAIL\n"); return 1; }
    wglMakeCurrent(hdc, c1);
    PFN_wglCreateContextAttribsARB pAttribs = getp("wglCreateContextAttribsARB");
    pGen = getp("glGenBuffers"); pBind = getp("glBindBuffer");
    pData = getp("glBufferData"); pStor = getp("glBufferStorage");
    pGetP = getp("glGetBufferParameteriv");
    if (!pAttribs || !pGen || !pData) { out("ABORT\n"); return 1; }
    /* create ALL contexts first, while c1 is current (the working order
     * from probes wgl3-wgl7) */
    const int core_shared[] = { 0x2091, 3, 0x2092, 2, 0x2094, 0x00000002, 0 };
    HGLRC c2 = pAttribs(hdc, c1, core_shared);
    const int core_plain[] = { 0x2091, 3, 0x2092, 2, 0x2094, 0x00000002, 0 };
    HGLRC c3 = pAttribs(hdc, NULL, core_plain);
    HGLRC c4 = wglCreateContext(hdc);
    const int compat_shared[] = { 0x2091, 3, 0x2092, 2, 0x2094, 0x00000001, 0 };
    HGLRC c5 = pAttribs(hdc, c1, compat_shared);
    const int core21_shared[] = { 0x2091, 2, 0x2092, 1, 0x2094, 0x00000002, 0 };
    HGLRC c6 = pAttribs(hdc, c1, core21_shared);
    out("created: c2=%p c3=%p c4=%p c5=%p c6=%p\n",
        (void *)c2, (void *)c3, (void *)c4, (void *)c5, (void *)c6);
    wglMakeCurrent(NULL, NULL);
    test_ctx(c1, hdc, "ctx1-legacy");
    test_ctx(c2, hdc, "ctx2-core33-shared");
    test_ctx(c3, hdc, "ctx3-core33-nonshared");
    test_ctx(c4, hdc, "ctx4-legacy-nonshared");
    test_ctx(c5, hdc, "ctx5-compat32-shared");
    test_ctx(c6, hdc, "ctx6-core21-shared");

    out("DONE\n");
    fclose(lg);
    return 0;
}
