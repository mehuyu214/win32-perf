#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/ptrace.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/uio.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <stddef.h>

/* --- restored-environment path resolution (patched for portability) ---
 * Original build hardcoded /home/hatch/workspace/vn-trials/... paths.
 * This version resolves paths relative to the q32sup executable location:
 *   <ROOT>/qemu10/q32sup            (this binary)
 *   <ROOT>/qemu10/usr/bin/qemu-i386 (QEMU)
 *   <ROOT>/sysroot32/root           (SYSROOT)
 *   <ROOT>/qemu10/wrap              (WRAPDIR, created on demand)
 * Overrides: Q32_QEMU, Q32_SYSROOT, Q32_WRAPDIR environment variables.
 * If resolution fails, it falls back to the original hardcoded paths. */
static char QEMU_buf[1024], SYSROOT_buf[1024], WRAPDIR_buf[1024];
static const char *QEMU, *SYSROOT, *WRAPDIR;
static void resolve_paths(void) {
    char exe[1024];
    ssize_t n = readlink("/proc/self/exe", exe, sizeof(exe) - 1);
    const char *env;
    if ((env = getenv("Q32_QEMU"))) snprintf(QEMU_buf, sizeof(QEMU_buf), "%s", env);
    if ((env = getenv("Q32_SYSROOT"))) snprintf(SYSROOT_buf, sizeof(SYSROOT_buf), "%s", env);
    if ((env = getenv("Q32_WRAPDIR"))) snprintf(WRAPDIR_buf, sizeof(WRAPDIR_buf), "%s", env);
    if (n > 0) {
        exe[n] = 0;
        char *slash = strrchr(exe, '/');
        if (slash) *slash = 0;                 /* <ROOT>/qemu10 */
        char *up = strrchr(exe, '/');
        if (up) *up = 0;                       /* <ROOT> */
        if (!QEMU_buf[0]) snprintf(QEMU_buf, sizeof(QEMU_buf), "%s/qemu10/usr/bin/qemu-i386", exe);
        if (!SYSROOT_buf[0]) snprintf(SYSROOT_buf, sizeof(SYSROOT_buf), "%s/sysroot32/root", exe);
        if (!WRAPDIR_buf[0]) snprintf(WRAPDIR_buf, sizeof(WRAPDIR_buf), "%s/qemu10/wrap", exe);
    }
    if (!QEMU_buf[0]) snprintf(QEMU_buf, sizeof(QEMU_buf), "%s", "/home/hatch/workspace/vn-trials/qemu10/usr/bin/qemu-i386");
    if (!SYSROOT_buf[0]) snprintf(SYSROOT_buf, sizeof(SYSROOT_buf), "%s", "/home/hatch/workspace/vn-trials/sysroot32/root");
    if (!WRAPDIR_buf[0]) snprintf(WRAPDIR_buf, sizeof(WRAPDIR_buf), "%s", "/home/hatch/workspace/vn-trials/qemu10/wrap");
    QEMU = QEMU_buf; SYSROOT = SYSROOT_buf; WRAPDIR = WRAPDIR_buf;
    mkdir(WRAPDIR, 0755);
}

static int is32elf(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return 0;
    unsigned char h[20];
    int n = read(fd, h, 20);
    close(fd);
    return (n == 20 && h[0] == 0x7f && h[1] == 'E' && h[2] == 'L' && h[3] == 'F'
            && h[4] == 1 && h[18] == 3 && h[19] == 0);
}

/* read a string from tracee memory */
static int read_str(pid_t pid, unsigned long addr, char *buf, size_t cap) {
    struct iovec local = { buf, cap - 1 };
    struct iovec remote = { (void *)addr, cap - 1 };
    ssize_t n = process_vm_readv(pid, &local, 1, &remote, 1, 0);
    if (n <= 0) return -1;
    buf[n] = 0;
    /* make sure we got a full string; if buffer filled without NUL, treat as truncated */
    return 0;
}

/* write a string into tracee memory at addr (word-wise via POKEDATA) */
static int write_str(pid_t pid, unsigned long addr, const char *s) {
    size_t len = strlen(s) + 1;
    size_t i = 0;
    while (i < len) {
        long word = 0;
        size_t chunk = len - i < sizeof(long) ? len - i : sizeof(long);
        memcpy(&word, s + i, chunk);
        if (ptrace(PTRACE_POKEDATA, pid, addr + i, word) < 0) return -1;
        i += chunk;
    }
    return 0;
}

/* create (or reuse) a wrapper script for target; returns path in static buf */
static const char *make_wrapper(const char *target) {
    static char wpath[512];
    /* hash the target path into a number */
    unsigned long h = 5381;
    for (const char *p = target; *p; p++) h = h * 33 + (unsigned char)*p;
    snprintf(wpath, sizeof(wpath), "%s/w%lu.sh", WRAPDIR, h);
    if (access(wpath, X_OK) == 0) return wpath;
    char tmp[600];
    snprintf(tmp, sizeof(tmp), "%s.tmp", wpath);
    int fd = open(tmp, O_WRONLY | O_CREAT | O_TRUNC, 0755);
    if (fd < 0) return NULL;
    char body[1024];
    int bl = snprintf(body, sizeof(body),
        "#!/bin/sh\nexec %s -cpu ${Q32_CPU_MODEL:-max} -L %s \"%s\" \"$@\"\n", QEMU, SYSROOT, target);
    if (write(fd, body, bl) < 0) { close(fd); return NULL; }
    close(fd);
    rename(tmp, wpath);
    chmod(wpath, 0755);
    return wpath;
}

static void install_filter(void) {
    struct sock_filter filt[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_execve, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRACE),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_execveat, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRACE),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog prog = { .len = (unsigned short)(sizeof(filt) / sizeof(filt[0])), .filter = filt };
    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
    prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
}

int main(int argc, char **argv) {
    resolve_paths();
    if (argc < 2) { fprintf(stderr, "usage: q32sup <cmd> [args...]\n"); return 2; }
    pid_t child = fork();
    if (child == 0) {
        install_filter();
        ptrace(PTRACE_TRACEME, 0, 0, 0);
        raise(SIGSTOP);
        execvp(argv[1], argv + 1);
        _exit(127);
    }
    int status;
    waitpid(child, &status, 0); /* initial SIGSTOP */
    ptrace(PTRACE_SETOPTIONS, child, 0,
           PTRACE_O_TRACESECCOMP | PTRACE_O_TRACEFORK | PTRACE_O_TRACEVFORK |
           PTRACE_O_TRACECLONE | PTRACE_O_EXITKILL);
    ptrace(PTRACE_CONT, child, 0, 0);
    int root_status = 0;
    int alive = 1;
    while (alive) {
        pid_t pid = waitpid(-1, &status, __WALL);
        if (pid < 0) { if (errno == EINTR) continue; break; }
        if (WIFEXITED(status) || WIFSIGNALED(status)) {
            if (pid == child) { root_status = status; alive = 0; }
            continue;
        }
        if (WIFSTOPPED(status)) {
            int sig = WSTOPSIG(status);
            unsigned long event = (unsigned long)status >> 16;
            if (sig == SIGTRAP && event == PTRACE_EVENT_SECCOMP) {
                struct user_regs_struct regs;
                ptrace(PTRACE_GETREGS, pid, 0, &regs);
                long nr = regs.orig_rax;
                if (nr == __NR_execve || nr == __NR_execveat) {
                    unsigned long paddr = (nr == __NR_execve) ? regs.rdi : regs.rsi;
                    char path[512];
                    if (read_str(pid, paddr, path, sizeof(path)) == 0) {
                        char abspath[600];
                        const char *check = path;
                        if (path[0] != '/') {
                            char cwd[256];
                            char linkp[64];
                            snprintf(linkp, sizeof(linkp), "/proc/%d/cwd", pid);
                            ssize_t cl = readlink(linkp, cwd, sizeof(cwd) - 1);
                            if (cl > 0) { cwd[cl] = 0; snprintf(abspath, sizeof(abspath), "%s/%s", cwd, path); check = abspath; }
                        }
                        if (is32elf(check)) {
                            const char *wrap = make_wrapper(check);
                            if (wrap) {
                                unsigned long scratch = (regs.rsp - 1024) & ~15UL;
                                if (write_str(pid, scratch, wrap) == 0) {
                                    if (nr == __NR_execve) regs.rdi = scratch;
                                    else { regs.rdi = -100; /* AT_FDCWD */ regs.rsi = scratch; }
                                    regs.rsp = scratch;
                                    ptrace(PTRACE_SETREGS, pid, 0, &regs);
                                    fprintf(stderr, "[q32sup] execve %s -> %s\n", check, wrap);
                                }
                            }
                        }
                    }
                }
                ptrace(PTRACE_CONT, pid, 0, 0);
            } else if (sig == SIGTRAP) {
                ptrace(PTRACE_CONT, pid, 0, 0);
            } else {
                ptrace(PTRACE_CONT, pid, 0, sig);
            }
        }
    }
    if (WIFEXITED(root_status)) return WEXITSTATUS(root_status);
    if (WIFSIGNALED(root_status)) { signal(WTERMSIG(root_status), SIG_DFL); raise(WTERMSIG(root_status)); }
    return 1;
}
