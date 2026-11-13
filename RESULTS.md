# win32-perf — rendering performance investigation (Sanoba trial, unmodified)

Line: `win32-perf`, display **:115**, own prefix, own PulseAudio (tcp 47135),
workspace `~/workspace/win32-perf/`. Started 2026-11-13 (KK's order after viewing
sm47039951: perceived ~0.2 fps; improve the GAME's real update rate, not the
recording's appearance).

Production stack being measured (from win32-env docs, not re-derived):
q32sup → qemu-i386 (first proc 10.0.2, children 8.2.2-static wrappers) →
Wine 11.21 x86 → PE32 game → wined3d (D3D9→GL) → winex11 (EGL-only) →
Mesa 25.2.8 llvmpipe (i386, JIT under TCG = double-JIT tax) → Xvfb.
VM: no GPU, no /dev/dri, no /dev/kvm, ≈1.5 effective cores, 6 GB RAM.

Prior measured anchors (docs/PERFORMANCE.md, docs/AUDIO-RESULTS.md,
docs/SANOBA-ENC-REPORT.md §3.7, docs/ARCHITECTURE-OPTIMIZATION.md):
- Game process total CPU at title ≈17 % of one core (NOT CPU-saturated).
- Audio delivery 1.000 on an exclusive VM; contention is the dominant audio lever.
- d3d9test (trivial Clear+Present loop, 640×480): 234 frames / 25 s ≈ 9.4 fps.
  Re-read of `win32-env/tests/d3d9test.c` (2026-11-13, this line): the loop
  contains `Sleep(16)` per iteration, so per-iteration wall ≈107 ms of which
  ≈16 ms is the deliberate sleep ⇒ **≈91 ms of work per Clear+Begin/End+Present
  + message-pump cycle** for an empty scene. The present path is expensive even
  with nothing to rasterize.
- Title-screen content-change rate measured by the audio line: ~1 distinct/s
  (R1) / 0.23 distinct/s (M2 window) via grabs.
- F1 (audio line): unmapping the game window changed nothing — Kirikiri draws
  into its surface regardless; presentation-to-window was never the audio cost.
- F2 (audio line): with a clockless audio device the engine produced audio at
  2.57× realtime at title — the engine *can* run fast when unpaced.

---

## Phase 1.1 — What the published video actually contains (artifact analysis)

**SOURCE AUDIT (KK methodology rule, 2026-11-13 15:22, binding):** never judge
frame rate / content change / quality from the NicoNico-published video or any
lossy re-encode (`part1-nico.mp4`, `part1-view.mp4`). Audited 2026-11-13:
**every number in this section was computed on the raw masters** —
P1 rows from `~/workspace/sanoba-play/video/full/continuous-video.mkv`
(111,023,982 B, h264 1280×720 @20 fps CFR, 2765.85 s) and P3 rows from
`~/workspace/sanoba-play/video/full/continuous-video.part3.mkv`
(311,689,216 B); the machine-readable logs (`results_change.jsonl`,
`results_frames.jsonl`) record the source file per row and confirm this.
The rejected Method A pilot and the frameA/frameB visual + PSNR checks also
ran on `continuous-video.mkv`. `part1-nico.mp4` was only ever `ffprobe`d for
container metadata during setup, and the master was independently probed with
identical values; no rate, freeze, or magnitude figure derives from it.
§3's numbers come from live instances (own :115; :113 observed read-only),
not from any video file. All future measurements cite their exact source.

Method A (REJECTED, recorded for honesty): per-frame MD5 (ffmpeg framemd5,
full-res) on `continuous-video.mkv` (part 1 master, 1280×720 @20 fps CFR)
window 600–660 s suggested 19.57 content changes/s. Spot-check falsified it:
frames 0.5 s apart are bit-identical (PSNR ∞) and the two dominant alternating
frames differ at PSNR 79.1 dB — a sub-perceptual 1-LSB flicker flips hashes
every frame. Exact-hash uniqueness is noise-dominated on this material and
must not be used as a content-rate metric.

Method B (USED): magnitude-weighted change rate. ffmpeg
`scale=480:270,tblend=all_mode=difference,signalstats` → per-frame-pair mean
absolute luma difference (YAVG, 0–255 scale). Counts/s above thresholds:
0.02 ≈ character-sized text change; 0.1 ≈ clearly visible update;
0.5 ≈ line/sprite-level change; 2.0 ≈ large scene change.
Tool: `analyze2.py` (this workspace); raw JSONL: `results_change.jsonl`.
Each 60 s window: decode wall ~40–52 s at `-threads 1` (host-native).

| window | scene | ≥0.02/s | ≥0.1/s | ≥0.5/s | ≥2.0/s | longest freeze (<0.1) |
|---|---|---|---|---|---|---|
| P1 120–180 s | opening dialogue | 1.08 | 0.97 | 0.43 | 0.33 | 2.8 s |
| P1 600–660 s | dialogue Ch.1-1 | 1.13 | 0.82 | 0.33 | 0.27 | 8.05 s |
| P1 1200–1260 s | dialogue | 0.98 | 0.82 | 0.47 | 0.40 | 5.55 s |
| P1 2100–2160 s | dialogue (incident span) | 0.92 | 0.67 | 0.32 | 0.23 | 5.05 s |
| P1 2700–2760 s | dialogue (part end) | 1.17 | 0.82 | 0.40 | 0.32 | 3.05 s |
| P3 600–660 s | dialogue (quiet stretch) | 0.10 | 0.10 | 0.10 | 0.10 | **22.15 s** |
| P3 3600–3660 s | dialogue | 1.07 | 0.90 | 0.38 | 0.30 | 2.95 s |
| P3 7140–7200 s | dialogue (shimmer scene) | 0.93 | 0.62 | 0.25 | 0.18 | 5.65 s |

Aggregate (8 windows, 480 s): meaningful updates (≥0.1) ≈ **0.1–1.0/s**
(median ≈0.82/s), substantial (≥0.5) ≈ 0.10–0.47/s. The profile is uniform
across parts and session ages — no degradation trend from P1 to P3.

**Interim conclusion (part 1, dialogue):** the x11grab recorder delivered all
1200 frames per 60 s window (20 fps CFR, no drop signature), but the window
content itself only changes meaningfully ≈**0.8–1.0 times/s**, substantial
changes (≥0.5) only ≈0.3–0.5/s, with multi-second freezes (up to 8.1 s).
KK's ~0.2 fps perception matches the substantial-change rate. **The bottleneck
is on the game side, not the recording side**: the recorder faithfully captured
a screen that barely updates. (Whether the game's *presents* are rare or the
presents land but content crawls is exactly KK's A/B/C question — §3 below.)

## Phase 1.2 — Ten-second environment checks (2026-11-13, this line)

| check | result |
|---|---|
| `/dev/kvm` | absent (confirmed again) |
| `/dev/dri` | absent |
| host virglrenderer / virgl_test_server | NOT installed; `virgl-server_1.0.0-1ubuntu2_amd64.deb` fetched into `debs/` (noble pool, network reachable); `libvirglrenderer1_1.0.0-1ubuntu2_amd64.deb` resolved via a private apt state in `apt/` (package is in noble *main*, not universe); both debs extracted to `virgl/`; **`virgl_test_server --use-egl-surfaceless` starts and binds `win32-perf/virgl.sock` (PID-logged in logs/virgl-server.log) — arch-PoC Phase 0 PASS** (native host process, no rendernode needed) |
| guest virgl driver | **present**: `sysroot32/root/usr/lib/i386-linux-gnu/dri/virtio_gpu_dri.so` |
| guest zink driver | present (`zink_dri.so`) — needs a guest Vulkan ICD to be useful |
| lavapipe | absent on host (libvulkan loader only, no ICDs, no /usr/share/vulkan) and absent in sysroot (no libvulkan at all) |
| DXVK | not found anywhere in workspace trees |
| qemu builds on disk | 8.2.2-static tree (`vn-trials/qemu/`), 10.0.2 tree (`vn-trials/qemu10/`, incl. qemu-x86_64) |
| host Vulkan | loader `libvulkan.so.1` (x86_64) only |

## Phase 1.3 / KK hypothesis test — design (running)

KK: 「多分システム側の問題、描画が処理されてない」 — frames may not reach the
screen at all for long stretches. On the :115 instance, three counters over the
same fixed 60 s scene:
1. **Swap rate** — `GALLIUM_HUD=fps` + `GALLIUM_HUD_DUMP_DIR` (Mesa counts
   eglSwapBuffers per context; CSV dump). (= presents issued by wined3d)
2. **Landed-present rate** — XDamage (DeltaRectangles) events on the game
   window, counted host-side (`scripts/xdamage.py`). (= presents that reach
   the X front buffer)
3. **True content-update rate** — host XGetImage poller at 20 Hz over the
   window's text-box + centre rects with magnitude-weighted diffs
   (`scripts/xpoll.py`), plus game-process CPU% from /proc.
Case A: swaps ≫ damage. Case B: swaps ≈ damage ≈ low AND render CPU low
(blocked/starved upstream). Case C: swaps ≈ damage ≈ healthy, content diffs
tiny (logic crawling). Scenes: title, then dialogue with AUTO on.

### Run T1 — title scene, 60 s (VM load 1.0–1.7, own instance, production config)

- Swaps (GALLIUM_HUD csv): 19 samples over boot→title all in 0.08–0.44 range;
  during the measured title minute the csv did not advance at all (HUD writes
  only when a frame is drawn ⇒ **0 swaps in 60 s**).
- Window poller (20 Hz × 1200): **0 content changes**, max diff exactly 0.0 in
  both rects — pixel-frozen for the full minute.
- Game CPU: +981 ticks ≈ 16 % of one core (matches the known title profile).
- On clicking START, presents resumed immediately (fade-to-black presented,
  HUD blip) — the title loop waits, it is not dead.

### Run D1 — dialogue scene (Ch.1-1, AUTO on), 60 s (VM load ~7.8 falling)

- Swaps (HUD, 17 one-second samples in-window): **≈0.29/s** (0.195–0.387).
- Window poller: changes **0.267/s** (≥0.05), 0.25/s (≥0.2), 0.167/s (≥1.0);
  longest quiet stretch 7.4 s.
- Game CPU: +3371 ticks / 63 s ≈ **53 % of one core** — busy but not saturated.
- XDamage (first attempt): 1 event — **instrument bug** (DeltaRectangles
  without XDamageSubtract never re-arms after the first report; disclosed,
  fixed in `scripts/xdamage.py`).

### Run D2 — dialogue, XDamage re-run with fixed instrument, 30 s

- **Damage events: 11 = 0.367/s**, evenly spread — same order as swaps (0.29/s)
  and content changes (0.25/s). Presents that are issued, land.

### Cross-check — production instance :113 observed read-only, 20 s

- Window content changes 0.2/s (≥0.05) / 0.1/s (≥1.0); longest quiet stretch
  7.6 s. Same regime as this line's instance (its XDamage reading in that
  window is void due to the instrument bug above; the poller numbers stand).

### VERDICT on KK's hypothesis (measured)

- **Case A (presents issued but dropped/stalled in EGL→Xvfb): EXCLUDED.**
  Swaps ≈ landed presents ≈ content updates (0.29 ≈ 0.37 ≈ 0.25 /s). The
  X/recording path is faithful; the published video's 20 fps stream shows a
  screen that genuinely receives a new frame only every ~3–4 s.
- **Case C (presents fine, content crawls): EXCLUDED as stated** — presents
  themselves are only ~0.3/s, 30× below the same stack's trivial-app ceiling
  (d3d9test ≈9.4 presents/s, ≈91 ms of work per present).
- **Case B: CONFIRMED in substance** — for seconds at a time the game issues
  no presents at all while its process is not CPU-saturated (16 % title /
  53 % dialogue of one core). KK's 「描画が処理されてない」 is the correct
  picture: the bottleneck is *upstream of rendering* — the engine's main-loop
  pacing/blocking under this stack (script VM scheduling, timer waits,
  audio-position sync are the candidate pacers; rasterization is not the
  constraint at these scenes). Phase 2 therefore starts with pacer
  identification (clockless-audio A/B first: the F2 precedent showed the
  unpaced engine producing audio at 2.57× realtime), then the render-path
  levers (CSMT, softpipe A/B, virgl/vtest) measured against this baseline:
  **dialogue swaps ≈0.29/s, content ≈0.25/s, CPU ≈53 %**.

---

## Phase 2 (re-aimed by KK 2026-11-13 15:20) — pinpoint the blocking site

KK: category-level answers are not the deliverable; name the specific
function/processing that delays the game, fix it there, verify at natural
speed. Tooling reality in this sandbox (all measured 2026-11-13):
- `perf`: not installed. `gdb`: not installed (and attach would be ptrace).
- `strace -p` attach to the running qemu: **EPERM** (`PTRACE_SEIZE` refused).
- `strace -f` from birth with q32sup under it: **dead** — the supervisor's
  child gets `ptrace(PTRACE_TRACEME) = -1 EPERM` (already traced by strace);
  trace file `logs/../st-hello.txt` (47 lines). The whole ptrace family is
  unavailable against the supervised stack.
- `/proc/<pid>/task/*/syscall`: mediated, returns empty. `wchan` and `stat`
  DO work → per-thread sampling tool `scripts/tsample.py` (10 Hz: state,
  wchan, utime+stime) is the host-side profiler of record.
- Remaining pinpoint instruments: /proc thread sampling; WINEDEBUG
  timestamp-gap analysis; in-guest PE32 micro-benchmarks of the pacing
  primitives (Sleep/QPC/Wait/DSound-position/present decomposition) —
  compiler route: private-apt download of gcc-mingw-w64-i686 (pending).

### Thread inventory during a dialogue no-present stretch (measured)

Tool: `scripts/tsample.py` (10 Hz × 60 s, /proc only). Instance: own :115,
ALSA-null (clockless) config, Ch.1-1 dialogue, AUTO on (「オートモード」
indicator + line-complete star prompt in `logs/shot-alsa-dlg.png`).
Raw: `logs/tsample-alsa-dlg.csv` / `.json`.

- 42 host threads in the game qemu process; total CPU in window = 3296
  ticks ≈ **55 % of one core** (same as the PulseAudio baseline's 53 %).
- **Two threads do nearly all the work, both ~always in R state:**
  tid 14823 — 1812 ticks (30 % of a core), R in 96.8 % of samples;
  tid 14572 (initial thread) — 1324 ticks (22 %), R in 99.0 %.
- All other 40 threads ≈ idle: futex_do_wait / anon_pipe_read / poll
  (llvmpipe workers waiting for work; winealsa thread 14901 mostly in
  poll_schedule_timeout, 31 ticks total).
- ⇒ During the freeze the process is **not blocked on a futex/poll** in
  aggregate: two threads spin/run continuously while presents issue at
  ~0.3/s. The delay is *inside running code*, not a host-level wait.
  (Caveat: VM load was 7.7 — R-state includes runnable-but-starved time;
  CPU ticks are the reliable column.)

### Clockless-audio A/B (interim, same instance family)

- PulseAudio realtime (baseline D1): swaps ≈0.29/s, content ≥0.2 ≈0.25/s.
- ALSA null clockless (this instance): HUD ≈0.28–0.40/s across boot and
  dialogue; poller 45 s: changes 0.311/s at ≥0.05 but **0.0/s at ≥0.2** —
  the displayed line sat complete for the whole window (only sub-visible
  flicker, e.g. the star prompt's pulse). Swaps did NOT increase when the
  audio device stopped pacing consumption.
- **Interim conclusion: the realtime audio clock is not the frame pacer.**
  The remaining candidate pacers are inside the guest: timer/wait
  primitives, the engine's own scheduling, or a sync inside the
  wined3d/present path — to be separated by the micro-benchmarks below,
  not by more A/B swaps.

### Micro-benchmarks inside the stack (probes/, run via scripts/run-probe.sh on :115)

**probe_time — timers/wait primitives HEALTHY** (log: probes/probe_time.log).
QPC freq 10 MHz; QPC/GetTickCount/timeGetTime agree within ~10 ms over
12 s (no guest-time dilation under TCG). Sleep medians (n=60): 1→1.08,
2→2.08, 5→5.10, 10→10.10, 16→16.20, 33→33.56, 100→100.19 ms. WFSO
timeout medians: 1→1.18, 10→10.31, 100→100.95 ms. timeBeginPeriod(1):
no material change. ALU calibration: 20M iterations = 183.2 ms
≈ 109M simple ops/s under TCG. **No pacing primitive is broken.**

**probe_present — the frame cost, decomposed** (1280×720, CSMT default ON;
per-call QPC around each D3D call, 90 frames/phase; log:
probes/probe_present.log series, since rotated per run — values below):
- A Clear+Present: wall 38.5 s; Present call median **400.4 ms**
  (p90 587.8, max 621.1); Clear ≈0 (queued under CSMT).
- B Present-ONLY (nothing drawn): wall 33.6 s; Present median **383.0 ms**.
- C Clear-only (no Present): wall 0.34 s total — calls are free until flush.
- D fullscreen textured quad + Present: wall **148.1 s**; the Draw call
  itself median **1515 ms** (p90 2118.7) and Present then ≈0.5 ms — the
  frame's pipeline cost materialises at whichever call forces the flush.
- 640×480 (probes/probe_present_640.log): Present A 163.6 / B 176.9 ms;
  D draw 486.1 ms. Fit: **Present ≈ 74 ms fixed + ~0.34 µs/px**;
  draw ≈ **1.6 µs/px at both resolutions** (pure per-pixel cost).
- Per-frame series is FLAT from frame 0 to 89 (640 log: B presents
  100–210 ms throughout; D draws 400–900 ms throughout) ⇒ the cost is
  steady-state EXECUTION of llvmpipe's JIT-compiled shader code under
  QEMU TCG retranslation, not per-frame shader compilation.
- d3d9test's historical "~91 ms/frame" at 640×480 (with a deliberate
  Sleep(16)/iter) is consistent with this present-cost curve.

**probe_egl — pure EGL, no Wine** (ctypes python3.12 from the sysroot
under plain qemu-i386 on :115; probes/probe_egl.py): window surface
1280×720 on llvmpipe: eglSwapBuffers median **4.7 ms** (p90 56.6 =
contention spikes); pbuffer swap ≈0.0 ms. ⇒ Mesa's EGL→X11 leg costs
~5 ms; **the ~385 ms Present cost lives inside wined3d's Present
implementation above EGL** (its backbuffer→frontbuffer pass executed as
software GL work), not in EGL/X/recording.

**CSMT on/off A/B — NULL.** `"csmt"=dword:00000000` in own prefix, full
restart: A Present 399.1 ms, B 387.8 ms — identical to CSMT-on.

**Synthesis (measured):** one game frame = several fullscreen textured
quads (~1.5 s each at 720p, llvmpipe JIT code executed under TCG) + one
wined3d Present (~0.39 s) ≈ the observed ~3.4 s/frame (0.29 swaps/s).
The two hot tsample threads are the game main thread + the pipeline
worker grinding through exactly this. Timers, waits, QPC, the audio
clock, CSMT, and the EGL/X/recording path are each measured NOT to be
the pacer.

### virgl/vtest — guest-side selection BLOCKED on this Mesa build

Host server works: `virgl_test_server --use-egl-surfaceless` runs
(PID 12100, socket win32-perf/virgl.sock; arch-PoC Phase 0 PASS).
Guest (Mesa 25.2.8 i386 from the shared sysroot) refuses to create a
virgl screen through every selector tried, all via probe_egl win/surf:
- GALLIUM_DRIVER=virgl + VTEST_SOCKET_NAME → eglInitialize fails 0x3001
  ("failed to create dri2 screen").
- MESA_LOADER_DRIVER_OVERRIDE=virgl (+VTEST) on X11 → init succeeds but
  renderer stays llvmpipe (override ignored on the swrast path).
- + LIBGL_DRI3_DISABLE=1 + GALLIUM_DRIVER=virgl → 0x3001 again.
- Surfaceless platform + override + GALLIUM_DRIVER=virgl → 0x3001.
The vtest winsys code IS compiled in (strings in
libgallium-25.2.8-0ubuntu0.24.04.4.so: `VTEST_SOCKET_NAME`,
`/tmp/.virgl_test`), but Ubuntu's build only instantiates it behind a
DRM fd (virtio_gpu), which this VM cannot provide (no /dev/dri).
Unblock = custom guest Mesa build or a DRM-fd shim; not an env var.
This matches the architecture study's Phase-1 kill condition.

### softpipe — present leg collapses, then a deterministic crash

GALLIUM_DRIVER=softpipe, probe_present (log rotated:
probes/probe_present-crash-softpipe.log; stdout
logs/probe-present-softpipe-stdout.log):
- A Clear+Present: 90 frames in **0.80 s** (vs 38.5 s llvmpipe);
  per-frame total median 2.0 ms.
- B Present-ONLY: 90 frames in **0.29 s**; Present call median **0.5 ms**
  (vs 383.0 ms llvmpipe) — **the wined3d present pass costs ~770× less**
  because softpipe interprets TGSI instead of executing JIT code under TCG.
- C Clear-only: 3.6 ms total.
- D: frame 0 completed (draw 95.2 ms, present 1.0 ms), then the process
  CRASHED during frame 1: `wine: Unhandled illegal instruction at
  address 7F864DC5 (thread 007c)`. Reproduced identically (same address,
  same thread role) on re-run, also with DRAW_USE_LLVM=0.
- The real GAME under softpipe also crashed during boot (before title):
  `Unhandled illegal instruction at address 1F9FE0C4 (thread 0108)`
  (logs/game-softpipe1.log) — different address; identity with the probe
  site NOT assumed (see forensics below).

### Crash forensics — the probe's crash site, verified two ways

Derivation (parent + this line, independent objdump, same result):
- `logs/maps-20829.txt` is the probe process's /proc maps snapshot
  (contains probe_present.exe, d3d9.dll, DRI libs). In it,
  wined3d.dll spans 7f630000–7f8ef000; the crash address 0x7F864DC5
  falls inside at file offset **0x234dc5** → .text VA **0x10234dc5**
  (ImageBase 0x10000000).
- objdump of the on-disk
  `~/workspace/vn-trials/wine32/wine-11.21-x86/lib/wine/i386-windows/wined3d.dll`
  at 0x10234dc5: the instruction is exactly **`f3 a4` — REP MOVSB**,
  inside **wined3d_context_gl_copy_bo_address** (+0x5a5); preceding
  instructions load ECX (copy length) and branch `cmp $0x8,%ecx; jae`
  — the ≥8-byte copy branch. Surrounding disassembly is coherent code.
- Interpretation: the fault is raised in **wined3d's buffer-object copy
  path** (dlls/wined3d/context_gl.c copy_bo_address), first exercised
  by phase D's first texture/BO data copies — NOT in Mesa code. Why it
  is taken under softpipe but not llvmpipe (whose D phase completes):
  the drivers expose different GL capabilities, so wined3d selects a
  different BO upload/copy strategy per driver. Why REP MOVSB itself
  raises #UD/SIGILL under this QEMU is the open sub-question (REP MOVSB
  is an ancient instruction; candidate: a TCG fast-string path/feature
  interaction) — the CPU-mask A/B below tests exactly that.

### QEMU guest-CPU A/B — tooling fixed first, then NULL for llvmpipe

Tooling catch (recorded so the void run is not mistaken for evidence):
the first "-cpu Nehalem" attempt was VOID — q32sup caches its generated
wrapper scripts by target hash, and the whole stack funnels through
TWO cached wrappers (wine-preloader + wineserver) in the shared
production wrapdir; my Q32_QEMU shim never executed. Fix built in this
workspace: `tools/q32sup-perf` (own build of win32-env/src/q32sup.c,
wrapper template patched to `-cpu ${Q32_CPU_MODEL:-max}`), own wrapdir
win32-perf/wrap/. Verified delivery: child qemu cmdlines read from
/proc show `-cpu Nehalem` on all Wine-spawned processes.
- With delivery verified, llvmpipe probe_present under **-cpu Nehalem**:
  A Present median **483.6 ms**, B **414.2 ms** (n=63) vs -cpu max
  400.4/383.0 — inside contention noise. **CPU model / AVX codegen is
  NOT the llvmpipe tax.** (-accel tcg,tb-size is also dead: qemu-i386
  user mode rejects `-accel` as an unknown option.)

### OffscreenRenderingMode=backbuffer — NULL

Own prefix `[Software\Wine\Direct3D] "OffscreenRenderingMode"="backbuffer"`,
full restart, probe_present (llvmpipe): A Present **398.6 ms**, B
**374.0 ms** — unchanged. (Key removed again after the test.) Wine 11
either ignores the key or the present pass cost is in the swapchain
blit it performs regardless.

### DECISIVE combination — softpipe × restricted guest CPU (2026-11-13 16:0x JST)

Question (parent/KK): does restricting the guest CPU model make
softpipe's phase D complete (i.e. is the REP MOVSB fault
feature-dependent)? Delivery via tools/q32sup-perf + Q32_CPU_MODEL
(verified in /proc cmdlines). Probe: probes/probe_present.exe,
GALLIUM_DRIVER=softpipe, otherwise baseline config.

- **-cpu Nehalem**: A wall 1114.1 ms, B 1008.1 ms, C 108.5 ms (90 frames
  each) — then phase D CRASHED, same address **7F864DC5**
  (logs/probe-sp-neh-stdout.log; probe log rotated to
  probes/probe_present-sp-neh-crash.log).
- **-cpu qemu32** (strictest standard model): A wall 500.2 ms, B
  205.3 ms, C 70.1 ms; phase D frame 0 completed (draw **20.5 ms**,
  present 0.5 ms), then CRASHED at the same address **7F864DC5**
  during frame 1 (logs/probe-sp-q32-stdout.log).
- **Verdict: the fault is CPU-model-independent** (max / Nehalem /
  qemu32 — identical address, identical trigger point: second textured
  frame). No CPU mask rescues softpipe; the in-game softpipe run under
  a mask is therefore NOT attempted (the probe's D phase is the gate
  the parent set, and it does not pass). The REP MOVSB fault lives in
  the wined3d BO-copy path's interaction with this QEMU build,
  independent of advertised CPU features.

### Crash thread — status reframe (KK's discipline: site ≠ cause)

**ESTABLISHED (measured):**
- Probe under softpipe crashes deterministically during phase D frame 1
  (frame 0 completes), at reported address 0x7F864DC5, under -cpu max,
  Nehalem and qemu32 alike; the address maps (logs/maps-20829.txt) into
  wined3d.dll at the REP MOVSB inside wined3d_context_gl_copy_bo_address.
- **REP MOVSB itself is innocent**: probes/probe_movsb.exe runs 13 cases
  under the identical stack — counts 8/9/100/4096/65536/3,686,400
  (exact fullscreen-texture size), misaligned src/dst, page-crossing,
  page-crossing 3.67 MB, backward (DF=1), overlapping, CRT memcpy
  3,686,400 — **all PASS** (probes/probe_movsb.log). The instruction,
  including at texture-copy size, does not fault here.
- The game under softpipe crashed during boot at a DIFFERENT reported
  address (0x1F9FE0C4, thread 0108). A shared cause with the probe is
  **not** established; its forensics are a separate pending item.
- csmt=0 + softpipe (probe): no crash in phase A, but Present median
  **8003.8 ms** (n=14) — a ~20× regression vs llvmpipe CSMT-on; dead
  end, key removed. (It also proves the crash is CSMT-path-dependent:
  with the CS worker out of the loop, phase A presents crawl instead.)

**EXCLUDED:** REP MOVSB opcode support; CPU-feature dependence of the
fault (3 models, same address); CSMT as the llvmpipe pacer; ORM
backbuffer; guest timer/wait breakage; the audio clock as pacer;
EGL/X/recording path (pure-EGL swap 4.7 ms).

**HYPOTHESES (unproven, in test order):** (h1) the true fault is a bad
operand (source/dest/length) in the softpipe-specific BO-copy call —
classically SIGSEGV, so the SIGILL banner would be a QEMU/Wine signal
mistranslation; discriminated by the NT exception code in a +seh
capture. (h2) control flow lands mid-code and the bytes at the reported
address merely decode as REP MOVSB. (h3) state from frame 0's copy
corrupts frame 1's operands. Root cause is **not yet identified**;
per KK's re-aim, the fix goal (stable fast path in the game) outranks
completing this identification.

### Exception record captured (+seh) — the destination operand is NULL

Run: probe_present under softpipe, WINEDEBUG=+seh
(log: logs/probe-sp-seh-stdout.log). The crashing thread's dispatch
record, verbatim:

```
007c:trace:seh:dispatch_exception code=c000001d (EXCEPTION_ILLEGAL_INSTRUCTION) flags=0 addr=7F864DC5
007c:trace:seh:dispatch_exception eip=7f864dc5 esp=01aafd04 ebp=01aafd44 eflags=00000246
007c:trace:seh:dispatch_exception eax=01aafd6c ebx=00361df0 ecx=00080000 edx=00000000
007c:trace:seh:dispatch_exception esi=01e40030 edi=00000000 cs=0023 ds=002b es=002b fs=0033 gs=003b ss=002b
```

**ESTABLISHED from the record:** at the fault, the copy's operands are
ECX=0x00080000 (524,288 bytes), ESI=0x01e40030 (plausible source),
**EDI=0x00000000 — the destination pointer is NULL**, DF=0 (forward).
The REP MOVSB itself never gets to copy: its destination is address 0.
So (a) the proximate defect is that wined3d's BO-copy path is invoked
under softpipe with a **NULL destination BO address**; (b) the
delivered NT exception code for this null write is c000001d
(illegal instruction) rather than the c0000005 a null write classically
produces — the mistranslation is observed in the delivered code; which
layer (QEMU signal mapping vs Wine's handler) performs it is not
isolated and is **not** needed for the fix. Root cause narrowed to:
*why does the destination BO have no CPU address under softpipe* —
the fix space is path selection (make wined3d map the BO or use the
GL-side copy), tested next via Mesa extension masking.

### FIX FOUND (probe level) — mask GL_ARB_buffer_storage under softpipe

Config: GALLIUM_DRIVER=softpipe +
`MESA_EXTENSION_OVERRIDE="-GL_ARB_buffer_storage"`, baseline registry,
-cpu max. Run: logs/probe-sp-nobufstor-stdout.log, probes/probe_present.log.

- **The probe runs to DONE — no crash.** Phase wall times (90 frames
  each): A 679.4 ms, B 117.2 ms, C 6.7 ms, **D 22,973.4 ms**, A2
  2,710.0 ms. Per-call QPC medians: A present 0.5 ms, B present 0.3 ms,
  D draw-call 0.5 ms (the D phase's real cost is CS-thread execution
  time: wall 255 ms/frame vs llvmpipe's 1,645 ms/frame for the identical
  workload = **6.5× faster**, with presents at ~0.3–0.5 ms vs 383 ms).
- Mechanism (as far as established): with ARB_buffer_storage masked,
  wined3d no longer keeps persistently-mapped BOs whose CPU address can
  be NULL at copy time; it maps BOs on demand, and the copy_bo_address
  call that received EDI=NULL is no longer taken (or receives a real
  mapping). Which of those two is literally true inside wined3d is not
  separately proven — the crash's disappearance + full D completion is
  the measured fact.
- Next gate (KK's criterion): the GAME on this config — dialogue AUTO
  swaps/content/CPU vs 0.29/0.25 baseline, freeze distribution, real
  screenshot, ≥10 min stability.

### Game crash — causal chain from the game's own +wined3d/+opengl log

(Llvmpipe comparison run completed just before KK's retirement order;
kept ONLY as the diff baseline for this crash context — zero
"Failed to map" in its boot log. No further llvmpipe runs per KK.)

Softpipe game boot (logs/game-sp-w3d.log), thread 0104, immediately
before the crash — the swapchain FBO's colour attachment (texture 11)
reports **0x0 size**, FBO INCOMPLETE_ATTACHMENT; wined3d clears, then
uploads the backbuffer through a fresh PBO:

```
glGenBuffers -> 1; glBindBuffer(PIXEL_UNPACK_BUFFER, 1)
glBufferData(PIXEL_UNPACK_BUFFER, 3686400, NULL, STREAM_DRAW)
glMapBufferRange(PIXEL_UNPACK_BUFFER, 0, 3686400, access 0x22)
err:d3d:wined3d_context_gl_map_bo_address Failed to map bo.
err:seh:segv_handler Got unexpected trap -1
-> crash: REP STOSD (f3 ab) in wined3d_resource_memory_colour_fill,
   EDI=0, ECX=0xe1000 (1280x720), EAX=0
```

**ESTABLISHED:** glMapBufferRange returned NULL in-game (no GL error
was logged by checkGLcall anywhere in the log); wined3d logged the
failure and a downstream colour fill still wrote through the resulting
NULL address. The identical call SUCCEEDS in isolation under softpipe
in every variant tested (probes/probe_glbuf.py: exact params, write-only,
invalidate-range, 512K, ARRAY_BUFFER, DYNAMIC_DRAW, legacy glMapBuffer —
all PASS; probe_glbuf3.py: persistent/coherent BufferStorage maps with
wined3d-style flags 0xD3/0xF2 — all PASS after correcting my storage
flags; probe_glbuf4.py: same transient map under up to 3 GiB of
reserved guest VA — still PASS). So the in-game map failure is
**state-dependent**; the specific in-game state that makes Mesa return
NULL is **not yet identified** (hypotheses narrowed but unproven:
BufferData storage allocation failure in-game, or a gallium-level
transfer failure unique to the Wine process's context state).
Wine 11.21 source (tag wine-11.21, dlls/wined3d/context_gl.c) confirms
the code path: wined3d_bo_gl_map -> glMapBufferRange branches
(ARB_BUFFER_STORAGE persistent / ARB_MAP_BUFFER_RANGE / legacy
glMapBuffer), NULL propagates via wined3d_context_gl_map_bo_address
("Failed to map bo.") to callers that do not all guard it.

**MR !9956 verdict (evidence-based):** RELATED defect family, DISTINCT
upstream trigger. The MR (Zhiyi Zhang; closed unmerged 2026-02-05;
final commit 6f94224951 = one line, `internal_format_set = FALSE` on
backup-DC fallback in wined3d_context_gl_set_gl_context) addresses a
NULL bo_address produced by a FAILED BO CREATION during thread/window
teardown via the backup DC. In our stack: no backup-DC evidence in the
traced boot (no "Using backup DC"/set_pixel_format failure lines), no
thread teardown, and the failure is a NULL result from a MAP call on a
successfully created buffer, consumed by a colour fill. Same symptom
class (NULL address reaching a wined3d CPU memory op), different
proximate cause; the MR's one-line fix is therefore NOT expected to
change our crash and is not being applied as a guess. If a patched
wined3d is built later, the rational patch site is a guard where the
NULL is consumed, verified against rendered correctness.

## Game application phase (2026-11-13 16:36 JST) — recovery note

Probe work stopped at probes/probe_wgl3.c + probe_surfbuf.py. Final
probe-matrix state: through the Wine PE GL layer with wined3d's true
context topology (second context = core profile, shared at creation),
creating buffer storage and mapping a fully-visible shared BO from the
second context FAIL (OUT_OF_MEMORY / INVALID_OPERATION), while the
identical operations pass in the first context, in legacy wglShareLists
form only after sharing is skipped, and in every pure-EGL/python
variant (window, pbuffer, surfaceless — all PASS). The failing layer is
therefore inside the winex11 second-context path, not Mesa's buffer
implementation in isolation; pinning it further was stopped by KK's
order to apply levers to the game. Lever sequence: (1) softpipe +
CSMT OFF (single GL context — the control configuration that passes),
(2) softpipe + buffer_storage mask with CSMT on — ALREADY EXECUTED
three times before this phase (logs/game-sp-fix1.log,
game-sp-fix2-seh.log, game-sp-w3d.log; crashed at 0x1F9FE0C4 each time;
mask delivery proven by the 0x22 transient map flags in the w3d trace),
(3) the combination. Each lever: boot -> title -> story/AUTO gate
measurements (swaps/s, content/s, freezes, screenshot, stability).

### Lever 1 — softpipe + CSMT OFF (own prefix, "csmt"=dword:0): BOOT CRASH

Title NOT reached. Within ~55 s the game process died at the host
level: `qemu: uncaught target signal 11 (Segmentation fault) - core
dumped` (×2 processes; logs/game-sp-csmt0.log, 20 lines) — no Wine
exception banner this time, i.e. the fault (same NULL-address family
by context, not independently proven) surfaced as a native segfault
on the app thread instead of through the CS thread's SEH path.
Screenshots at +55 s/+115 s: black root window only; HUD produced no
new samples. Infrastructure note: a VM restart had wiped this line's
Xvfb :115 / PulseAudio / virgl server just before this phase; Xvfb and
PA (tcp 47135, null sink "game") were rebuilt before the run.
Lever 2 (mask, CSMT on) already stands at three recorded crashes.
Proceeding to lever 3 = mask + CSMT OFF.

### Lever 3 — softpipe + buffer_storage mask + CSMT OFF: GAME BOOTS, REAL SCENE RENDERED

Config: GALLIUM_DRIVER=softpipe,
MESA_EXTENSION_OVERRIDE="-GL_ARB_buffer_storage", own prefix
"csmt"=dword:00000000. Log: logs/game-sp-mask-csmt0.log.

**The game passed the boot crash point that killed every other
softpipe configuration** (lever 1 = signal-11 segfault; lever 2 =
c000001d at 0x1F9FE0C4 ×3; unmasked CSMT-on = same). At +180 s the
process (sanoba_trial.exe) is alive and the screen shows the game's
real age-warning screen — warning-triangle texture, gradient
background, full Japanese text, all correctly rendered
(logs/shot-maskcsmt0-t180.png, 548,401 B). Rendering correctness at
this stage: PASS (not a black/texture-less non-crash). Gate continues:
title -> story -> AUTO measurements + >=10 min stability clock
(started at launch, ~16:41 JST).

### Lever 3 heavy-vs-stuck discrimination (live instance, measured)

Question from KK: is the white-screen game stuck, or just extremely
heavy? Method: xpoll 90 s (logs/xpoll-l3-white90.csv), scripts/tsample.py
70 s on the game qemu pid 5550 (logs/tsample-l3-white.out), /proc tick
trend across the same window. Instance NOT restarted.

- Content: **0.022 changes/s** at every magnitude threshold (2 changes
  in 1800 polls / 90 s); longest pixel-identical stretch **65.3 s**.
- Threads: main thread (tid 5550) = **1981 ticks in 70 s (~28 % of one
  core), R-state in 99.6 % of samples** (wchan "0" = on-CPU); every
  other thread ~0 ticks, idle in futex/anon_pipe_read. Process total:
  9690 -> 12656 ticks across ~97 s (~30 % of one core).
- **Verdict: HEAVY-but-alive, single-threaded.** The (CSMT-off) main
  thread runs continuously in guest code; the screen changes about
  once per 45 s and presents run at ~0.02–0.04/s (HUD). Not idle, not
  deadlocked — per-frame work on the synchronous path is simply
  enormous (plus VM contention caps it at ~0.3 core). Stability: the
  instance passed **10 minutes without a crash** (~16:41 launch,
  alive at 16:52+) — lever 3 meets the stability criterion but fails
  the speed criterion by ~two orders of magnitude; it is a boot
  workaround, not the fix. The gate therefore still hinges on the
  CSMT-on fast path, i.e. on KK's already-mapped hypothesis and the
  wined3d patch route.

### KK's already-mapped hypothesis — CONFIRMED as the mechanism class

Probes: probe_wgl4.c (controls), probe_wgl5.c (clean pair), topology as
in wgl3 (ctx2 = core profile, shared at creation; 16 MiB BufferStorage
BOs, storage verified via BUFFER_SIZE). Sources: probes/probe_wgl5.log
(softpipe) and probes/probe_wgl5-softpipe.log naming aside, the llvmpipe
run of the same binary.

- **Control (same-context double map):** second map -> NULL, err
  **0x502** (GL_INVALID_OPERATION) — the error means "already mapped",
  as KK stated.
- **case0 (ctx1 maps, stays mapped; ctx2 maps):** -> NULL, err **0x502**
  under softpipe AND under llvmpipe (identical). Not driver leniency:
  both drivers are spec-strict.
- **caseA (ctx1 maps, ctx1 UNMAPS, ctx2 maps):** -> **SUCCEEDS** under
  both drivers (ctx2 even returns the same pointer value).
- Verdict: **the mapping state of shared BOs is the blocker.** A fresh
  map of an already-mapped shared BO fails with 0x502+NULL by spec;
  wined3d's allocator/BO map path attempts exactly that in the softpipe
  topology (its own map_ptr bookkeeping desyncs from the GL object's
  mapped state across wined3d's two contexts) and downstream code
  proceeds with the NULL. Under llvmpipe the game survives because
  wined3d happens never to attempt the double map there (different
  context/path timing), not because the driver tolerates it.
- Fix direction (KK's programme): patch wined3d's map handling so a
  map attempt on an already-mapped target REUSES the existing mapping
  (glGetBufferPointerv fallback) instead of failing into NULL —
  correctness-preserving (no data is dropped; the existing mapping is
  the data). A crash-avoidance-only NULL check is explicitly NOT the
  fix. Build + gate next. **[Major verdict — repo sync worthwhile.]**

### wined3d map-adoption patch — built, deployed, PARTIALLY verified; game blocked by a second, independent defect

Patch (own build of wine-11.21, tree win32-perf/wine-src, built with the
workspace mingw --enable-archs=i386; pristine source kept at
tools/context_gl.c.pristine): in wined3d_allocator_chunk_gl_map() and
wined3d_bo_gl_map(), when glMapBufferRange/glMapBuffer returns NULL and
ARB_MAP_BUFFER_RANGE is present, adopt the existing mapping via
glGetBufferPointervARB(GL_BUFFER_MAP_POINTER) instead of propagating
NULL. Deployed ONLY into the workspace copy win32-perf/wine32-patched/
(stock DLL kept as wined3d.dll.stock); production/shared trees untouched.

Established:
- probe_wgl6: the adoption primitive works in this stack — from ctx2,
  glGetBufferPointervARB returns ctx1's live mapping pointer, and
  writing through it succeeds.
- Patched probe_present (softpipe, CSMT on, unmasked): phase A frames
  run with presents of 128-512 us (vs 383 ms llvmpipe) and NO crash
  through the previously fatal early frames; run 1 was lost to session
  teardown (see below), the full D-phase completion is still open.
- Patched GAME (softpipe, CSMT on, unmasked, logs/game-patched1.log):
  STILL crashes in boot, "Unhandled illegal instruction at 7F76EA31
  (thread 0104)" — different VA because the rebuilt DLL's layout
  differs; +seh register capture for this build is still open.
- probe_wgl7 (bisect of the game's other failure): in the shared
  two-context topology, NEW buffer allocations in ctx2 (BufferData
  3.6 MB, BufferStorage 16 MiB) fail with **0x505 OUT_OF_MEMORY,
  size 0** — whether or not ctx1's buffer is currently mapped. The
  second context's allocation path itself is broken in this
  guest-softpipe stack; no map-side patch can fix a buffer that has no
  storage. This is a distinct defect from the already-mapped 0x502 one
  (which the patch does fix).
- Note: killing my lever-3 game (pid 5550) also took down my probe
  session (shared prefix wineserver/session) — run 1 of the patched
  probe was lost that way at phase A frame 13 (no crash in its log).

### CORRECTION — the two patched probe runs are CONFOUNDED; the ~8 s Present mode identified

Methodology failure (mine, flagged by KK via the parent): the patched
probe runs logs/probe-present-patched-sp.log (run 1) and
logs/probe-present-patched-sp2.log (run 2) were launched while the
prefix registry still carried "csmt"=dword:0 from the lever tests (the
key was only removed later, for the patched game run). Their CSMT state
was neither pinned nor verified. **Both runs are CONFOUNDED and must
not be cited as patch evidence in either direction.** (In my interim
reading I also took the wrong column of the probe's frame lines: the
format is frame,<phase>,<i>,<clear_us>,<draw_us>,<present_us>,<cum_us>;
the ~128-512 us figures were the CLEAR times.)

Recomputed Present-call (tp) medians, phase A, from the frame lines:
- patched run 1 (patched DLL, csmt off, mask off): 7937.7 ms (n=14)
- patched run 2 (patched DLL, csmt off, mask off): 8184.1 ms (n=9)
- STOCK DLL softpipe csmt-off probe (lever era,
  probes/probe_present-sp-csmt0.log): 7988.2 ms (n=15)
- nobufstor run (mask ON, probes/probe_present-wgl-era.log): A tp
  median 0.5 ms; phase walls A 679 ms/90, B 117 ms/90 (~1.3 ms/frame)
- original softpipe run (csmt on, mask off): A wall ~990 ms/90 frames

Verdict on the fingerprint: the ~8 s Present is a property of
**CSMT-off + softpipe + buffer_storage mask OFF**, identical for the
stock and patched DLLs (a suspiciously constant ~8.0 s quantum — a
fixed timeout-like wait in the serial present path; mechanism not
isolated). It does NOT contradict the nobufstor baseline: with the mask
ON the mode vanishes at probe level. Consequence for lever 3 (mask on
+ csmt off, in-game): its 0.022 content-changes/s crawl is NOT
explained by this 8 s present mode; the heavy-single-thread reading
stands for that cell. And CSMT-off softpipe in the GAME crashes at
boot with host signal 11 on BOTH DLLs (lever 1 stock; patched
logs/game-patched-csmt0.log, same qemu uncaught-signal-11 signature) —
CSMT-off is a dead cell on this stack regardless of the DLL.

From here: every patched run pins its CSMT state in the registry
before launch and verifies it from the live process (maps/environ +
registry hash recorded in a run header).

### Second defect characterised (KK: not a known upstream bug; report at resolution)

Established by probes wgl7-wgl9 (softpipe, guest stack), all in
probes/probe_wgl*.log:
- In the two-context topology, NEW buffer allocations (BufferData,
  BufferStorage) in the SECOND context fail with **0x505
  OUT_OF_MEMORY, BUFFER_SIZE 0** — whether or not any buffer is
  currently mapped, and (wgl9, corrected attribs) whether the second
  context is a CORE or a COMPATIBILITY profile (profile mask
  0x9126 = 1 core / 2 compat; the version string confirms each). The
  first (legacy) context allocates normally.
- Correction to my own earlier probe labelling: probes wgl3-wgl8 set
  attrib 0x2094 (WGL_CONTEXT_FLAGS_ARB) = 2, i.e. FORWARD_COMPATIBLE,
  not an explicit profile mask; wined3d's own context_create_wgl_
  attribs (context_gl.c) sets NO profile mask at all, only the GL
  version (3.3) — so wined3d's dedicated contexts here are default
  profile. The 0x505 conclusion is profile-independent per wgl9.
- At most two WGL contexts could be created in these probes; a third
  creation of any flavour failed (creation-order artefact not yet
  fully separated from a hard limit).
- The map-adoption patch does NOT address this defect (nothing exists
  to adopt when storage itself failed). In the patched CSMT-on probe,
  the D-phase still dies at frame 1, but the manifestation VARIES by
  run (map-chain + memcpy at 7FA46861 in one run; a call to address 0
  with no map-chain in another, in which the diagnostic build's
  chunk-create/chunk-map diagnostics never fired) — multiple NULL
  consumptions racing downstream of flaky second-context behaviour.
- wined3d-side consequence chain (source-verified): the allocator
  chunk (64 MiB, wined3d_context_gl_allocate_vram_chunk_buffer) is
  created with glBufferStorage on whichever context first needs VRAM;
  if that is the CS (second) context, storage fails here, the chunk's
  map then fails, and copy_bo_address's memcpy branch consumes the
  NULL (ARB_COPY_BUFFER branch requires both BOs present).

### Defect layer moved: raw EGL and raw GLX are HEALTHY; the break is in Wine 11's win32u OpenGL layer

Discriminators (all softpipe, guest stack):
- probe_egl2 (raw EGL, X11 platform, shared ctx2): BufferData and
  BufferStorage SUCCEED in ctx2.
- probe_glx / glx2 / glxD / glxS (raw GLX: attribs-core, compat,
  cross-connection, create+destroy-first, stencil configs): ALL
  healthy, ctx2 allocations succeed everywhere.
- Via WGL (winex11/win32u): second-context allocations fail 0x505
  (wgl7-wgl11), with order dependence (wgl12: a lone attribs context
  allocates fine; legacy-then-attribs-after-destroy fine; two live
  attribs contexts -> second creation fails outright).
- Wine 11 win32u/opengl.c architecture (source-read): every app
  context is created by egldrv_context_create via EGL with
  EGL_NO_CONFIG_KHR, SHARING with an internal per-profile ROOT
  context (root_core / root_compat / root_noerror, created lazily by
  internal_context_create), plus per-thread internal contexts sharing
  the root. In the wgl10 run, win32u logged:
  "err:wgl:internal_context_create Failed to create internal thread
  context with attrs {format 101 ... profile 0x1}" — an internal
  context creation failed across all formats.
- Working model (hypothesis, to be bisected by patch): the SECOND
  root context created lands on a broken EGL screen instance in this
  stack; contexts sharing that root inherit the allocation failure
  (0x505). First root (and its members) are healthy — matching
  wgl10 (compat ctx1 healthy, core ctx2 broken) and wgl12-A/C
  (first-created profile's contexts healthy).
- Fix candidates in win32u (buildable in win32-perf/build):
  V1 = single share-root for all profiles in get_root_context.
  V2 = default attribs profile -> compat (single root_compat).

### Wine MR !11161 — ABSENT from our 11.21 (established); backport in progress

MR !11161 "opengl32: Implement wglShareLists on the PE side and share
all unix contexts together" (7 commits, merged to master 2026-06-17;
key commit e0a0ab55202d "win32u: Share all unix-side GL contexts with
a global context"). Content check against the 11.21 tree
(win32-perf/wine-src): the MR's markers (global_context, null_context,
the new p_context_create(struct opengl_context*, HDC, const int*)
driver signature in include/wine/opengl_driver.h) are ABSENT; 11.21
carries the older root-context design (root_core/root_compat/
root_noerror + internal_context_create with the attrs-based
p_context_create). So the MR is a live candidate for our chain — it
reworks exactly the internal-context/sharing machinery whose failure
we measured (err:wgl internal_context_create, second-context 0x505).
Backport (cherry-pick onto 11.21) + discriminator ladder
(wgl10-C -> wgl12-C -> probe_present D -> game gate) in progress.
Also open from the raw-EGL work: config-less eglCreateContext fails
0x3004 on a fresh platform-X11 display in raw EGL for every profile
combination (probe_egl6), yet succeeds inside Wine — the in-Wine
display path differs from the raw probes in some loader respect not
yet isolated; the MR test may moot it.

## PATCH LINE FROZEN (2026-11-13 ~18:40, KK order)

State at freeze: winex11.drv version-supply patch (supply GL 3.3 attribs
when a profile mask is given without a version, for win32u internal
thread contexts) built as i386 via a local -m32 pipeline
(scripts/build-winex11-32.sh; extracted libc6-dev-i386/lib32gcc debs).
Blocker that froze the line: the self-built winex11.so does NOT
reproduce the Kron4ek binary's behaviour — with the self-build (patched
OR pristine source, verified both), the graphics driver fails to load
in the prefix (nodrv) unless linked -Bsymbolic, and even then attribs
context creation returns NULL where the Kron4ek build creates it (root
cause traced to build configuration: my configure lacked the host -dev
libraries, so SONAME_LIBGL and the X-extension sonames are UNDEFINED in
my config.h — the GLX/opengl support is compiled out). Comparisons
against the Kron4ek baseline are therefore meaningless on the self-build
tree. The MR !11161 backport is likewise parked (absent from 11.21,
established; its patches do not apply to 11.21 due to structural drift).
The patched tree currently holds the self-built winex11.so — DO NOT
USE wine32-patched for game runs; the stock tree is the baseline.
Repo-sync note: this freeze state + the virgl section below are
sync-worthy.

## VIRGL/VTEST CAMPAIGN (2026-11-13 evening) — game boots and renders
## on virgl, stalls at the title loop

KEY DISCOVERY (the earlier "guest selection blocked" verdict was
WRONG): the software-winsys virgl-over-vtest screen is selected with
GALLIUM_DRIVER=virpipe (not "virgl" — mesa-src
auxiliary/target-helpers/inline_sw_helper.h: driver name "virpipe" ->
virgl_vtest_winsys_wrap -> virgl_create_screen). The shipped Ubuntu
libgallium-25.2.8 in the sysroot contains "virpipe" and
"VTEST_SOCKET_NAME" strings — the path is compiled in. No custom Mesa
build needed. virgl_test_server (win32-perf/virgl, --use-egl-surfaceless,
socket win32-perf/virgl.sock) verified accepting; guest contexts
connect ("vtest_client_dispatch_commands: client context created").

ESTABLISHED:
- Raw GLX on virpipe (probe_glxswap.py, own :115 X server, guest stack):
  legacy context window swaps WORK: swap0 30.2 ms, swaps 1-4 =
  14.1/1.6/1.5/1.6 ms, err 0. (Compare: softpipe D3D9 Present median
  ~400 ms; the virgl present path is ~2 orders faster at the GL level.)
- The GAME (stock wine tree, own prefix, GALLIUM_DRIVER=virpipe +
  VTEST_SOCKET_NAME) boots through the logo sequence to the FULL TITLE
  SCREEN, rendered CORRECTLY (all textures, menu, logo;
  logs/shot-virgl3-t240.png, shot-virgl7-b.png). Boot-to-title ~3.5-4 min
  wall under current VM contention (production recording holds ~100%
  of one core). No crash in CSMT-on or CSMT-off virgl runs.
- At the title, the game then stalls: XDamage on :115 = 0.05 events/s
  (1 event in 20 s, attributable to my own screenshot) across virgl4/5/6/7;
  a 60 s x11grab capture (logs/cap-virgl6-60s.mkv) shows the title
  pixel-static over 25 s windows; the game does not respond to ANY input:
  scripts/click (XSendEvent), xdotool XTEST clicks (instant and 1.5 s
  held, with windowfocus on the correct game window 0xa00005 and on the
  second fullscreen window), keyboard Down/Return/Space after
  windowfocus (KK's suggestion — no effect, no highlight movement).
  vblank_mode=0 and CSMT-off variants: identical stall.
- Not audio: my line's PulseAudio (tcp 47135) had died in a VM restart
  (as had the :115 Xvfb — both restarted); with PA up, the game holds a
  live sink input (TVP/KIRIKIRI, not corked, BGM flowing, buffer
  latency ~341 ms) and STILL stalls. Wine game log: no err/fixme lines.
- Thread state at the stall (virgl7, game qemu): the two busiest
  threads (51 s and 30 s cumulative CPU) both blocked in anon_pipe_read;
  main thread near-idle. NOT a CPU-bound render loop; NOT a hard crash.
- Control memory: on THIS line with llvmpipe (Phase 1-2, hours earlier)
  the same prefix/game was driven into dialogue Ch.1-1 with the same
  input tooling — input worked there. (Not re-run; llvmpipe retired by
  KK. A fresh control would separate virgl-specific from
  environment-drift, since Xvfb/PA died unnoticed today once already.)

HYPOTHESIS (not established): after presenting the title, the game's
main loop blocks on a pipe-based wait that never completes on the virgl
path (candidates: a wined3d sync/fence completion routed differently
under virgl, or a TVP helper/movie-thread pipe), while boot-phase
presents (loading-driven) succeed. The stall is ABOVE the Mesa present
path — raw virgl swaps are fast and correct — and is not explained by
audio, vsync throttling, CSMT state, focus, or input method.

STATUS vs GATE: virgl FAILS the in-game gate as it stands (cannot enter
the story), despite passing rendering correctness at title and a ~250x
faster raw present. Story video/numbers: not obtainable until the
title stall is broken. Live instance left running: virgl7 (CSMT off,
title, sup-pid 20697) for any follow-up test.

## LLVPIPE CONTROL RUN (2026-11-13 ~19:28-19:45 JST) — the title stall
## is ENVIRONMENT-COMMON, not virgl-specific

KK authorised ONE llvmpipe control (one-time exception to the 16:14
retirement) for discrimination only. Successor agent ran it: virgl7
killed (recorded state preserved above), prefix csmt set back to 1
(Phase 2 baseline; the key had been left at 0 by the csmt0 virgl runs),
stock Kron4ek tree, own prefix, :115 (Xvfb alive, pid 13862), PA tcp
47135 verified LISTENING, launch.sh with NO GALLIUM_DRIVER /
VTEST_SOCKET_NAME (default llvmpipe stack). Log:
logs/game-ctrl-llvmpipe.log, sup-pid 24238, game pid 24240.

ESTABLISHED:
- Boot to title: screenshot at t+240 s is byte-identical to the virgl
  title (md5 2c0a7733...). No crash lines in the log.
- Content rate at title (xpoll 45 s, 900 polls @20 Hz, logs/
  xpoll-ctrl-title.csv): **0.0 changes/s at every threshold
  (0.05/0.2/1.0/5.0); the full 44.99 s window was static.** The X front
  buffer never changes at the llvmpipe title either. (Screenshot md5
  differences seen during the battery are the X-rendered cursor, not
  window content.)
- Input battery — IDENTICAL to the virgl tests, each followed by
  35-40 s observation + screenshot: XTEST click on START (85,475) with
  windowfocus on the game window 0xa00005; XSendEvent via
  scripts/click.py 85 475; XTEST held click (mousedown 1.5 s);
  keyboard Down/Return/Space after windowfocus. **NO transition, NO
  menu change, nothing.** (logs/shot-ctrl-after-{xtest,sendevent,
  held,keys}.png.)
- Thread states at title (tsample 30 s @10 Hz, logs/
  tsample-ctrl-title.csv): 43 threads, total 496 ticks/30 s
  (~16.5 % of one core — matches the Phase 2 title CPU of ~16 %).
  Busiest thread tid 24418: 326 ticks/30 s, R in 33 % of samples, top
  wchan **anon_pipe_read (198/300)**. Main thread 24240: anon_pipe_read
  268/300 when sleeping. So the llvmpipe title's busy threads ALSO sit
  predominantly in anon_pipe_read — the same wchan fingerprint as the
  virgl stall — though they do wake and burn CPU regularly (not a hard
  block).

VERDICT (by the pre-registered rule): llvmpipe ALSO stalls at the
title ⇒ **the title stall is environment-common, NOT virgl-specific.**
The virgl path is exonerated as the cause. Something in the common
environment drifted between Phase 2 (same prefix/game/tooling driven
into Ch.1-1 dialogue on llvmpipe, ~15:20-16:00) and this evening:
candidates (UNVERIFIED): the :115 Xvfb and line PA were silently
killed by a VM restart and restarted mid-evening; the prefix registry
was edited repeatedly (csmt toggles); game-side saved state in the
prefix/game dir accumulated across many runs. KK's discipline note:
"busy threads in anon_pipe_read" is a shared SYMPTOM on both stacks,
not a root cause on either.

NEXT (agent's delegated choice): hunt the common layer. No further
llvmpipe runs without KK's word; the virgl path remains the target
route once the common stall is broken. Repo-sync note: this verdict +
the virgl section are sync-worthy.

## OP / BOOT-SEQUENCE CAPTURE ON VIRGL (2026-11-13 ~19:39-19:45 JST, KK request)

Fresh virgl boot (GALLIUM_DRIVER=virpipe + VTEST_SOCKET_NAME, stock
tree, csmt=1) with x11grab started BEFORE launch; 380 s total.
File: logs/cap-op-virgl.mkv — ffprobe-verified: h264 1280x720 @20 fps,
7,599 frames, duration 380.000 s, 5,114,853 B. Game log
logs/game-op-virgl.log: no crash (0 signal-11). Instance left running
at the title (sup-pid 26422).

Timeline (capture t; launch at t≈4 s), from framemd5 (254 distinct
frames overall) + extracted stills:
- 0-~75 s: BLACK. Wine/qemu startup; no window content. (Six 12.3 s
  hash blocks are the same black frame modulo cursor/encoder noise.)
- ~76-96 s: Kirikiri window present, WINDOWED, white client area with
  menu bar (logs still loading).
- ~97-~103 s: age-warning screen (fullscreen, ATTENTION) — static hold.
- ~104-116 s: black again (~12 s); the logo does not hold as a
  readable still in this capture.
- ~117-130 s: title fades in (t=121 menu still ghosting; t=130 settled
  with menu). Boot-to-title ≈126 s from launch — faster than the
  earlier ~3.5-4 min virgl boots.
- 130-380 s: settled title; framemd5 cycles continuously through ~15
  distinct frames, longest identical run 0.10 s — the title's ambient
  sparkle animation IS being presented continuously in this run (the
  picture does not freeze pixel-static, unlike virgl3/4/5's settled
  titles between screenshots).

Motion character (for KK's own judgement from the file): the boot/OP
does NOT flow smoothly — it advances in long static steps (black ~75 s,
white window ~20 s, warning ~6 s, black ~12 s); genuine frame-by-frame
motion occurs only in the ~100-140 s transition band and in the
title's ambient loop after settling.

## COMMON-LAYER HUNT (2026-11-13 ~19:48- JST) — OP instance input test + :113 diff

Continued by successor agent. All readings on :113 are read-only; the
recording line was not disturbed.

### Step 1 — input battery on the still-running OP instance (sup-pid 26422)
The OP-capture instance (virgl, csmt=1, title settled, ambient ~15-frame
animation RUNNING) had never had input tested. Battery, same as before
(window 0xa00005, START at 85,475):
- baseline screenshot logs/shot-op-before.png (full title, menu present).
- XTEST click on START after windowfocus, +30 s: screenshot BYTE-IDENTICAL
  (logs/shot-op-after-xtest.png, md5 b1cf5272... == before).
- XSendEvent via scripts/click.py 85 475: no change (after-shot identical).
  NOTE: click.py itself died with SIGSEGV this time (it did not in the
  control run) — the tool's own crash, not a game event; the XTEST and
  keyboard paths are independent of it.
- Keyboard Down/Return/Space after windowfocus, +30 s: BYTE-IDENTICAL
  (logs/shot-op-after-keys.png).
VERDICT: input is dead on the OP instance too. The stall is NOT
intermittent per-instance: every title instance this evening (virgl3-7,
llvmpipe control, OP instance) is input-dead, including one whose title
keeps animating. Ambient presentation continuing while input is ignored
matches the earlier thread picture (title loop cycles, message/input
handling never advances the game state).

### Step 2 — stack diff vs the known-good recording line (:113)
ESTABLISHED (all read-only):
- Process envs: LANG/LC_ALL, LP_NUM_THREADS=1, PULSE_LATENCY_MSEC=750
  identical; only DISPLAY, PA port (47135 vs 47130), WINEPREFIX and the
  virgl vars differ — as designed.
- Xvfb: :115 "-screen 0 1280x720x24 -nolisten tcp"; :113 same minus
  -nolisten tcp. PA: same recipe (line-local pa-bin tree, own default.pa).
- Launch env files (scripts/my.env vs sanoba-audio/scripts/common.env):
  same LOCPATH, __EGL_VENDOR_LIBRARY_DIRS, LIBGL_DRIVERS_PATH, same
  qemu10 tree, same q32sup82 supervisor path, same wine tree. Only
  line-local paths differ (libs32, prefix, PA port, display).
- RUNNING supervisor binaries differ: :113's live game runs under
  sanoba-audio/q32sup-mine (their own build); :115's runs under
  qemu10/q32sup82. (common.env names q32sup82 too, so the live :113
  instance was started by a different script.) q32sup steady-state
  overhead was measured ~0 in the audio campaign; whether a supervisor
  variant can affect guest pipe/input behaviour is UNVERIFIED.
- Prefix registry: structure identical. win32-perf prefix adds only
  [Software\Wine\Direct3D] "csmt"=dword:1 (CSMT on = Wine 11 default)
  and a WineDbg section. Nothing input-related on either side.
- Game dirs: identical file sets; perf savedata additionally holds
  Kirikiri crash dumps from the softpipe/patch era (07:36-09:44) and
  more quick-save thumbnails. sanoba_trial.cfu identical (778 B,
  2026-11-12) on both lines.
CONCLUSION: no configuration smoking gun. Remaining untested state
variables: (a) prefix-internal state beyond user.reg sections
(system.reg / prefix files accumulated over the day's patched and
self-built Wine runs against THIS prefix), (b) the :115 display/PA
daemon instances themselves (restarted mid-evening after a silent
VM-restart death), (c) supervisor binary variant.

### Step 3 — fresh-state discriminator (RUNNING)
Fresh Xvfb on :116 (my line only) + FRESH prefix (prefix-fresh) +
virgl, everything else shared (sysroot, wine tree, q32sup82, PA 47135,
virgl server). scripts/fresh.env; log logs/game-fresh-virgl.log,
sup-pid 30143, launched 19:54 JST. If input works here, bisect
(prefix vs display); if it is still dead with all state fresh, the
cause sits in the shared binaries/VM layer, not in accumulated state.

### Step 3 — fresh-state discriminator: VERDICT (fresh display :116 + fresh prefix)
Fresh Xvfb on :116 + FRESH prefix (prefix-fresh) + virgl, everything else
shared. Boot (log logs/game-fresh-virgl.log, sup-pid 30143, 19:54 JST):
prefix init showed the wine-mono install prompt (fresh prefixes ask);
XTEST click on the dialog's Cancel at (707,440) dismissed it (a click at
(708,455) missed the button — coordinates, not input). The game then
booted to the title (logs/shot-fresh-t7.png: window 0xa00005, 1280x720,
title md5 b1cf5272... — BYTE-IDENTICAL to the OP instance's title).
Input battery on the fresh instance (all with 25-30 s observation):
- XTEST click on START (85,475): byte-identical (shot-fresh-after-xtest.png).
- XSendEvent via a repaired sender (scripts/click2.py, explicit window id;
  see tooling note below): press+release both ret=1, flushed — still
  byte-identical (shot-fresh-after-sendevent2.png).
- Keyboard Down/Return/Space: byte-identical (shot-fresh-after-keys.png).
VERDICT: with fresh display AND fresh prefix the title is STILL
input-dead (full battery, files prove it: every post-input shot md5
b1cf5272...). Accumulated prefix state and display/daemon state are
EXONERATED. The cause sits in the shared components or in how this line
launches (qemu tree, supervisor binary, wine tree, sysroot, line PA,
libs32) — or in the host/VM layer. Remaining untested state variables
after step 3: (a) supervisor binary variant (q32sup82 vs the recording
line's q32sup-mine), (b) line-local libs32 tree, (c) line PA daemon
(47135) vs theirs (47130) — the game itself does not need PA to accept
input, so (c) is a weak candidate.

TOOLING CORRECTION (affects earlier records): scripts/click.py
segfaults (SIGSEGV, exit 139) before sending, twice in a row on the
fresh runs — its XQueryTree children walk crashes; it prints nothing,
so XSendEvent was NEVER SENT in those two runs. Whether click.py
crashed or sent in the earlier virgl/control batteries was not recorded
at the time, so the "XSendEvent also dead" legs of the virgl3-7 and
control batteries are NOT reliably established (XTEST and keyboard legs
are — xdotool exits cleanly and the shots are byte-identical).
scripts/click2.py (explicit window id, step prints) is the replacement;
it verified press+release ret=1 on the fresh instance and still no game
reaction. The XSendEvent leg is therefore now established as dead on
the fresh stack.

### Step 4 — supervisor-variant test (q32sup-mine-copy), attempt log
The recording line's live game runs under sanoba-audio/q32sup-mine;
this line's runs use qemu10/q32sup82. The binary was copied (md5
8ce92e3e... identical) to sup-test/q32sup-mine-copy so its location-
derived paths stay inside this line's tree.
HARNESS BUGS, fixed in sequence (do not re-tread):
- Attempt 1 (20:04, log game-supmine-virgl.log): q32sup-mine derives
  the wrapper's qemu path as <base>/qemu10/usr/bin/qemu-i386 where
  base = dirname(dirname(/proc/self/exe)); the copy sat in
  win32-perf/sup-test, so the wrapper exec'd
  win32-perf/qemu10/usr/bin/qemu-i386 (does not exist). ALSO the
  wrapper file is generated once and REUSED — stale wrappers survive
  env changes.
- Attempt 2 (20:07): same stale wrapper (never deleted), same failure.
- The wrapper's qemu IS overridable: q32sup-mine reads Q32_QEMU
  (strings-verified). The recording line's own wrappers
  (sanoba-audio/mywrap/*.sh, read-only) exec
  vn-trials/qemu/usr/bin/qemu-i386-static — i.e. their runtime sets
  Q32_QEMU to the old static qemu. The fresh run's children ALSO ran
  under qemu-i386-static (q32sup82's compiled-in default), so
  Q32_QEMU=qemu-i386-static reproduces the fresh run's child-qemu
  exactly; the top-level $QEMU stays qemu10/usr/bin/qemu-i386 in both.
- Attempt 3 "supmine3" (20:08, log game-supmine3-virgl.log, sup-pid
  3431/3432): wrappers deleted and regenerated with Q32_QEMU set —
  verified on disk: preloader and wineserver wrappers both exec
  vn-trials/qemu/usr/bin/qemu-i386-static, byte-matching the recording
  line's wrappers. The ONLY remaining difference vs the fresh run is
  the supervisor binary itself. RESULT: NEW failure instead of the
  title stall — at ~20:08:46 the game log shows "lost connection to
  rendering server on 8 read -1 22" + "wine: Assertion failed at
  address 7DC06556 (thread 00f8), starting debugger..."; the :116
  screen stays BLACK with a cursor (shot-supmine3-now.png); the game
  window never appears. The supervisor process (3432) and a qemu child
  (3434) remain alive afterwards. Attribution is OPEN: supervisor
  variant vs post-VM-restart environment noise (the VM restarted at
  ~20:06, two minutes before this launch; the recording line's own
  q32sup-mine instance was still re-booting at the time). One clean
  re-run is planned to separate them.

ENVIRONMENT NOTE (VM restart ~20:06 JST): the restart wiped more than
processes this time — /usr/bin lost xdotool, scrot, xwininfo, xwd and
libXtst.so.6 (they were present before the restart). Tooling restored
from line-local copies: xdotool lives in win32-perf/pa-bin/usr/bin/
(and libXtst.so.6 in pa-bin/usr/lib/x86_64-linux-gnu/); screenshots
now via ffmpeg x11grab. scripts/xtest.py (libXtst via pa-bin) and
scripts/wininfo.py (ctypes XQueryTree) were added as replacements.

### Step 4 (concluded) — supervisor variant: q32sup-mine-copy LAUNCH-FAILS, twice
Re-run "supmine4" (20:13 JST, log game-supmine4-virgl.log, sup-pid 4452):
identical configuration to supmine3 (Q32_QEMU=static, :116,
prefix-fresh, virgl, PA 47135). REPRODUCED the same launch failure:
grep counts 2 matches for Assertion|lost connection|signal 11 within
75 s; child list shows 'winedbg --auto 240 96' spawned. So under
q32sup-mine-copy the game fails at launch 2/2 times (supmine3, supmine4)
with "lost connection to rendering server on 8 read -1 22" + wine
Assertion at 7DC06556 (thread 00f8); under q32sup82 with the same
everything-else (fresh run) it boots to the title 1/1.
CAREFUL about attribution: the ONLY difference between the fresh run
and supmine3/4 is the supervisor binary — top-level $QEMU (qemu10
dynamic), guest-child qemu (static, via Q32_QEMU=static in supmine
runs / q32sup82's compiled-in default in the fresh run), wrapdir
(wrap-fresh in both), display, prefix, PA, virgl are all identical.
So the supervisor variant DOES change the outcome at launch on this
line. BUT the recording line runs the same q32sup-mine binary (the
original, md5-identical) successfully — its stack differs in
DISPLAY :113, prefix, PA 47130, libs32, game dir, and llvmpipe (no
virgl). Which of those interacts with the supervisor is UNSEPARATED.
The supervisor finding does NOT by itself explain the title stall:
under q32sup82 (the normal supervisor) the game boots and stalls at
the title with dead input; under q32sup-mine it does not boot at all
here. Both block the goal. The stall under q32sup82 remains the main
roadblock; the supervisor launch failure is a second, separate defect
signature worth one more discriminator (q32sup-mine + llvmpipe on this
line) if time allows.

### Step 5 — game-dir savedata removed (RUNNING)
New discriminator launched 20:15 JST (log game-nosave-virgl.log,
sup-pid 4950): the perf game dir's savedata/ was moved aside to
savedata-bak/ (reversible; the game's own runtime state, not game
code/data — the recording line's savedata is untouched in its own
dir), then the EXACT fresh-run configuration (q32sup82, virgl,
:116, prefix-fresh) was relaunched. If input works with no savedata,
the perf savedata (datasc.ksd/datasu.ksd/data_anchor.ksd, accumulated
across the day's runs incl. crash dumps) is implicated. If it still
stalls, game-dir state is exonerated too, leaving: line libs32,
line PA, the qemu/wine/sysroot binaries, and the host/VM layer.

## SCORING METHOD (KK standard, 2026-11-13 19:55) — adopted for all footage
KK's definition: split a recording at 20 fps, award 1 point per frame
whose PICTURE changed vs the previous frame, graph points per second;
ideal = 10 pts/s. Calibration (parent, on logs/cap-op-virgl.mkv):
literal frame-hash (framemd5) scoring INFLATES — settled title 19.92
pts/s from sparkle noise, contradicting KK's own eye verdict (カクカク).
Picture-level scoring (each frame downscaled to 160x90 grayscale, then
hash-distinct) gives OP total 0.81 pts/s, boot 1.28/s, settled title
0.56/s, only 5 of 380 s reach >=10 pts — matching KK's judgement.
WORKING DEFINITION: "絵が変わっている" = the 160x90-grayscale-hash
series. All future footage scores (in-game captures, llvmpipe-魔改造
before/after on the same scene, story footage) use this method, with
the per-second graph and the 10 pts/s ideal as the judge. (A scorer
script implementing it is being added under tools/.)

### Boot-failure cluster post-restart — ROOT CAUSE FOUND (virgl server socket)
All three virgl runs after the ~20:06 VM restart (supmine3 20:08,
supmine4 20:13, nosave 20:15) failed identically at launch with
"lost connection to rendering server on 8 read -1 22" + wine Assertion
7DC06556. Root cause, measured:
- The virgl_test_server restarted after the restart (pid 3183) was
  ALIVE but NOT listening on ~/workspace/win32-perf/virgl.sock:
  the socket file was stale (mtime 09:41 UTC = pre-restart server),
  `ss -x` showed no listener at that path, and a python connect to
  the path got ECONNREFUSED. The guest's virpipe driver therefore
  could not reach the rendering server at first EGL init -> the
  assertion. My "server is up" check (pgrep only) was insufficient.
- Why: virgl_test_server does NOT read VTEST_SOCKET_NAME (that var is
  the CLIENT's). It binds the default /tmp/.virgl_test unless given
  `--socket-path <path>` (usage string verified). The 18:41 server
  must have been launched with --socket-path $WP/virgl.sock; my
  restart omitted it, so it bound /tmp/.virgl_test while every game
  pointed at the dead $WP/virgl.sock file.
- Fix verified: killed 3183, removed the stale socket file, restarted
  with --socket-path $WP/virgl.sock — fresh socket file, python
  CONNECT OK (server pid 5783). The re-run (nosave2, q32sup82) shows
  0 assertion matches at 60 s: the launch failure is GONE.
CONSEQUENCE: Step 4's supervisor attribution is WEAKENED — the nosave
run under the standard q32sup82 reproduced the identical assertion,
so the launch failure was the server socket, NOT the supervisor
variant. The supervisor question (q32sup82 vs q32sup-mine on this
line) is UNDECIDED again; the 2/2 assertion reproductions under
q32sup-mine-copy are explained by the dead socket, not by the
supervisor. (A clean q32sup-mine + llvmpipe discriminator is still
open if needed.)
LESSON (process): after any VM restart, verify every daemon by its
SERVICE (socket connect / port listen), not by process existence.
A persistent infra-check script is warranted (TODO for the line).

### nosave2 early stall — double-launch stale wineserver lock (own error)
The nosave2 run (sup 5800, 20:19) showed 0 assertions after the
server fix but sat BLACK with no window for ~8 min. Cause found in
the process tree: the EARLIER nosave instance (sup 4951) was still
alive — I had killed the launch bash (4950) instead of the setsid
supervisor (4951), so two game instances shared :116 and
prefix-fresh. Its wineserver socket dir /tmp/.wine-0/server-5b-660ce
(created 11:15 UTC by the old instance) outlived it; nosave2's log
contains ZERO wineserver execve lines and its game (3 threads,
utime ~60 ticks in 8 min, anon_pipe_read) never spawned a
wineserver. The double-launch stale lock is the likely cause of
THIS early stall — it is a separate signature from the title stall
(no window at all vs title reached, 3 threads vs 43). The stale
server dir was removed and the run relaunched singly (nosave3,
sup 7365, 20:27) — its child list already shows the wineserver
execve + wineboot --init, i.e. the wineserver IS spawning this time.
REMINDER (kill discipline): the .pid files hold the setsid wrapper's
pid, NOT the supervisor's; always kill the supervisor found via
pgrep on the actual supervisor binary, then verify zero game
processes remain before relaunching.
