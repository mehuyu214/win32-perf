/* probe_wgl7.c - does ctx1's live persistent mapping poison NEW buffer
 * allocations (BufferData / BufferStorage) in the shared ctx2?
 * A: ctx1 16MiB storage + persistent map (stays) -> ctx2 allocations.
 * B: ctx1 unmaps -> ctx2 allocations again. */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
typedef ptrdiff_t GLintptr;
#define GL_ARRAY_BUFFER 0x8892
#define GL_PIXEL_UNPACK_BUFFER 0x88EC
#define GL_STREAM_DRAW 0x88E0
#define GL_BUFFER_SIZE 0x8764
#define GL_MAP_READ_BIT 0x0001
#define GL_MAP_WRITE_BIT 0x0002
#define GL_MAP_PERSISTENT_BIT 0x0040
#define GL_MAP_COHERENT_BIT 0x0080
#define GL_DYNAMIC_STORAGE_BIT 0x0100

typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferData)(GLenum, GLsizeiptr, const void *, GLenum);
typedef void (APIENTRY *PFN_glBufferStorage)(GLenum, GLsizeiptr, const void *, GLbitfield);
typedef void *(APIENTRY *PFN_glMapBufferRange)(GLenum, GLintptr, GLsizeiptr, GLbitfield);
typedef void (APIENTRY *PFN_glGetBufferParameteriv)(GLenum, GLenum, GLint *);
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
static PFN_glBufferData pData; static PFN_glBufferStorage pStor;
static PFN_glMapBufferRange pMapR; static PFN_glGetBufferParameteriv pGetP;
static PFN_glUnmapBuffer pUnmap;

static void try_allocs(const char *tag) {
    GLuint b = 0; GLint sz = -1; GLenum e;
    pGen(1, &b); pBind(GL_PIXEL_UNPACK_BUFFER, b);
    pData(GL_PIXEL_UNPACK_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    e = glGetError(); pGetP(GL_PIXEL_UNPACK_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  %s ctx2 BufferData(3686400): err=%#x size=%d\n", tag, e, sz);
    pBind(GL_PIXEL_UNPACK_BUFFER, 0);
    GLuint b2 = 0; sz = -1;
    pGen(1, &b2); pBind(GL_ARRAY_BUFFER, b2);
    pStor(GL_ARRAY_BUFFER, 16777216, NULL,
          GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT |
          GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT);
    e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("  %s ctx2 BufferStorage(16MiB): err=%#x size=%d\n", tag, e, sz);
    pBind(GL_ARRAY_BUFFER, 0);
}

int main(void) {
    lg = fopen("probe_wgl7.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl7 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe7", WS_OVERLAPPEDWINDOW,
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
    pMapR = getp("glMapBufferRange"); pGetP = getp("glGetBufferParameteriv");
    pUnmap = getp("glUnmapBuffer");
    if (!pAttribs || !pGen || !pData || !pStor || !pMapR) { out("ABORT\n"); return 1; }
    out("renderer: %s\n", (const char *)glGetString(GL_RENDERER));
    const int attribs[] = { 0x2091, 3, 0x2092, 2, 0x2094, 0x00000002, 0 };
    HGLRC c2 = pAttribs(hdc, c1, attribs);
    if (!c2) { out("ctx2 FAIL\n"); return 1; }

    GLuint bo = 0;
    pGen(1, &bo); pBind(GL_ARRAY_BUFFER, bo);
    pStor(GL_ARRAY_BUFFER, 16777216, NULL,
          GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT |
          GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT);
    void *p1 = pMapR(GL_ARRAY_BUFFER, 0, 16777216, 0xD3);
    out("ctx1: storage+map -> %p err=%#x\n", p1, glGetError());
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current FAIL\n"); return 1; }
    try_allocs("A(mapped)");
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c1)) { out("ctx1 rec FAIL\n"); return 1; }
    pBind(GL_ARRAY_BUFFER, bo); pUnmap(GL_ARRAY_BUFFER); pBind(GL_ARRAY_BUFFER, 0);
    out("ctx1: unmapped\n");
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current2 FAIL\n"); return 1; }
    try_allocs("B(unmapped)");
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
