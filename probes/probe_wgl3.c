/* probe_wgl3.c - wined3d's actual context topology: ctx2 is created
 * ALREADY SHARED via wglCreateContextAttribsARB(share=c1) (no legacy
 * wglShareLists recreation). Create a BufferStorage BO in ctx1, then map
 * it in ctx2 (the CS-thread role) and in ctx1. Ladder for BufferData too. */
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

int main(void) {
    lg = fopen("probe_wgl3.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl3 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe3", WS_OVERLAPPEDWINDOW,
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
    PFN_glBufferData pData = getp("glBufferData");
    PFN_glBufferStorage pStor = getp("glBufferStorage");
    PFN_glMapBufferRange pMapR = getp("glMapBufferRange");
    PFN_glGetBufferParameteriv pGetP = getp("glGetBufferParameteriv");
    PFN_glUnmapBuffer pUnmap = getp("glUnmapBuffer");
    if (!pAttribs || !pGen || !pStor || !pMapR) { out("ABORT\n"); return 1; }

    /* ctx2: core 3.2, shared with c1 at creation (wined3d style) */
    const int attribs[] = { 0x2091, 3, 0x2092, 2,
                            0x2094, 0x00000002 /*CORE_PROFILE*/, 0 };
    HGLRC c2 = pAttribs(hdc, c1, attribs);
    out("ctx2 (attribs+share) = %p err %lu\n", (void *)c2, GetLastError());
    if (!c2) { out("ABORT ctx2\n"); return 1; }

    const GLsizeiptr SIZE = 67108864;
    const GLbitfield STOR = GL_MAP_READ_BIT | GL_MAP_WRITE_BIT |
        GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT;

    /* still on ctx1: create the chunk-style BO */
    GLuint buf = 0;
    pGen(1, &buf); pBind(GL_ARRAY_BUFFER, buf);
    pStor(GL_ARRAY_BUFFER, SIZE, NULL, STOR);
    GLint sz = -1; pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("ctx1: storage_err=%#x BUFFER_SIZE=%d\n", glGetError(), sz);
    void *p1 = pMapR(GL_ARRAY_BUFFER, 0, SIZE, 0xD3);
    out("ctx1: map=%p err=%#x -> %s\n", p1, glGetError(), p1 ? "PASS" : "FAIL");
    if (p1) { memset(p1, 0x41, 4096); /* stay mapped, persistent-style */ }
    pBind(GL_ARRAY_BUFFER, 0);
    wglMakeCurrent(NULL, NULL);

    /* ctx2 (CS role): bind + inspect + map the same BO */
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 MakeCurrent FAIL %lu\n", GetLastError()); return 1; }
    out("ctx2 renderer: %s\n", (const char *)glGetString(GL_RENDERER));
    out("ctx2 version: %s\n", (const char *)glGetString(GL_VERSION));
    pBind(GL_ARRAY_BUFFER, buf);
    sz = -1; pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("ctx2: BUFFER_SIZE=%d err=%#x\n", sz, glGetError());
    void *p2 = pMapR(GL_ARRAY_BUFFER, 0, SIZE, 0xD3);
    out("ctx2: map=%p err=%#x -> %s\n", p2, glGetError(), p2 ? "PASS" : "FAIL(NULL)");
    if (p2) { memset(p2, 0x42, 4096); pUnmap(GL_ARRAY_BUFFER); }
    pBind(GL_ARRAY_BUFFER, 0);

    /* ctx2: transient PBO burst (masked-config style) */
    GLuint pb = 0;
    pGen(1, &pb); pBind(GL_PIXEL_UNPACK_BUFFER, pb);
    pData(GL_PIXEL_UNPACK_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    GLenum de = glGetError();
    sz = -1; pGetP(GL_PIXEL_UNPACK_BUFFER, GL_BUFFER_SIZE, &sz);
    void *p3 = pMapR(GL_PIXEL_UNPACK_BUFFER, 0, 3686400, 0x22);
    out("ctx2 PBO: bufdata_err=%#x BUFFER_SIZE=%d map=%p err=%#x -> %s\n",
        de, sz, p3, glGetError(), p3 ? "PASS" : "FAIL(NULL)");
    if (p3) pUnmap(GL_PIXEL_UNPACK_BUFFER);
    pBind(GL_PIXEL_UNPACK_BUFFER, 0);
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
