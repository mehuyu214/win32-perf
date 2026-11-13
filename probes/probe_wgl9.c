/* probe_wgl9.c - sole second context, COMPATIBILITY profile, shared:
 * do allocations work there? (Decides the wined3d profile patch.) */
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

int main(void) {
    lg = fopen("probe_wgl9.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl9 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe9", WS_OVERLAPPEDWINDOW,
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
    PFN_glGetBufferParameteriv pGetP = getp("glGetBufferParameteriv");
    if (!pAttribs || !pGen || !pData) { out("ABORT\n"); return 1; }
    const char *prof = getenv("WGL_PROFILE");
    int maskval = (prof && strcmp(prof, "core") == 0) ? 0x00000001 : 0x00000002;
    const int compat_shared[] = { 0x2091, 3, 0x2092, 2, 0x9126, maskval, 0 };
    HGLRC c2 = pAttribs(hdc, c1, compat_shared);
    out("ctx2 profile-mask=%#x (%s) created: %p\n", maskval,
        maskval == 1 ? "CORE" : "COMPAT", (void *)c2);
    if (!c2) { out("DONE\n"); return 0; }
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current FAIL\n"); return 1; }
    out("ctx2: renderer=%s version=%s\n",
        (const char *)glGetString(GL_RENDERER), (const char *)glGetString(GL_VERSION));
    GLuint b = 0; GLint sz = -1; GLenum e;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pData(GL_ARRAY_BUFFER, 3686400, NULL, GL_STREAM_DRAW);
    e = glGetError(); sz = -1; pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("ctx2 BufferData: err=%#x size=%d\n", e, sz);
    GLuint b2 = 0; sz = -1;
    pGen(1, &b2); pBind(GL_ARRAY_BUFFER, b2);
    pStor(GL_ARRAY_BUFFER, 16777216, NULL,
          GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT |
          GL_MAP_COHERENT_BIT | GL_DYNAMIC_STORAGE_BIT);
    e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &sz);
    out("ctx2 BufferStorage: err=%#x size=%d\n", e, sz);
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
