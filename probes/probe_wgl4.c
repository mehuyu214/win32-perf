/* probe_wgl4.c - KK's already-mapped hypothesis, discriminated.
 * Topology as in probe_wgl3 (ctx2 = core profile, shared at creation).
 *   case0: ctx1 maps BO, STAYS mapped -> ctx2 maps (baseline; wgl3 repeat)
 *   caseB: ctx1 maps BO, maps AGAIN in ctx1 (control; spec says 0x502)
 *   caseA: ctx1 maps BO, UNMAPS -> ctx2 maps (prediction: succeeds iff
 *          already-mapped state was the blocker)
 * Each case uses its own 64 MiB BufferStorage BO created in ctx1. */
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
typedef GLboolean (APIENTRY *PFN_glUnmapBuffer)(GLenum);
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
static PFN_glUnmapBuffer pUnmap;
static const GLsizeiptr BSIZE = 67108864;
static const GLbitfield STOR = GL_MAP_READ_BIT | GL_MAP_WRITE_BIT |
    GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT;

static GLuint make_bo(void) {
    GLuint b = 0;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pStor(GL_ARRAY_BUFFER, BSIZE, NULL, STOR);
    if (glGetError()) { out("  make_bo storage err\n"); }
    pBind(GL_ARRAY_BUFFER, 0);
    return b;
}
static void *map_in(GLuint b) {
    pBind(GL_ARRAY_BUFFER, b);
    void *p = pMapR(GL_ARRAY_BUFFER, 0, BSIZE, 0xD3);
    GLenum e = glGetError();
    pBind(GL_ARRAY_BUFFER, 0);
    out("    map -> %p err=%#x\n", p, e);
    return p;
}
static void unmap(GLuint b) {
    pBind(GL_ARRAY_BUFFER, b);
    pUnmap(GL_ARRAY_BUFFER);
    pBind(GL_ARRAY_BUFFER, 0);
}

int main(void) {
    lg = fopen("probe_wgl4.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl4 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe4", WS_OVERLAPPEDWINDOW,
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
    pUnmap = getp("glUnmapBuffer");
    if (!pAttribs || !pGen || !pStor || !pMapR || !pUnmap) { out("ABORT\n"); return 1; }
    out("renderer: %s\n", (const char *)glGetString(GL_RENDERER));
    const int attribs[] = { 0x2091, 3, 0x2092, 2, 0x2094, 0x00000002, 0 };
    HGLRC c2 = pAttribs(hdc, c1, attribs);
    if (!c2) { out("ctx2 FAIL\n"); return 1; }

    GLuint bo0 = make_bo(), boB = make_bo(), boA = make_bo();
    /* caseB (control): map boB, then map it again in the same context */
    out("caseB same-context double map:\n");
    void *pb1 = map_in(boB);
    void *pb2 = map_in(boB);
    out("  caseB: first=%p second=%p -> %s\n", pb1, pb2,
        pb2 ? "second SUCCEEDED" : "second FAILED (0x502 class)");
    /* case0: map bo0 in ctx1, keep mapped; caseA: map boA in ctx1, unmap */
    out("setup: map bo0 (stays), map+unmap boA, in ctx1:\n");
    void *p0 = map_in(bo0);
    void *pa = map_in(boA);
    if (pa) unmap(boA);
    wglMakeCurrent(NULL, NULL);
    /* ctx2 attempts */
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current FAIL\n"); return 1; }
    out("case0 ctx2 maps bo0 (still mapped in ctx1):\n");
    void *q0 = map_in(bo0);
    out("  case0 -> %s\n", q0 ? "SUCCEEDED" : "FAILED");
    out("caseA ctx2 maps boA (unmapped in ctx1):\n");
    void *qa = map_in(boA);
    out("  caseA -> %s\n", qa ? "SUCCEEDED" : "FAILED");
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
