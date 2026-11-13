/* probe_wgl5.c - clean already-mapped discrimination, one 16 MiB BO:
 *   verify storage (BUFFER_SIZE) -> ctx1 map -> ctx1 UNMAP -> ctx2 map.
 *   plus case0 repeat: fresh BO, ctx1 map (stays) -> ctx2 map.
 * Run under softpipe and llvmpipe; compare. */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
typedef ptrdiff_t GLintptr;
#define GL_ARRAY_BUFFER 0x8892
#define GL_BUFFER_SIZE 0x8764
#define GL_MAP_READ_BIT 0x0001
#define GL_MAP_WRITE_BIT 0x0002
#define GL_MAP_PERSISTENT_BIT 0x0040
#define GL_MAP_COHERENT_BIT 0x0080
#define GL_DYNAMIC_STORAGE_BIT 0x0100

typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferStorage)(GLenum, GLsizeiptr, const void *, GLbitfield);
typedef void *(APIENTRY *PFN_glMapBufferRange)(GLenum, GLintptr, GLsizeiptr, GLbitfield);
typedef void (APIENTRY *PFN_glGetBufferParameteriv)(GLenum, GLenum, GLint *);
typedef GLboolean (APIENTRY *PFN_glUnmapBuffer)(GLenum);
typedef void (APIENTRY *PFN_glDeleteBuffers)(GLsizei, const GLuint *);
typedef HGLRC (WINAPI *PFN_wglCreateContextAttribsARB)(HDC, HGLRC, const int *);

static FILE *lg;
static void out(const char *fmt, ...) {
    char buf[1024]; va_list ap; va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap); va_end(ap);
    fputs(buf, lg); fflush(lg); printf("%s", buf); fflush(stdout);
}
static void *getp(const char *n) {
    void *p = (void *)wglGetProcAddress(n);
    if (!p) out("MISSING PROC %s\n", n);
    return p;
}

static PFN_glGenBuffers pGen; static PFN_glBindBuffer pBind;
static PFN_glBufferStorage pStor; static PFN_glMapBufferRange pMapR;
static PFN_glGetBufferParameteriv pGetP; static PFN_glUnmapBuffer pUnmap;
static PFN_glDeleteBuffers pDel;
static const GLsizeiptr BSIZE = 16777216;
static const GLbitfield STOR = GL_MAP_READ_BIT | GL_MAP_WRITE_BIT |
    GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT;

static GLuint make_bo(void) {
    GLuint b = 0;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pStor(GL_ARRAY_BUFFER, BSIZE, NULL, STOR);
    GLenum e = glGetError();
    GLint sz = -1; pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  make_bo %u: storage_err=%#x BUFFER_SIZE=%d\n", b, e, sz);
    pBind(GL_ARRAY_BUFFER, 0);
    return b;
}
static void *map_in(GLuint b, const char *tag) {
    pBind(GL_ARRAY_BUFFER, b);
    void *p = pMapR(GL_ARRAY_BUFFER, 0, BSIZE, 0xD3);
    GLenum e = glGetError();
    pBind(GL_ARRAY_BUFFER, 0);
    out("  %s: map -> %p err=%#x\n", tag, p, e);
    return p;
}
static void unmap(GLuint b) {
    pBind(GL_ARRAY_BUFFER, b); pUnmap(GL_ARRAY_BUFFER); pBind(GL_ARRAY_BUFFER, 0);
}

int main(void) {
    lg = fopen("probe_wgl5.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl5 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe5", WS_OVERLAPPEDWINDOW,
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
    pStor = getp("glBufferStorage"); pMapR = getp("glMapBufferRange");
    pGetP = getp("glGetBufferParameteriv"); pUnmap = getp("glUnmapBuffer");
    pDel = getp("glDeleteBuffers");
    if (!pAttribs || !pGen || !pStor || !pMapR) { out("ABORT\n"); return 1; }
    out("renderer: %s\n", (const char *)glGetString(GL_RENDERER));
    const int attribs[] = { 0x2091, 3, 0x2092, 2, 0x2094, 0x00000002, 0 };
    HGLRC c2 = pAttribs(hdc, c1, attribs);
    if (!c2) { out("ctx2 FAIL\n"); return 1; }

    /* caseA: map in ctx1, unmap, then map in ctx2 */
    GLuint boA = make_bo();
    void *pa = map_in(boA, "caseA ctx1 map");
    if (pa) unmap(boA);
    /* case0: fresh BO mapped in ctx1, stays mapped */
    GLuint bo0 = make_bo();
    void *p0 = map_in(bo0, "case0 ctx1 map (stays)");
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current FAIL\n"); return 1; }
    void *qa = map_in(boA, "caseA ctx2 map (after ctx1 unmap)");
    out("caseA verdict: %s\n", qa ? "SUCCEEDED" : "FAILED");
    void *q0 = map_in(bo0, "case0 ctx2 map (still mapped in ctx1)");
    out("case0 verdict: %s\n", q0 ? "SUCCEEDED" : "FAILED");
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
