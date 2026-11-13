/* probe_wgl.c - the in-game BO sequence through the PE-side Wine GL stack
 * (opengl32 -> winex11), which the python/EGL probes bypass:
 *   GenBuffers, Bind(PIXEL_UNPACK), BufferData(3686400, NULL, STREAM_DRAW),
 *   MapBufferRange(0, 3686400, 0x22)  -- the exact failing burst --
 * plus a BufferStorage persistent-map variant and legacy glMapBuffer.
 * Logs PASS/FAIL + glGetError per case to probe_wgl.log. */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
typedef ptrdiff_t GLintptr;
#define GL_PIXEL_UNPACK_BUFFER 0x88EC
#define GL_ARRAY_BUFFER 0x8892
#define GL_STREAM_DRAW 0x88E0
#define GL_WRITE_ONLY 0x88B9
#define GL_MAP_READ_BIT 0x0001
#define GL_MAP_WRITE_BIT 0x0002
#define GL_MAP_PERSISTENT_BIT 0x0040
#define GL_DYNAMIC_STORAGE_BIT 0x0100
typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferData)(GLenum, GLsizeiptr, const void *, GLenum);
typedef void *(APIENTRY *PFN_glMapBufferRange)(GLenum, GLintptr, GLsizeiptr, GLbitfield);
typedef void *(APIENTRY *PFN_glMapBuffer)(GLenum, GLenum);
typedef void (APIENTRY *PFN_glBufferStorage)(GLenum, GLsizeiptr, const void *, GLbitfield);
typedef GLboolean (APIENTRY *PFN_glUnmapBuffer)(GLenum);
typedef void (APIENTRY *PFN_glDeleteBuffers)(GLsizei, const GLuint *);

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
    lg = fopen("probe_wgl.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe", WS_OVERLAPPEDWINDOW,
                                0, 0, 640, 480, NULL, NULL, GetModuleHandleA(NULL), NULL);
    if (!hwnd) { out("CreateWindow FAIL %lu\n", GetLastError()); return 1; }
    ShowWindow(hwnd, SW_SHOW);
    HDC hdc = GetDC(hwnd);
    PIXELFORMATDESCRIPTOR pfd = { sizeof(pfd), 1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        PFD_TYPE_RGBA, 32, 0,0,0,0,0,0, 0,0,0,0,0,0,0, 24, 8, 0,
        PFD_MAIN_PLANE, 0, 0, 0, 0 };
    int fmt = ChoosePixelFormat(hdc, &pfd);
    if (!fmt || !SetPixelFormat(hdc, fmt, &pfd)) { out("PixelFormat FAIL fmt=%d err=%lu\n", fmt, GetLastError()); return 1; }
    HGLRC rc = wglCreateContext(hdc);
    if (!rc) { out("wglCreateContext FAIL %lu\n", GetLastError()); return 1; }
    if (!wglMakeCurrent(hdc, rc)) { out("wglMakeCurrent FAIL %lu\n", GetLastError()); return 1; }
    out("renderer: %s\n", (const char *)glGetString(GL_RENDERER));
    out("version: %s\n", (const char *)glGetString(GL_VERSION));
    const char *ext = (const char *)glGetString(GL_EXTENSIONS);
    out("has ARB_buffer_storage: %s\n", ext && strstr(ext, "GL_ARB_buffer_storage") ? "yes" : "no");
    out("has ARB_map_buffer_range: %s\n", ext && strstr(ext, "GL_ARB_map_buffer_range") ? "yes" : "no");

    PFN_glGenBuffers pGen = getp("glGenBuffers");
    PFN_glBindBuffer pBind = getp("glBindBuffer");
    PFN_glBufferData pData = getp("glBufferData");
    PFN_glMapBufferRange pMapR = getp("glMapBufferRange");
    PFN_glMapBuffer pMap = getp("glMapBuffer");
    PFN_glBufferStorage pStor = getp("glBufferStorage");
    PFN_glUnmapBuffer pUnmap = getp("glUnmapBuffer");
    PFN_glDeleteBuffers pDel = getp("glDeleteBuffers");
    if (!pGen || !pBind || !pData || !pMapR) { out("ABORT missing core procs\n"); return 1; }
    glGetError();

    /* case 1: exact in-game burst */
    GLuint buf = 0;
    pGen(1, &buf);
    pBind(GL_PIXEL_UNPACK_BUFFER, buf);
    pData(GL_PIXEL_UNPACK_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    GLenum e1 = glGetError();
    pBind(GL_PIXEL_UNPACK_BUFFER, 0);
    pBind(GL_PIXEL_UNPACK_BUFFER, buf);
    void *p = pMapR(GL_PIXEL_UNPACK_BUFFER, 0, 3686400, 0x22);
    GLenum e2 = glGetError();
    out("case exact-burst: buf=%u bufdata_err=%#x map=%p map_err=%#x -> %s\n",
        buf, e1, p, e2, p ? "PASS" : "FAIL(NULL)");
    if (p) { memset(p, 0x41, 4096); pUnmap(GL_PIXEL_UNPACK_BUFFER); }
    pBind(GL_PIXEL_UNPACK_BUFFER, 0);
    pDel(1, &buf);

    /* case 2: persistent storage map, wined3d staging style */
    if (pStor) {
        GLuint b2 = 0;
        pGen(1, &b2);
        pBind(GL_ARRAY_BUFFER, b2);
        pStor(GL_ARRAY_BUFFER, 67108864, NULL,
              GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT | 0x0080 /*GL_MAP_COHERENT_BIT*/ | GL_DYNAMIC_STORAGE_BIT);
        GLenum e3 = glGetError();
        void *q = pMapR(GL_ARRAY_BUFFER, 0, 67108864, 0xD3);
        GLenum e4 = glGetError();
        out("case persistent-64M: storage_err=%#x map=%p map_err=%#x -> %s\n",
            e3, q, e4, q ? "PASS" : "FAIL(NULL)");
        if (q) { memset(q, 0x41, 4096); pUnmap(GL_ARRAY_BUFFER); }
        pBind(GL_ARRAY_BUFFER, 0);
        pDel(1, &b2);
    }
    /* case 3: legacy glMapBuffer */
    if (pMap) {
        GLuint b3 = 0;
        pGen(1, &b3);
        pBind(GL_PIXEL_UNPACK_BUFFER, b3);
        pData(GL_PIXEL_UNPACK_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
        glGetError();
        void *r = pMap(GL_PIXEL_UNPACK_BUFFER, GL_WRITE_ONLY);
        out("case legacy-map: map=%p err=%#x -> %s\n", r, glGetError(), r ? "PASS" : "FAIL(NULL)");
        if (r) pUnmap(GL_PIXEL_UNPACK_BUFFER);
        pBind(GL_PIXEL_UNPACK_BUFFER, 0);
        pDel(1, &b3);
    }
    out("DONE\n");
    fclose(lg);
    return 0;
}
