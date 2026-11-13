// probe_dsound.c - DirectSound GetCurrentPosition granularity.
// Plays a 4 s looping silence buffer; polls play/write cursors for ~12 s,
// dumping (qpc_ms, play, write) whenever the play cursor changes, plus a
// heartbeat every ~250 ms. The step pattern is what a game engine syncing
// to audio position would observe.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>
#include <dsound.h>
#include <stdio.h>

static FILE *lf;
static LARGE_INTEGER freq;
static double qpc_ms(void) {
    LARGE_INTEGER t; QueryPerformanceCounter(&t);
    return (double)t.QuadPart * 1000.0 / (double)freq.QuadPart;
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
int main(void) {
    lf = fopen("probe_dsound.log", "w");
    QueryPerformanceFrequency(&freq);
    WNDCLASSA wc = {0}; wc.lpfnWndProc = WndProc; wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = "DSPROBE";
    RegisterClassA(&wc);
    HWND hwnd = CreateWindowA("DSPROBE", "dsprobe", WS_OVERLAPPEDWINDOW,
        0, 0, 320, 200, NULL, NULL, wc.hInstance, NULL);
    ShowWindow(hwnd, SW_SHOW);
    IDirectSound8 *ds = NULL;
    HRESULT hr = DirectSoundCreate8(NULL, &ds, NULL);
    out("DirectSoundCreate8 hr=0x%08lx", (unsigned long)hr);
    if (FAILED(hr)) { out("FAIL ds create"); return 1; }
    hr = IDirectSound8_SetCooperativeLevel(ds, hwnd, DSSCL_PRIORITY);
    out("SetCooperativeLevel hr=0x%08lx", (unsigned long)hr);
    WAVEFORMATEX wf = {0};
    wf.wFormatTag = WAVE_FORMAT_PCM; wf.nChannels = 2; wf.nSamplesPerSec = 48000;
    wf.wBitsPerSample = 16; wf.nBlockAlign = 4; wf.nAvgBytesPerSec = 48000 * 4;
    DSBUFFERDESC bd = {0};
    bd.dwSize = sizeof(bd); bd.dwFlags = DSBCAPS_GETCURRENTPOSITION2 | DSBCAPS_GLOBALFOCUS;
    bd.dwBufferBytes = 4 * 48000 * 4; bd.lpwfxFormat = &wf;
    IDirectSoundBuffer *buf = NULL;
    hr = IDirectSound8_CreateSoundBuffer(ds, &bd, &buf, NULL);
    out("CreateSoundBuffer hr=0x%08lx", (unsigned long)hr);
    if (FAILED(hr)) { out("FAIL buffer"); return 2; }
    void *p1; DWORD n1;
    hr = IDirectSoundBuffer_Lock(buf, 0, 0, &p1, &n1, NULL, NULL, DSBLOCK_ENTIREBUFFER);
    if (SUCCEEDED(hr)) { memset(p1, 0, n1); IDirectSoundBuffer_Unlock(buf, p1, n1, NULL, 0); }
    hr = IDirectSoundBuffer_Play(buf, 0, 0, DSBPLAY_LOOPING);
    out("Play hr=0x%08lx", (unsigned long)hr);
    out("fmt: t_ms,play,write (on change + heartbeat)");
    double t0 = qpc_ms(), lastBeat = 0;
    DWORD lastPlay = 0xFFFFFFFF;
    long polls = 0;
    while (qpc_ms() - t0 < 12000.0) {
        DWORD play = 0, write = 0;
        IDirectSoundBuffer_GetCurrentPosition(buf, &play, &write);
        double now = qpc_ms() - t0;
        polls++;
        if (play != lastPlay || now - lastBeat >= 250.0) {
            out("%.2f,%lu,%lu", now, (unsigned long)play, (unsigned long)write);
            lastPlay = play; lastBeat = now;
        }
    }
    out("polls=%ld DONE", polls);
    IDirectSoundBuffer_Stop(buf);
    if (lf) fclose(lf);
    return 0;
}
