/* probe_wgl2.c - context-sharing test: create + BufferStorage a 64 MiB BO
 * in context 1, then Bind + glMapBufferRange it in context 2 (shared via
 * wglShareLists). In wined3d, BOs are created under one GL context and
 * first mapped under the CS thread's context; if the object is not truly
 * shared, ctx2 sees a size-0 buffer and the map must fail. */
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

static HGLRC mkctx(HDC hdc) {
    PIXELFORMATDESCRIPTOR pfd = { sizeof(pfd), 1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        PFD_TYPE_RGBA, 32, 0,0,0,0,0,0, 0,0,0,0,0,0,0, 24, 8, 0,
        PFD_MAIN_PLANE, 0, 0, 0, 0 };
    int fmt = ChoosePixelFormat(hdc, &pfd);
    if (!fmt || !SetPixelFormat(hdc, fmt, &pfd)) return NULL;
    return wglCreateContext(hdc);
}

int main(void) {
    lg = fopen("probe_wgl2.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl2 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe2", WS_OVERLAPPEDWINDOW,
                                0, 0, 640, 480, NULL, NULL, GetModuleHandleA(NULL), NULL);
    ShowWindow(hwnd, SW_SHOW);
    HDC hdc = GetDC(hwnd);
    HGLRC c1 = mkctx(hdc);
    if (!c1) { out("ctx1 FAIL %lu\n", GetLastError()); return 1; }
    HGLRC c2 = wglCreateContext(hdc);
    if (!c2) { out("ctx2 FAIL %lu\n", GetLastError()); return 1; }
    BOOL shared = wglShareLists(c1, c2);
    out("wglShareLists -> %d (err %lu)\n", shared, GetLastError());

    const GLsizeiptr SIZE = 67108864;
    const GLbitfield STOR = GL_MAP_READ_BIT | GL_MAP_WRITE_BIT |
        GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT;
    const GLbitfield ACC = 0xD3;

    /* ctx1: create the BO */
    wglMakeCurrent(hdc, c1);
    PFN_glGenBuffers pGen = getp("glGenBuffers");
    PFN_glBindBuffer pBind = getp("glBindBuffer");
    PFN_glBufferStorage pStor = getp("glBufferStorage");
    PFN_glMapBufferRange pMapR = getp("glMapBufferRange");
    PFN_glGetBufferParameteriv pGetP = getp("glGetBufferParameteriv");
    PFN_glUnmapBuffer pUnmap = getp("glUnmapBuffer");
    if (!pGen || !pStor || !pMapR) { out("ABORT missing procs\n"); return 1; }
    out("ctx1 renderer: %s\n", (const char *)glGetString(GL_RENDERER));
    GLuint buf = 0;
    pGen(1, &buf);
    pBind(GL_ARRAY_BUFFER, buf);
    pStor(GL_ARRAY_BUFFER, SIZE, NULL, STOR);
    out("ctx1: storage_err=%#x\n", glGetError());
    GLint sz = -1; pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("ctx1: BUFFER_SIZE=%d\n", sz);
    void *p1 = pMapR(GL_ARRAY_BUFFER, 0, SIZE, ACC);
    out("ctx1: map=%p err=%#x -> %s\n", p1, glGetError(), p1 ? "PASS" : "FAIL");
    if (p1) { memset(p1, 0x41, 4096); pUnmap(GL_ARRAY_BUFFER); }
    pBind(GL_ARRAY_BUFFER, 0);
    wglMakeCurrent(NULL, NULL);

    /* ctx2: bind + map the same name */
    wglMakeCurrent(hdc, c2);
    pBind(GL_ARRAY_BUFFER, buf);
    sz = -1; GLenum ge = glGetError(); (void)ge;
    pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("ctx2: BUFFER_SIZE=%d (err %#x)\n", sz, glGetError());
    void *p2 = pMapR(GL_ARRAY_BUFFER, 0, SIZE, ACC);
    out("ctx2: map=%p err=%#x -> %s\n", p2, glGetError(), p2 ? "PASS" : "FAIL(NULL)");
    if (p2) { memset(p2, 0x42, 4096); pUnmap(GL_ARRAY_BUFFER); }
    pBind(GL_ARRAY_BUFFER, 0);
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
