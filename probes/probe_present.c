// probe_present.c - decompose the D3D9 frame cost at 1280x720.
// Phases: A Clear+Present, B Present-only, C Clear-only,
// D textured-quad + Present (VN-like frame), A2 = A + Sleep(16).
// Per-frame QPC timings (us) for clear/draw/present go to probe_present.log.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>

static FILE *lf;
static LARGE_INTEGER freq;
static double qpc_us(void) {
    LARGE_INTEGER t; QueryPerformanceCounter(&t);
    return (double)t.QuadPart * 1000000.0 / (double)freq.QuadPart;
}
static void out(const char *fmt, ...) {
    char buf[1024]; va_list ap; va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap); va_end(ap);
    if (lf) { fputs(buf, lf); fputc('\n', lf); fflush(lf); }
    fputs(buf, stdout); fputc('\n', stdout); fflush(stdout);
}
static LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    if (m == WM_DESTROY) { PostQuitMessage(0); return 0; }
    return DefWindowProcA(h, m, w, l);
}
static void pump(void) {
    MSG msg;
    while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg); DispatchMessageA(&msg);
    }
}
struct FVF { float x, y, z, rhw; DWORD col; float u, v; };
#define FVF_FLAGS (D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1)

static IDirect3DDevice9 *dev;
static void run_phase(const char *name, int frames, int mode, IDirect3DTexture9 *tex) {
    // mode bits: 1=clear, 2=draw quad, 4=present, 8=sleep16
    double wall0 = qpc_us();
    for (int i = 0; i < frames; i++) {
        double f0 = qpc_us(), tc = 0, td = 0, tp = 0, t;
        pump();
        if (mode & 1) {
            t = qpc_us();
            IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET,
                D3DCOLOR_XRGB(255, 0, 255), 1.0f, 0);
            tc = qpc_us() - t;
        }
        IDirect3DDevice9_BeginScene(dev);
        if (mode & 2) {
            t = qpc_us();
            struct FVF v[4] = {
                {0, 0, 0, 1, 0xffffffff, 0, 0}, {PW, 0, 0, 1, 0xffffffff, 1, 0},
                {0, PH, 0, 1, 0xffffffff, 0, 1}, {PW, PH, 0, 1, 0xffffffff, 1, 1}};
            IDirect3DDevice9_SetTexture(dev, 0, (IDirect3DBaseTexture9*)tex);
            IDirect3DDevice9_SetFVF(dev, FVF_FLAGS);
            IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, v, sizeof(struct FVF));
            td = qpc_us() - t;
        }
        IDirect3DDevice9_EndScene(dev);
        if (mode & 4) {
            t = qpc_us();
            IDirect3DDevice9_Present(dev, NULL, NULL, NULL, NULL);
            tp = qpc_us() - t;
        }
        if (mode & 8) Sleep(16);
        out("frame,%s,%d,%.0f,%.0f,%.0f,%.0f", name, i, tc, td, tp, qpc_us() - f0);
    }
    out("phase,%s,frames=%d,wall_ms=%.1f", name, frames, (qpc_us() - wall0) / 1000.0);
}

#ifndef PW
#define PW 1280
#endif
#ifndef PH
#define PH 720
#endif
int main(void) {
    lf = fopen("probe_present.log", "w");
    QueryPerformanceFrequency(&freq);
    WNDCLASSA wc = {0}; wc.lpfnWndProc = WndProc; wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = "PRESPROBE";
    RegisterClassA(&wc);
    HWND hwnd = CreateWindowA("PRESPROBE", "presprobe", WS_OVERLAPPEDWINDOW,
        0, 0, PW, PH, NULL, NULL, wc.hInstance, NULL);
    ShowWindow(hwnd, SW_SHOW); UpdateWindow(hwnd);
    IDirect3D9 *d3d = Direct3DCreate9(D3D_SDK_VERSION);
    if (!d3d) { out("FAIL create9"); return 1; }
    D3DPRESENT_PARAMETERS pp = {0};
    pp.Windowed = TRUE; pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    pp.BackBufferFormat = D3DFMT_UNKNOWN; pp.hDeviceWindow = hwnd;
    HRESULT hr = IDirect3D9_CreateDevice(d3d, D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL,
        hwnd, D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp, &dev);
    out("CreateDevice hr=0x%08lx", (unsigned long)hr);
    if (FAILED(hr)) { out("FAIL device"); return 2; }
    // one 1280x720 texture, filled once (VN background stand-in)
    IDirect3DTexture9 *tex = NULL;
    hr = IDirect3DDevice9_CreateTexture(dev, PW, PH, 1, 0, D3DFMT_X8R8G8B8,
        D3DPOOL_MANAGED, &tex, NULL);
    out("CreateTexture hr=0x%08lx", (unsigned long)hr);
    if (SUCCEEDED(hr)) {
        D3DLOCKED_RECT lr;
        if (SUCCEEDED(IDirect3DTexture9_LockRect(tex, 0, &lr, NULL, 0))) {
            for (int y = 0; y < PH; y++) {
                DWORD *row = (DWORD*)((char*)lr.pBits + y * lr.Pitch);
                for (int x = 0; x < PW; x++) row[x] = 0xFF000000 | (x * 255 / PW) << 16 | (y * 255 / PH);
            }
            IDirect3DTexture9_UnlockRect(tex, 0);
        }
        IDirect3DDevice9_SetRenderState(dev, D3DRS_ALPHABLENDENABLE, TRUE);
        IDirect3DDevice9_SetRenderState(dev, D3DRS_SRCBLEND, D3DBLEND_SRCALPHA);
        IDirect3DDevice9_SetRenderState(dev, D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA);
    }
    // warmup
    for (int i = 0; i < 10; i++) {
        IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET, 0, 1.0f, 0);
        IDirect3DDevice9_Present(dev, NULL, NULL, NULL, NULL);
    }
    run_phase("A_clear_present", 90, 1 | 4, NULL);
    run_phase("B_present_only", 90, 4, NULL);
    run_phase("C_clear_only", 90, 1, NULL);
    run_phase("D_quad_present", 90, 2 | 4, tex);
    run_phase("A2_clear_present_sleep16", 90, 1 | 4 | 8, NULL);
    out("DONE");
    if (lf) fclose(lf);
    return 0;
}
