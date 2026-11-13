/* probe_movsb.c - isolate REP MOVSB: does the instruction itself fault
 * under this qemu stack, across counts / alignments / page crossings /
 * directions / overlap? Prints one PASS line per case to probe_movsb.log
 * (and stdout). If every case passes, REP MOVSB per se is exonerated and
 * the wined3d crash must come from operands/state, not the opcode. */
#include <stdio.h>
#include <string.h>
#include <windows.h>

static FILE *lg;
static void out(const char *fmt, ...) {
    char buf[512]; va_list ap; va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap); va_end(ap);
    fputs(buf, lg); fflush(lg); printf("%s", buf); fflush(stdout);
}

static void rep_movsb_fwd(void *dst, const void *src, size_t n) {
    __asm__ volatile("cld\n\trep movsb"
                     : "+D"(dst), "+S"(src), "+c"(n)
                     : : "memory");
}
static void rep_movsb_bwd(void *dst_end, const void *src_end, size_t n) {
    __asm__ volatile("std\n\trep movsb\n\tcld"
                     : "+D"(dst_end), "+S"(src_end), "+c"(n)
                     : : "memory");
}

static unsigned cksum(const unsigned char *p, size_t n) {
    unsigned s = 0; for (size_t i = 0; i < n; i++) s = s * 131u + p[i];
    return s;
}

static int caseno = 0;
static void run_case(const char *what, unsigned char *dst, unsigned char *src,
                     size_t n, int backward) {
    caseno++;
    for (size_t i = 0; i < n; i++) src[i] = (unsigned char)(i * 7u + 13u);
    memset(dst, 0xEE, n);
    unsigned want = cksum(src, n);
    if (backward) rep_movsb_bwd(dst + n - 1, src + n - 1, n);
    else rep_movsb_fwd(dst, src, n);
    unsigned got = cksum(dst, n);
    out("case,%d,%s,n=%zu,%s\n", caseno, what, n,
        got == want ? "PASS" : "FAIL-CHECKSUM");
}

int main(void) {
    lg = fopen("probe_movsb.log", "w");
    if (!lg) lg = stdout;
    out("probe_movsb start\n");
    const size_t BIG = 1280u * 720u * 4u; /* one fullscreen texture */
    unsigned char *src = (unsigned char *)VirtualAlloc(NULL, BIG + 8192,
                             MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    unsigned char *dst = (unsigned char *)VirtualAlloc(NULL, BIG + 8192,
                             MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!src || !dst) { out("alloc FAIL\n"); fclose(lg); return 1; }

    run_case("small8", dst, src, 8, 0);
    run_case("small9", dst, src, 9, 0);
    run_case("small100", dst, src, 100, 0);
    run_case("page4096", dst, src, 4096, 0);
    run_case("k64", dst, src, 65536, 0);
    run_case("texture3686400", dst, src, BIG, 0);
    run_case("misalign_s1d2", dst + 2, src + 1, 100000, 0);
    run_case("misalign_s3d1", dst + 1, src + 3, 100000, 0);
    /* page-crossing: start 64 bytes before a 4096 boundary, copy 8192 */
    run_case("pagecross", dst + 4032, src + 4032, 8192, 0);
    run_case("pagecross_big", dst + 4000, src + 4000, BIG - 8000, 0);
    /* backward copy (DF=1) */
    run_case("backward64k", dst, src, 65536, 1);
    /* overlapping forward copy, dst = src + 1 */
    caseno++;
    for (size_t i = 0; i < 200000; i++) src[i] = (unsigned char)(i * 7u + 13u);
    rep_movsb_fwd(src + 1, src, 100000);
    out("case,%d,overlap,n=100000,PASS(no fault)\n", caseno);
    /* CRT memcpy, large (whatever implementation it picks) */
    caseno++;
    for (size_t i = 0; i < BIG; i++) src[i] = (unsigned char)(i * 7u + 13u);
    unsigned want = cksum(src, BIG);
    memcpy(dst, src, BIG);
    out("case,%d,crt_memcpy,n=%zu,%s\n", caseno, BIG,
        cksum(dst, BIG) == want ? "PASS" : "FAIL-CHECKSUM");
    out("DONE\n");
    fclose(lg);
    return 0;
}
