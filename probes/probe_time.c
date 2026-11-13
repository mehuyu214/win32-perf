// probe_time.c - pacing primitives under this stack: Sleep accuracy,
// WaitForSingleObject timeout accuracy, clock agreement/drift.
// Logs to probe_time.log in CWD and stdout.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>
#include <stdio.h>
#include <stdlib.h>

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
static int cmpd(const void *a, const void *b) {
    double d = *(const double*)a - *(const double*)b;
    return d < 0 ? -1 : d > 0 ? 1 : 0;
}
static void stats(const char *name, double *v, int n) {
    qsort(v, n, sizeof(double), cmpd);
    out("%s n=%d min=%.3f med=%.3f p90=%.3f max=%.3f", name, n,
        v[0], v[n/2], v[(int)(n*0.9)], v[n-1]);
}
static void sleep_test(const char *tag, DWORD ms, int reps) {
    double *v = malloc(sizeof(double) * reps);
    for (int i = 0; i < reps; i++) {
        double t0 = qpc_ms();
        Sleep(ms);
        v[i] = qpc_ms() - t0;
    }
    char name[64]; snprintf(name, sizeof name, "Sleep(%lu)%s", (unsigned long)ms, tag);
    stats(name, v, reps); free(v);
}
static void wait_test(DWORD ms, int reps) {
    HANDLE ev = CreateEventA(NULL, TRUE, FALSE, NULL);
    double *v = malloc(sizeof(double) * reps);
    for (int i = 0; i < reps; i++) {
        double t0 = qpc_ms();
        WaitForSingleObject(ev, ms);
        v[i] = qpc_ms() - t0;
    }
    char name[64]; snprintf(name, sizeof name, "WFSO(timeout=%lu)", (unsigned long)ms);
    stats(name, v, reps); free(v); CloseHandle(ev);
}
int main(void) {
    lf = fopen("probe_time.log", "w");
    QueryPerformanceFrequency(&freq);
    out("QPC freq = %lld Hz", (long long)freq.QuadPart);
    // clock agreement: QPC vs GetTickCount vs timeGetTime over ~12 s
    out("--- clock agreement (sampled every ~500 ms of Sleep(500)) ---");
    double base_q = qpc_ms(); DWORD base_g = GetTickCount(); DWORD base_t = timeGetTime();
    for (int i = 0; i < 24; i++) {
        Sleep(500);
        out("qpc=%+.1f gtc=%+lu tgt=%+lu", qpc_ms() - base_q,
            (unsigned long)(GetTickCount() - base_g),
            (unsigned long)(timeGetTime() - base_t));
    }
    out("--- Sleep accuracy, default timer resolution ---");
    sleep_test("", 0, 60); sleep_test("", 1, 60); sleep_test("", 2, 60);
    sleep_test("", 5, 60); sleep_test("", 10, 60); sleep_test("", 16, 60);
    sleep_test("", 33, 40); sleep_test("", 100, 20);
    out("--- WaitForSingleObject timeouts ---");
    wait_test(1, 60); wait_test(10, 60); wait_test(100, 20);
    out("--- with timeBeginPeriod(1) ---");
    timeBeginPeriod(1);
    sleep_test("[tbp1]", 1, 60); sleep_test("[tbp1]", 10, 60);
    wait_test(1, 60);
    timeEndPeriod(1);
    // ALU reference for TCG slowdown calibration
    volatile unsigned long acc = 0;
    double t0 = qpc_ms();
    for (unsigned long i = 0; i < 20000000UL; i++) acc += i ^ (acc << 1);
    out("ALU 20M iters: %.1f ms (acc=%lu)", qpc_ms() - t0, (unsigned long)acc);
    out("DONE");
    if (lf) fclose(lf);
    return 0;
}
