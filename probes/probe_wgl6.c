/* probe_wgl6.c - does glGetBufferPointervARB from ctx2 return the pointer
 * of a buffer that is mapped (and stays mapped) in ctx1? This is the
 * load-bearing assumption of the wined3d map-adoption patch. */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
typedef ptrdiff_t GLintptr;
#define GL_ARRAY_BUFFER 0x8892
#define GL_BUFFER_MAP_POINTER 0x88BD
#define GL_MAP_READ_BIT 0x0001
#define GL_MAP_WRITE_BIT 0x0002
#define GL_MAP_PERSISTENT_BIT 0x0040
#define GL_MAP_COHERENT_BIT 0x0080
#define GL_DYNAMIC_STORAGE_BIT 0x0100

typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferStorage)(GLenum, GLsizeiptr, const void *, GLbitfield);
typedef void *(APIENTRY *PFN_glMapBufferRange)(GLenum, GLintptr, GLsizeiptr, GLbitfield);
typedef void (APIENTRY *PFN_glGetBufferPointervARB)(GLenum, GLenum, void **);
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

int main(void) {
    lg = fopen("probe_wgl6.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl6 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe6", WS_OVERLAPPEDWINDOW,
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
    PFN_glGenBuffers pGen = getp("glGenBuffers");
    PFN_glBindBuffer pBind = getp("glBindBuffer");
    PFN_glBufferStorage pStor = getp("glBufferStorage");
    PFN_glMapBufferRange pMapR = getp("glMapBufferRange");
    PFN_glGetBufferPointervARB pGetPtr = getp("glGetBufferPointervARB");
    if (!pAttribs || !pGen || !pStor || !pMapR || !pGetPtr) { out("ABORT\n"); return 1; }
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
    out("ctx1 map -> %p err=%#x\n", p1, glGetError());
    void *self = NULL;
    pGetPtr(GL_ARRAY_BUFFER, GL_BUFFER_MAP_POINTER, &self);
    out("ctx1 GetBufferPointerv (own map) -> %p err=%#x\n", self, glGetError());
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current FAIL\n"); return 1; }
    pBind(GL_ARRAY_BUFFER, bo);
    void *adopt = NULL;
    pGetPtr(GL_ARRAY_BUFFER, GL_BUFFER_MAP_POINTER, &adopt);
    GLenum e = glGetError();
    out("ctx2 GetBufferPointerv (ctx1 still mapped) -> %p err=%#x\n", adopt, e);
    out("verdict: %s (ctx1 ptr %p)\n",
        adopt ? "ADOPTION RETURNS POINTER" : "ADOPTION RETURNS NULL", p1);
    if (adopt) {
        ((volatile char *)adopt)[12345] = 42;
        out("write through adopted pointer OK\n");
    }
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
