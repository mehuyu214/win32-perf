/* probe_wgl11.c - granularity of the ctx2 failure: which GL object
 * creations fail in the second context, and at what sizes? Does ctx1
 * stay healthy after ctx2 exists? Does ctx2 render? */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <GL/gl.h>

typedef ptrdiff_t GLsizeiptr;
#define GL_ARRAY_BUFFER 0x8892
#define GL_BUFFER_SIZE 0x8764
#define GL_STREAM_DRAW 0x88E0
#define GL_TEXTURE_2D 0x0DE1
#define GL_RGBA 0x1908
#define GL_UNSIGNED_BYTE 0x1401
#define GL_FRAGMENT_SHADER 0x8B30
#define GL_COMPILE_STATUS 0x8B81

typedef void (APIENTRY *PFN_glGenBuffers)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindBuffer)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glBufferData)(GLenum, GLsizeiptr, const void *, GLenum);
typedef void (APIENTRY *PFN_glGetBufferParameteriv)(GLenum, GLenum, GLint *);
typedef void (APIENTRY *PFN_glGenTextures)(GLsizei, GLuint *);
typedef void (APIENTRY *PFN_glBindTexture)(GLenum, GLuint);
typedef void (APIENTRY *PFN_glTexImage2D)(GLenum, GLint, GLint, GLsizei, GLsizei, GLint, GLenum, GLenum, const void *);
typedef GLuint (APIENTRY *PFN_glCreateShader)(GLenum);
typedef void (APIENTRY *PFN_glShaderSource)(GLuint, GLsizei, const char **, const GLint *);
typedef void (APIENTRY *PFN_glCompileShader)(GLuint);
typedef void (APIENTRY *PFN_glGetShaderiv)(GLuint, GLenum, GLint *);
typedef HGLRC (WINAPI *PFN_wglCreateContextAttribsARB)(HDC, HGLRC, const int *);

static FILE *lg;
static void out(const char *fmt, ...) {
    char buf[1024]; va_list ap; va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap); va_end(ap);
    fputs(buf, lg); fflush(lg); printf("%s", buf); fflush(stdout);
}
static void *getp(const char *n) { return (void *)wglGetProcAddress(n); }
static PFN_glGenBuffers pGen; static PFN_glBindBuffer pBind;
static PFN_glBufferData pData; static PFN_glGetBufferParameteriv pGetP;
static PFN_glGenTextures pGenT; static PFN_glBindTexture pBindT;
static PFN_glTexImage2D pTex;
static PFN_glCreateShader pCS; static PFN_glShaderSource pSS;
static PFN_glCompileShader pComp; static PFN_glGetShaderiv pGS;

static void buf_test(const char *tag, GLsizeiptr sz) {
    GLuint b = 0; GLint got = -1;
    pGen(1, &b); pBind(GL_ARRAY_BUFFER, b);
    pData(GL_ARRAY_BUFFER, sz, NULL, GL_STREAM_DRAW);
    GLenum e = glGetError(); pGetP(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &got);
    out("  %s BufferData(%d): id=%u err=%#x size=%d\n", tag, (int)sz, b, e, got);
    pBind(GL_ARRAY_BUFFER, 0);
}
static void tex_test(const char *tag) {
    GLuint t = 0;
    pGenT(1, &t); pBindT(GL_TEXTURE_2D, t);
    pTex(GL_TEXTURE_2D, 0, GL_RGBA, 256, 256, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
    out("  %s TexImage2D(256x256): id=%u err=%#x\n", tag, t, glGetError());
    pBindT(GL_TEXTURE_2D, 0);
}
static void shader_test(const char *tag) {
    static const char *src = "void main(){ gl_FragColor = vec4(1.0); }\n";
    GLuint s = pCS(GL_FRAGMENT_SHADER);
    pSS(s, 1, &src, NULL); pComp(s);
    GLint ok = -1; pGS(s, GL_COMPILE_STATUS, &ok);
    out("  %s shader compile: id=%u err=%#x status=%d\n", tag, s, glGetError(), ok);
}
static void render_test(const char *tag) {
    unsigned char px[16] = {0};
    glClearColor(0.25f, 0.5f, 0.75f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    glReadPixels(0, 0, 2, 2, GL_RGBA, GL_UNSIGNED_BYTE, px);
    out("  %s clear+readpx: err=%#x px0=%u,%u,%u,%u\n", tag, glGetError(),
        px[0], px[1], px[2], px[3]);
}

int main(void) {
    lg = fopen("probe_wgl11.log", "w");
    if (!lg) lg = stdout;
    out("probe_wgl11 start\n");
    HWND hwnd = CreateWindowExA(0, "STATIC", "glprobe11", WS_OVERLAPPEDWINDOW,
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
    pData = getp("glBufferData"); pGetP = getp("glGetBufferParameteriv");
    pGenT = getp("glGenTextures"); pBindT = getp("glBindTexture");
    pTex = getp("glTexImage2D");
    pCS = getp("glCreateShader"); pSS = getp("glShaderSource");
    pComp = getp("glCompileShader"); pGS = getp("glGetShaderiv");
    const int attribs[] = { 0x2091, 3, 0x2092, 2, 0 };
    HGLRC c2 = pAttribs(hdc, c1, attribs);
    out("ctx2 created: %p\n", (void *)c2);
    out("ctx1 tests:\n");
    buf_test("ctx1", 4096); tex_test("ctx1"); shader_test("ctx1"); render_test("ctx1");
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c2)) { out("ctx2 current FAIL\n"); return 1; }
    out("ctx2 tests (renderer %s):\n", (const char *)glGetString(GL_RENDERER));
    buf_test("ctx2", 1); buf_test("ctx2", 4096); buf_test("ctx2", 1048576);
    buf_test("ctx2", 3686400); tex_test("ctx2"); shader_test("ctx2"); render_test("ctx2");
    wglMakeCurrent(NULL, NULL);
    if (!wglMakeCurrent(hdc, c1)) { out("ctx1 rec FAIL\n"); return 1; }
    out("ctx1-after-ctx2 tests:\n");
    buf_test("ctx1b", 3686400); tex_test("ctx1b");
    wglMakeCurrent(NULL, NULL);
    out("DONE\n");
    fclose(lg);
    return 0;
}
