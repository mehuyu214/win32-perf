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

## COMMON-LAYER HUNT — CONSOLIDATED VERDICTS (2026-11-13 20:40 JST)
This section consolidates Steps 3-5 + Track C and CORRECTS earlier
wording. The parent synced commit bbeb643 (2026-11-13 ~20:36) with a
commit message saying the "launch failure is GONE" — that wording is
SUPERSEDED by logs/game-nosave3-virgl.log and is RETRACTED here:
the launch failure was NOT gone; it recurred with a different errno
(see Step 5 run 3 below).

### (1) Step 3 verdict — fresh state reproduces the input stall
(recorded in detail above under "Step 3 — fresh-state discriminator:
VERDICT") Fresh Xvfb :116 + fresh prefix + virgl: title reached,
full input battery dead (XTEST, repaired XSendEvent via click2.py
ret=1, keyboard), every post-input shot byte-identical (md5
b1cf5272...). ESTABLISHED: accumulated prefix state and display/
daemon state are EXONERATED as causes of the title stall. The stall
reproduces on fully fresh state under the normal supervisor (q32sup82).

### (2) Step 4 — supervisor variant, result AND its weakening
q32sup-mine-copy (md5-identical to the recording line's supervisor)
launched the game 2/2 times into a NEW launch failure
("lost connection to rendering server on 8 read -1 22" + wine
Assertion 7DC06556), while q32sup82 booted to the title. That looked
like a supervisor effect. WEAKENED by Step 5 run 1: the nosave run
under the STANDARD q32sup82 reproduced the IDENTICAL assertion
(errno 22) — so the launch failure was the virgl server's dead
socket, NOT the supervisor variant. The supervisor question
(q32sup82 vs q32sup-mine on this line) is UNDECIDED again; the 2/2
reproductions under q32sup-mine-copy are explained by the socket,
not by the supervisor binary. (The harness bugs found along the way
— stale wrapper reuse, Q32_QEMU override — are recorded in the Step 4
section above and remain valid tooling notes.)

### (3) Step 5 — the three no-savedata runs
All three ran q32sup82 + virgl + :116 + prefix-fresh, game-dir
savedata moved aside to savedata-bak/ (still aside at time of writing;
restore pending the outcome of the stall hunt — the files are the
perf line's own quick saves, not the recording line's).
- Run 1 "nosave" (20:15, log game-nosave-virgl.log, sup 4950/4951):
  INVALIDATED as a stall test. Assertion errno 22 at lines 14-15 —
  the virgl server socket was dead (see socket-path root cause
  below). Never reached the title. Also DOUBLE-LAUNCHED: the launch
  bash (4950) was killed instead of the setsid supervisor (4951),
  so a second instance shared :116/prefix-fresh and left a stale
  wineserver socket dir.
- Run 2 "nosave2" (20:19, log game-nosave2-virgl.log, sup 5800):
  INVALIDATED as a stall test. After the server-socket fix it showed
  0 assertions at 60 s, but sat BLACK with no window for ~8 min
  because the run-1 instance (4951) was still alive and the two
  instances fought over the prefix; its log has ZERO wineserver
  execve lines and its game (3 threads, ~60 ticks in 8 min) never
  spawned a wineserver — the stale /tmp/.wine-0/server-5b-660ce
  socket dir from run 1 is the likely cause. Stale dir removed;
  kill discipline corrected (kill the supervisor via pgrep, verify
  zero game processes before relaunch).
- Run 3 "nosave3" (20:27, log game-nosave3-virgl.log, sup 7365/7366):
  VALID run, NEW failure signature. Server socket FIXED and verified
  (CONNECT OK before launch), single instance, clean wineserver
  state (wineserver execve + wineboot --init in the child list).
  STILL failed at launch: "lost connection to rendering server on
  8 read -1 **104**" (ECONNRESET, not 22) + wine Assertion 7DC06556
  (thread 00ec) at log lines 14-15; :116 stayed BLACK, no window.
  The server log (logs/virgl-server.log) shows the cause: the
  server repeats "Couldn't open libEGL.so.1: libEGL.so.1: cannot
  open shared object file" — it has no EGL backend, so it RESETS
  the guest's connection at first context creation. THIS is the
  refutation of "launch failure is GONE": the socket-path fix
  removed errno 22, but the launch still fails, now with errno 104
  for a different reason (missing libEGL in the server).
- ROOT CAUSE (socket path), established: virgl_test_server does NOT
  read VTEST_SOCKET_NAME (client-side var); it binds the default
  /tmp/.virgl_test unless given --socket-path <path>. The post-restart
  server (pid 3183) was alive but bound /tmp/.virgl_test while games
  pointed at the stale $WP/virgl.sock file (mtime 09:41 UTC,
  pre-restart) -> ECONNREFUSED for the guest. Fixed by relaunching
  with --socket-path $WP/virgl.sock (server pid 5783, fresh socket
  file, python CONNECT OK). LESSON: after any VM restart, verify
  every daemon by its SERVICE (socket connect / port listen), never
  by process existence alone.

### (4) OPEN ITEM — virgl server cannot load libEGL.so.1
ESTABLISHED: the host lost libEGL.so.1 in the ~20:06 VM restart
(same restart also removed /usr/bin xdotool, scrot, xwininfo, xwd,
libXtst.so.6 — tooling restored from line-local pa-bin copies).
The host still has libgbm.so.1, libgl1-mesa-dri, libglx-mesa0,
mesa-libgallium 25.2.8 and the full dri/ tree, but no libegl package
(dpkg -l shows none; only i386 libEGL exists, in the sysroot).
apt-get update works (Ubuntu mirror reachable); `apt-get install
libegl1` and `libegl-mesa0` both report "Unable to locate package"
and apt-cache search returns nothing for libegl — the cache seems
to lack the main component's EGL entries (a second update + install
attempt was backgrounded and its outcome is not yet in this record).
Fallback if apt cannot supply it: extract libEGL.so.1 (+deps) from
the Ubuntu archive into a workspace-local tree and point the
server's LD_LIBRARY_PATH there; or build libEGL from mesa-src
25.2.8 (the Track B build route). Until the server can load EGL,
NO virgl game run can pass EGL init — the virgl route is blocked
at launch, which is a SEPARATE signature from the title input
stall (which was measured on pre-restart virgl runs with a working
server). The two must not be conflated in any verdict.

### (5) TRACK C — native WoW64 (no QEMU, no supervisor): DOES NOT WORK
KK's report (20:36): 64-bit Nukitashi ran buttery smooth on another
VM. Tested here on 2026-11-13 ~20:38-20:39, Kron4ek
wine-11.21-amd64-wow64 (~/workspace/vn-trials/wow64/), hybrid prefix
(~/workspace/vn-trials/wineprefix-hybrid), DISPLAY :116, PA 47135,
llvmpipe (no virgl), no QEMU/supervisor.
- hello64.exe: WORKS — "HELLO_FROM_PE", exit 0 (~17 s). Native
  64-bit Wine execution is confirmed on this VM post-restart.
- hello32.exe (WoW64): DOES NOT RUN. Two attempts: (a) timeout 60 s
  foreground — zero output; (b) backgrounded, sampled at 30 s —
  process (start.exe, pid 10593) alive with CPU time 00:00:00,
  /proc maps contain NO wow64.dll / wow64cpu.dll / wow64win.dll
  and NO syswow64 mappings (only 64-bit Windows DLLs + NLS
  files), no children, empty log. Killed afterwards.
VERDICT: the 2026-11-12 WoW64 verdict is REPRODUCED exactly — the
sandbox blocks 32-bit code-segment execution below Wine, in any
form (native ELF32 segfaults; WoW64 children never map the 32-bit
runtime). The 64-bit Nukitashi result on another VM does not change
this VM's 32-bit block. Track C is CLOSED: Sanoba (PE32) cannot run
under native WoW64 here; the qemu-i386 + q32sup detour remains
necessary. (The game itself was not launched under WoW64 — the
hello32 result makes that moot; no point burning a game boot on a
dead path.)

### Current state of the stall hunt (as of 20:40 JST)
- Title input stall: ESTABLISHED on fully fresh state (Step 3);
  environment-common, not virgl-specific (llvmpipe control);
  NOT intermittent per-instance (OP instance too). Untested
  remaining variables: line libs32 tree, line PA 47135, the
  qemu/wine/sysroot binaries, host/VM layer, and (still open)
  whether the perf savedata itself matters (Step 5's intended
  test never reached a title — savedata still aside).
- Virgl route: BLOCKED AT LAUNCH post-restart by the server's
  missing libEGL (open item above) — fix that first, then the
  title stall is again the live blocker on virgl.
- Track B (llvmpipe 魔改造）: not yet started — probe_present
  baseline re-measurement + LP_NUM_THREADS sweep are the next
  cheap steps; mesa rebuild needs i386 LLVM dev (only runtime
  libLLVM in sysroot — see Track B notes). Scorer tool
  tools/score_frames.py is written (KK's 160x90 picture-level
  method) and awaits validation against cap-op-virgl.mkv.
- Infra debt: write a persistent post-restart infra-check script
  (Xvfb/PA/virgl-server verified by SERVICE, not by pid) so the
  next VM restart does not cost another hour of phantom failures.

### TRACK C — CANCELLED per KK (2026-11-13 20:41)
KK countermanded Track C: WoW64 was ALREADY verified and FAILED on
2026-11-12 (Wine 11.21 normal AND Staging builds could not execute
32-bit PE; transition into 32-bit compatibility mode blocked by the
VM's execution environment). The :104 record cited for the track was
window metrics only, NOT PE32 execution success — that citation was
an error. No further WoW64 work: no downloads/builds for it unless
genuinely new evidence overturns the 2026-11-12 result. The hello32
retest in this line (20:38-20:39, same signature: CPU time 0, no
wow64 DLLs mapped) was the last WoW64 action and is recorded above
as a reproduction, not as an open lead. Nothing was fetched for
Track C — the Kron4ek wow64 trees were already on disk from 11-12.

### libEGL via apt — CLOSED (2026-11-13 ~20:42)
Background apt job proc_6efcbd654b20 (install libegl-mesa0, then a
second apt-get update) COMPLETED exit 0: `E: Unable to locate
package libegl-mesa0`; the follow-up update reported no errors.
ESTABLISHED: apt cannot supply libEGL on this VM even after a clean
update (libegl1 also unlocatable; apt-cache search returns nothing
for libegl). Remaining routes for the virgl server's EGL backend:
(a) fetch the .deb directly from archive.ubuntu.com and extract it
into a workspace-local tree (system installs do not survive VM
replacement anyway); (b) build libEGL from mesa-src 25.2.8.

### KK's restated policy (2026-11-13 20:41, binding)
- Proven base: QEMU-i386 + Wine32 + supervisor (story execution +
  recording results on the production line). virgl/vtest: correct
  title rendering + fast GL swaps, three open problems — progression
  stall, OP slowness, post-restart rendering-server connection
  failure.
- Success = story progresses normally with input, audio and
  rendering all functioning + measured speed/stability improvements.
  Probe numbers and title screens do NOT count.
- No re-verification of already-failed routes; no fixation on any
  single method (virgl / llvmpipe mods / Wine-QEMU-supervisor / any
  rational route — choose by measured promise).
- Recording line :113 is preserved; hands off entirely.
- Immediate shape: re-establish a RELIABLE virgl boot (vtest server
  launch env, libEGL lead), then the title input stall is the
  central blocker; Track B (llvmpipe mods incl. partial-present)
  proceeds as the speed track.

## INPUT BREAKTHROUGH — env-recipe run (2026-11-13 20:52-21:05 JST)
### The diff (win32-env official recipe vs this line's launch)
Read-only source: ~/workspace/win32-env/scripts/start-x.sh,
scripts/games/launch-game.sh, scripts/env.sh. Cave Story playtest
(20:26-20:41) ran that recipe verbatim and got working input.
| element | win32-env recipe | this line (my.env/fresh.env) |
| X display | :99, 1600x900x24, plain Xvfb | :115/:116, 1280x720x24, -nolisten tcp |
| audio | ALSA null (asound-null.conf: pcm/ctl !default type null) | PulseAudio tcp 47135 + PULSE_LATENCY_MSEC=750 + libs32 pulse libs |
| GL env | __EGL_VENDOR_LIBRARY_DIRS + LIBGL_DRIVERS_PATH only | same two + LP_NUM_THREADS=1 + LD_LIBRARY_PATH (libs32) + GALLIUM_DRIVER=virpipe (virgl runs) |
| supervisor | q32sup (repo lineage; md5 90ee109a... in vn-trials/qemu10/) | q32sup82 (md5 7298e63f...) |
| Q32_QEMU | UNSET (children under dynamic qemu-i386) | static qemu-i386-static (my.env) |
| QEMU top | qemu10 dynamic, -cpu max -L sysroot | same |
| Wine/sysroot | wine-11.21-x86 + sysroot32 (same lineage) | same (vn-trials copies) |
| prefix | fresh wineprefix-games, wineboot --init if missing | prefix / prefix-fresh |
| launch | foreground exec of supervisor | setsid nohup ... & |
| WM/focus | none (bare Xvfb) | none (bare Xvfb) |
Note: the win32-env checkout here holds only SOURCES (src/q32sup.c)
+ tarballs (archives/); the live binaries are the vn-trials copies.
The adapted run therefore used vn-trials binaries throughout.

### Adapted run (scripts-env/launch-sanoba-env.sh, log game-envrecipe-llvmpipe.log)
Env-recipe structure on MY line only: DISPLAY :116, WINEPREFIX
prefix-fresh, perf game dir (savedata STILL aside in savedata-bak/),
supervisor q32sup (90ee109a), Q32_QEMU unset, ALSA null, no PA,
no LP_NUM_THREADS, no GALLIUM_DRIVER (llvmpipe default), no
LD_LIBRARY_PATH, fresh wrapdir wrap-env/. sup 14112, game 14114.
Boot to title: ~210 s (shot-env-t210.png: full title, correct).
0 assertions in the game log (only benign libEGL DRI3 warnings).

### EXACT input sequence (all on :116, via scripts/xtest.py + libXtst)
- Focus-click: `xtest click 640 200` (tap, ~100 ms press) — frame
  changed (cursor moved); NO menu effect.
- START tap: `xtest click 105 465` — NO effect after 20 s.
- Focus probe (ground truth): XGetInputFocus = **0x1 (PointerRoot)**,
  pointer at 105,465 over window **0xa00005** — clicks REACH the
  game window but focus never moves (no WM; a click does not set
  focus by itself in bare X). wininfo.py segfaults (broken Attr
  struct) — do not use; pointer/focus queried via inline ctypes.
- Explicit focus: `xtest focus 0xa00005` — verified focus 0xa00005.
- START tap again WITH focus set: STILL no effect (byte-identical
  shot after 20 s). Mouse tap-clicks do not register, focused or not.
- `holdkey Down 1.0s` then `holdkey Return 1.0s` → **LOAD screen**
  (12 empty slots, SAVE/Q.LOAD/BACK) — INPUT WORKS via held keys.
- `holdkey Escape 1.0s` → title, START highlighted (selected).
- `holdkey Return 1.0s` on START → black transition (~25 s) →
  **Chapter 1-1 dialogue**: sky background, 【女子】「あの……
  保科君、ちょっといいかな？」 (shot-env-story1.png).
- `holdkey A 1.0s` → **AUTO ON** ("Auto ▶" indicator bottom-right,
  ▶ highlighted in the bottom bar); scene advanced to the school
  hallway on its own.
- 60 s capture logs/cap-env-story60.mkv (1280x720 @20fps, 567,972 B,
  60.000 s) under AUTO; end frame: hallway + narration 「新しい学年
  になって約半年。夏休みも明けた９月ともなれば、クラスメイトとも
  打ち解けている。」 AUTO still on, story advancing.
- `holdkey A 1.0s` (AUTO off), then killed sup 14112. Final uptime
  12:35, game CPU time 5:04, ~35-40% CPU during story. 0 crashes.
  Recording line processes (2911/2912) untouched.

### REVISED stall characterization (supersedes "input dead")
ESTABLISHED: the title is NOT input-dead. Mouse tap-clicks and short
key taps do not land; HELD keys (1.0 s) DO — same pattern as the Cave
Story playtest. The game loop is alive (title animates, story
progresses, AUTO advances). The evening's "full input battery dead"
verdict is REVISED: every battery used taps/clicks (XTEST tap 100 ms,
keyboard taps ~80 ms, XSendEvent, 1.5 s HOLD-click was tried once on
the control run but WITHOUT explicit focus and WITHOUT held keys).
HYPOTHESIS (unmeasured): short synthetic events fall between the
game's input polls under emulation slowness (10-40% realtime), so
only events held across a poll are seen. Mechanism NOT established.
OPEN: whether a held MOUSE click works (untested); whether held keys
work on the standard my.env stack (q32sup82 + PA) — the env recipe
was NOT bisected, so its elements (ALSA vs PA, q32sup vs q32sup82,
dynamic vs static children, LP_NUM_THREADS) are NOT individually
implicated or exonerated. Next run should bisect: my.env + explicit
focus + held keys.

### First in-story KK-score (llvmpipe, env recipe, AUTO, Ch.1-1)
tools/score_frames.py (first use — validates: 1200 frames = 60 s x
20 fps) on logs/cap-env-story60.mkv, picture-level (160x90 gray):
**mean 4.03 pts/s, median 3.0, 6 of 60 s >= 10 pts/s** (ideal 10).
Scores: logs/cap-env-story60-scores.json/.csv/.png. Context: VM
under contention (recording line :113 also capturing + x11grab);
llvmpipe in-story dialogue advances every few seconds, so ~4 pts/s
is the dialogue-advance rate, not a smooth-motion rate. Compare
later: same scene on virgl (once its server is fixed) and on a
Track B llvmpipe variant.

### Virgl server status (parked behind this lead)
- Route (a) DONE: libegl1 1.7.0-1build1 + libegl-mesa0 25.2.8
  (noble) apt-downloaded, extracted to $WP/virgl-libs/ (libEGL.so.1
  + libEGL_mesa.so.0 + 50_mesa.json). Server restarted with that
  LD path: CONNECT OK, no "Couldn't open libEGL" — but renderer
  init FAILS: "failed to initialise renderer." x2 (log
  virgl-server2.log). Root cause, established by ctypes EGL probe:
  host has NO /dev/dri, no PCI GPU, no DRM modules, no
  /lib/modules at all (kernel 7.0.0-44-generic); Mesa's EGL
  surfaceless init falls back to "surfaceless swrast without DRM"
  and SEGFAULTS there (reproduced 4x, incl. with GALLIUM_DRIVER=
  llvmpipe and LIBGL_ALWAYS_SOFTWARE=1). Without the vendor dir,
  eglGetDisplay fails EGL_BAD_PARAMETER (host has no
  /usr/share/glvnd/egl_vendor.d at all — the rollback removed it).
  gdb 15.1 installed for a backtrace (not yet run).
- --use-glx server (pid 12341, log virgl-server3.log, still alive):
  served the raw GLX probe (legacy ctx, 5 swaps 83.2/7.2/4.5/1.7/
  1.5 ms, err=0x0) — server healthy for simple contexts — but the
  GAME still dies at launch (errno 104 + assertion) and the server
  logs GLXBadFBConfig x2: Xvfb's GLX cannot satisfy the config the
  game requests. --use-glx is a dead end for the game.
- Next for virgl: gdb backtrace of the surfaceless segfault, or the
  --venus (Vulkan/lavapipe) backend — host HAS libvulkan.so.1
  (1.3.275) but no icd.d entries found; check lavapipe presence.
  The virgl route is blocked at server renderer init, independent
  of the (now-cracked) title input stall.

### Repo sync flag
SYNC-WORTHY: this whole section (input breakthrough + revised stall
+ first in-story score) + the Track C cancellation + the "GONE"
retraction + the libEGL/virgl-server findings above. Parent: please
re-sync win32-perf (RESULTS.md + logs incl. cap-env-story60.mkv
scores + shot-env-*.png + game-envrecipe-llvmpipe.log).

## SCORER INTEGRITY FIX — v1 hash scores RETRACTED (2026-11-13 21:21 JST)
ESTABLISHED: tools/score_frames.py v1 (exact MD5 of 160x90 gray, no
magnitude threshold) was noise-inflated. Verification on
cap-base2-story60.mkv: consecutive-frame mean abs diff median 0.001
(0-255 scale), max 0.776; frames 1 s apart byte-identical; the
"19.3 pts/s" came from sub-perceptual dither (max +/-2 LSB over the
whole frame) flipping the hash every frame -- the same failure as the
literal-hash method rejected in Phase 1.1 (settled title 19.92 pts/s).
The 4.03 pts/s (env capture) used the same scorer. **Both v1 numbers
are RETRACTED. KK's eye verdict 「かくかくやん かわらん」 stands
unrefuted.**
### v2 scorer (thresholded MAD)
tools/score_frames.py v2: a frame counts as changed only when the
mean absolute difference of the 160x90 grayscale frames exceeds
epsilon = 0.05. Calibration (/tmp/calib.py, per-frame MAD at 160x90):
| segment | median | p99 | max | frac>0.05 |
| settled title cap-op-virgl.mkv 200-260s (near-static ref) | 0.0000 | 0.0016 | 0.0037 | 0.000 |
| cap-env-story60 (whole) | 0.0000 | 0.1371 | 0.7935 | 0.021 |
| cap-base2-story60 (whole) | 0.0008 | 0.1256 | 0.7740 | 0.028 |
Low dither/drift band tops out ~0.012; event band (dialogue/scene
changes) starts ~0.13 -- the valley is wide, eps=0.05 sits in it with
~4x margin over the static reference. Epsilon sensitivity: at 0.02 /
0.05 / 0.10 the two captures give (0.50/0.42/0.35) and
(0.75/0.57/0.40) pts/s -- ordering and scale stable. Spot-check: the
largest event in env (MAD 0.794) is a real dialogue/scene change
(full-res frame diff confirms 392k px changed between distant
frames); one nuance: the ffmpeg fps=20 filter can shift an event by
+-1 frame when the source timestamps jitter -- per-second aggregation
is unaffected.
### Corrected scores (v2, eps=0.05)
- cap-env-story60.mkv (contended, mid-hallway): **mean 0.417 pts/s,
  median 0.0, 0/60 s >= 10, 35/60 s zero** (scores-v2.json/.csv/.png).
- cap-base2-story60.mkv (contended, story start): **mean 0.567 pts/s,
  median 0.0, 0/60 s >= 10, 34/60 s zero**.
- These are the honest baselines. NOTE: in a dialogue scene the v2
  score is dominated by the AUTO dialogue-advance rate (~1 line per
  2-3 s), so it measures advance rate, not motion smoothness. A
  motion-rich test scene (fades/pans) is still needed for a pure
  smoothness read; KK's eye remains the gate.

## VIRGL SERVER REVIVED — clean-env surfaceless works (2026-11-13 21:1x JST)
ESTABLISHED: virgl_test_server --use-egl-surfaceless in a CLEAN
environment (env -i; only PATH/HOME/LD_LIBRARY_PATH to virgl +
virgl-libs, __EGL_VENDOR_LIBRARY_DIRS) INITIALISES its renderer and
serves the guest: raw GLX probe (probe_glxswap.py, GALLIUM_DRIVER=
virpipe, VTEST_SOCKET_NAME=virgl-test.sock) got legacy ctx + 5 swaps
210.2 / 56.7 / 3.1 / 1.7 / 2.7 ms, err=0x0; server survived
(pid 18234). Earlier "surfaceless segfault / failed to initialise
renderer" failures are therefore NOT a Mesa/host defect: host EGL
surfaceless alone also works (probe /tmp/egl_host_probe.py: llvmpipe
GL 4.5 context, makeCurrent OK). HYPOTHESIS (unbisected): the
predecessor's server inherited a polluted environment from agent
shells that had sourced env files exporting LIBGL_DRIVERS_PATH to the
i386 sysroot (32-bit DRI drivers into a 64-bit process). The exact
offending variable was not bisected -- not needed for progress.
Also ESTABLISHED: the default (no-flag) server mode fails renderer
init (GBM platform, no /dev/dri) -- surfaceless is the required flag.
Next: game-facing server on the standard virgl.sock, then a virgl
story run with the same protocol as the llvmpipe baseline.

## BASELINE 3 — llvmpipe, UNCONTENDED (2026-11-13 21:18-21:26 JST)
Recording line :113 stopped 21:14-21:17, so this run is the first
llvmpipe baseline without recording-line contention (qruppo test line
:117 + light restored crons remain). Same env recipe (log
game-base3-llvmpipe.log, sup 20475). Boot to title ~2.5 min.
NAVIGATION LEARNING: with the game running faster uncontended, a
1.0 s Down hold auto-repeats and overshoots (sequence Down+Return
landed on SYSTEM settings, not LOAD). Shorter holds work: focus ->
Down 1.0 (overshoot) -> Escape -> Return 0.4 s on selected START ->
Chapter 1-1, first line fully displayed. **0.4 s holds are the new
navigation step; verify each step by screenshot.** AUTO on (holdkey
a 0.4 s). Capture logs/cap-base3-story60.mkv (60.0 s, 2,006,641 B).
v2 score: **mean 0.95 pts/s, median 1.0, 0/60 s >= 10, 12/60 s zero**.
tools/analyze_smooth.py (hash fields removed, MAD-only): meaningful
frames 57/1200, longest gap without meaningful change 2.05 s, max
meaningful gap 42 frames. vs contended v2 (0.42 / 0.57): ~2x mean,
but the window differs (story start with fade-in vs mid-hallway) --
do NOT claim contention = 2x without a same-window comparison. The
instance ran ~12 min, 0 crashes, AUTO advancing; killed cleanly for
the virgl run (sup 20475 + game 20480 terminated by pid, recording
line untouched).
Held keys reproduced on a second env-recipe run (base2: title ->
LOAD -> Ch.1-1 -> AUTO, no crash) -- the input fix is not a one-off.

### Repo sync flag (updated)
SYNC-WORTHY: scorer v2 + calibration + corrected scores + virgl
server revival + base3 uncontended baseline. Parent: please re-sync
win32-perf (RESULTS.md + tools/score_frames.py + tools/analyze_smooth.py
+ logs incl. cap-base2/cap-base3 story captures + scores-v2 +
shot-base2/3-*.png).

## VIRGL STORY RUN — game runs in-story on virgl (2026-11-13 21:27-21:3x JST)
Server: virgl_test_server --use-egl-surfaceless, CLEAN env, socket
$WP/virgl.sock (pid 24054, log virgl-server-main.log EMPTY -- no
renderer-init failure across the whole run). Launch:
scripts-env/launch-sanoba-virgl2.sh (env recipe + GALLIUM_DRIVER=
virpipe + VTEST_SOCKET_NAME), log game-virgl8-story.log (only benign
DRI3 warnings, 0 assertions), sup 24075.
ESTABLISHED: the game BOOTS on virgl (title ~2.5 min, correct render),
navigates by held keys (focus -> lone Return: no effect -> Down 0.4 s
arms selection on START -> Return 0.4 s -> Chapter 1-1, first line
fully displayed), AUTO on (holdkey a 0.4 s), story advances
sky -> hallway narration -> character-sprite scene (shot-virgl8-
final.png), 0 crashes. Capture logs/cap-virgl8-story60.mkv (60.0 s,
2,510,246 B).
v2 score (eps=0.05): **mean 2.283 pts/s, median 1.0, 0/60 s >= 10,
25/60 s zero**. Per-second: [4,8,2,0,5,0,1,6,2,0,9,1,1,8,3,0,3,4,
0,1,8,1,0,0,0,0,1,6,0,0,0,5,4,0,4,1,0,7,0,0,0,0,5,0,2,2,0,4,1,0,
0,0,4,5,0,5,6,0,1,7]. analyze_smooth: meaningful frames 137/1200,
longest no-change gap 5.75 s, max meaningful gap 116 frames.
READING (honest): the mean (~2.4x llvmpipe uncontended 0.95) is
driven by BURSTS (4-9 events in one second, then 2-5 fully static
seconds); the MEDIAN is identical (1.0) and zero-seconds / max gap
are WORSE than llvmpipe (25 vs 12 zero-s; 5.75 s vs 2.05 s gap).
**No "virgl is smoother" claim is supported.** The dialogue scene's
v2 score is advance-rate-bound on both stacks; what virgl changes is
the delivery shape (bursty), not the steady rate. The real
smoothness discriminator needs a motion-rich scene (fade/pan):
the settled title is NOT one -- re-scored cap-op-virgl.mkv 150-218 s
with v2: **0.0 pts/s over 68 s** (title sparkles are sub-threshold
at 160x90). Next: capture a scene-transition fade on both stacks and
count distinct intermediate frames per 50 ms; and/or a longer virgl
AUTO run for the stability gate.
Stability VERIFIED: 10 min 16 s uptime at 21:37:55, AUTO advancing
(shot-virgl8-10min.png: two-sprite hallway scene, Hideaki line
「ドMだと！？ なるほど。学内で興奮す」), 0 crashes. AUTO stopped,
instance killed cleanly (sup 24075 + game child by pid). Server left
running on virgl.sock (pid 24054) for the next virgl run.

### Repo sync flag (updated 2)
SYNC-WORTHY: virgl8 story run + bursty-delivery reading + title
v2 re-score (0.0). Parent: please re-sync win32-perf (RESULTS.md +
scripts-env/launch-sanoba-virgl2.sh + logs incl. cap-virgl8-story60
+ scores-v2 + shot-virgl8-*.png + game-virgl8-story.log).

## SETTINGS LEVER — text/AUTO speed to max on virgl (2026-11-13 21:39-21:47 JST)
Run virgl9: same virgl stack as virgl8 (server pid 24054 still
healthy, clean-env surfaceless; launch-sanoba-virgl2.sh, log
game-virgl9-settings.log, sup 26429). Boot to title ~2 min.
Config interaction ESTABLISHED: the SYSTEM config UI responds to
HELD mouse input -- holdclick (0.5 s) switches tabs, and a new
/tmp/drag.py (XTEST press -> stepped motion -> release) drags
sliders. (Title-menu tap-clicks still do not register; config
widgets accept held press/drag.) Exact changes made in the
テキスト tab via the game's own UI (normal play, no file edits):
- テキスト速度 (text display speed): **50 -> 100** (slider max;
  verified value box 100, shot-virgl9-config-textmax.png)
- オート速度 (AUTO speed): **50 -> 100** (slider max; verified
  value box 100, shot-virgl9-config-automax.png)
- オートモードパターン: **ノーマルモード -> スピードモード**
  (help text: advances at the AUTO-speed setting without waiting
  for voice; shot-virgl9-config-final.png)
Before-values were the defaults (50/50/ノーマル) seen on entry
(shot-virgl9-config-text2.png). Settings took effect immediately:
first Ch.1-1 line rendered instantly full-line; AUTO reached the
hallway narration within ~2 s of being switched on.
Capture logs/cap-virgl9-fasttext-story60.mkv (60.0 s, 20 fps,
2,491,089 B), AUTO from hallway narration to the two-sprite
hallway scene. v2 score (eps=0.05): **mean 2.333 pts/s, median
2.0, 0/60 s >= 10, only 2/60 s zero**. analyze_smooth: meaningful
frames 140/1200, longest no-change gap **1.55 s** (max gap 32
frames), gap p95 23 frames.
READING vs virgl8 (defaults, same stack): mean is UNCHANGED
(2.283 -> 2.333) and total meaningful frames are the same
(137 -> 140) -- the settings do NOT create more picture change.
What changes is the DISTRIBUTION: zero-seconds 25 -> 2, median
1.0 -> 2.0, longest freeze 5.75 s -> 1.55 s. ESTABLISHED: with
default settings AUTO delivery was bursty because lines waited
on typewriter + voice-wait; at max settings the same content
arrives as a steady ~2-3 changes/s with no freeze over 1.55 s.
CAVEAT: capture windows differ slightly (virgl8 from the sky
scene's first line; virgl9 from hallway narration, because AUTO
raced ahead before the grab started) -- both are Ch.1-1
dialogue/narration under AUTO; the comparison is distribution-
level, not frame-aligned. NOTE for KK's ideal: dialogue at max
advance still yields only ~2.3 pts/s mean and 0 s >= 10 -- the
10 pts/s ideal is unreachable in dialogue at any setting; it
requires motion (fades/pans), which is the next test.

## FADE / MOTION TEST — virgl vs llvmpipe (2026-11-13 21:48-21:56 JST)
New tool: tools/fade_analyze.py -- native-rate per-frame MAD at
160x90 (eps=0.05 = distinct; at 20 fps capture one slot = 50 ms,
KK's unit) + brightness series; detects sustained-change windows
and reports delivered distinct frames vs stalled (duplicate) slots.
Procedure, identical on both stacks (max text/AUTO settings set
beforehand on virgl; config re-verification on llvmpipe was
derailed by a quit-dialog mishap -- see below): at title, arm
START, start x11grab 20 fps, Return at +1 s, AUTO on after the
black load, capture the scenario start (cap-fade-virgl.mkv 45 s;
cap-fade-llvmpipe.mkv 60 s -- llvmpipe given a longer window for
its slower load; windows are located by content, so the totals
do not bias the comparison). Both captures contain the same two
transitions, verified on extracted frames:
(1) **Fade-in from black** (scenario start, brightness 0 -> ~155):
- virgl: brightness ramp 0->35->67->103->136->157 in 5 big steps
  at ~100 ms cadence (19.70-20.10 s), UI fade steps continuing
  to 20.65 s -- window total **14 distinct / 22 slots**, 8
  stalled, longest internal stall 2 slots.
- llvmpipe: **2 delivered frames total** -- 0->31 at 20.75 s,
  a 0.90 s freeze, then 31->157 in ONE jump (MAD 126). The fade
  is a single intermediate frame plus a jump cut.
(2) **Crossfade sky -> hallway** (brightness ~156 -> 189):
- virgl: 8 blend steps of MAD ~5-6.5 over 22.40-23.20 s
  (156->163->168->171->174->177->181->184->188->189) -- a real
  crossfade ramp; window total 11 distinct / 19 slots.
- llvmpipe: **2 blend steps** -- 156->177 at 34.65 s (MAD 34.6),
  177->189 at 35.65 s (MAD 18.4), 1.0 s apart.
ESTABLISHED: on the motion metric, virgl delivers ~5-8
intermediate frames per fade at ~100 ms cadence (~10 distinct
frames/s during transitions -- the game's own render loop under
QEMU is now the limiter, not the swap); llvmpipe delivers ~2
frames per fade regardless of fade duration, i.e. fades render
as jump cuts. This is the first clean stack discrimination on
KK's actual complaint (カクカク): the dialogue v2 score could
not separate the stacks; the fade test does. Black-load duration
(title -> fade-in) was comparable: ~18 s virgl, ~17 s llvmpipe.
Also recorded: llvmpipe title key handling is treacherous --
0.4 s holds under llvmpipe queue and drain late; a Return sent
with SYSTEM highlighted executed on EXIT (a leftover Down step
landed first) and raised the quit dialog (cancelled with
いいえ). Verify selection by screenshot IMMEDIATELY before
Return on this stack, with a pause for the queue to drain.
Settings persistence across processes: NOT re-verified on
llvmpipe (the config check was the derailed step); functionally
AUTO advanced the story through the hallway into the sprite
scene inside the capture window.

## TRACK B PROBE SALVAGE — interrupted run (2026-11-13 22:02-22:05 JST, recorded 22:4x JST by successor agent)
CONTEXT: the predecessor agent was interrupted at 22:25 JST with this
line idle afterwards; two completed/near-completed probe runs were
never written up. Salvaged here from the raw stdout logs so the work
is not lost. Probe = probes/probe_present.c via scripts/run-probe.sh
(my.env harness, llvmpipe). Columns per probes/probe_present.c:
frame,<phase>,<i>, **clear_us, draw_us, present_us, total_us** (QPC
microseconds). Stats below are median / p95 of the QPC total column
unless noted; wall = phase wall_ms / frames.
### Run 1 — logs/probe_present-trackb2.stdout.log (COMPLETE, DONE)
- A clear+present: wall 205.5 ms/fr; total med 196.6 / p95 291.2;
  present med 196.1 ms (cost is the present call itself).
- B present-only: wall 184.6 ms/fr; total med 188.7 / p95 247.2;
  present med 188.4 ms.
- C clear-only: wall 0.2 ms/fr; total med ~0.0 ms.
- D quad+present: wall 766.2 ms/fr; total med 764.7 / p95 889.6;
  draw med 733.2 ms, present med 0.5 ms (draw-bound).
- A2 (A + Sleep(16)): wall 182.6 ms/fr; total med 189.2 / p95 249.2;
  present med 125.4 ms. Total ~= A total: at ~190 ms/frame a 16 ms
  pace cap is free (the sleep overlaps the present wait).
### Run 2 — logs/probe_present-lp1.stdout.log (LP_NUM_THREADS=1; CUT mid-D by the interruption: A/B/C complete, D has 74/90 frames, no A2, no DONE)
- A clear+present: wall 242.5 ms/fr; total med 234.8 / p95 279.9;
  present med 234.5 ms.
- B present-only: wall 236.6 ms/fr; total med 232.5 / p95 251.3;
  present med 232.5 ms.
- C clear-only: wall 0.1 ms/fr.
- D quad+present (74 frames only): total med 1,126.1 / p95 1,290.3;
  draw med 1,125.9 ms, present med ~0.0 ms.
### What this does and does not establish
- vs the stock llvmpipe probe baselines recorded earlier in this
  file (present-only 373 ms/fr, clear+present 428 ms/fr, textured
  quad+present 1,645 ms/fr): trackb2 is ~1.8-2.2x faster per phase
  (B 185 vs 373; A 205 vs 428; D 766 vs 1,645). **This CANNOT be
  attributed to any named mod or config change**: no variant
  description was recorded with either run (nothing in the logs,
  scripts, or env files names what "trackb2" changed — run-probe.sh
  + my.env is the standard harness and sets no LP_NUM_THREADS), and
  the stock baselines were measured under recording-line contention
  while these runs were uncontended (post-21:17). The base3 game
  baseline showed the same ~2x contention effect. TREATMENT:
  trackb2 is the current UNCONTENDED llvmpipe probe reference,
  not evidence of a Track B mod effect.
- LP_NUM_THREADS=1 vs trackb2 (same evening, same harness, minutes
  apart): lp1 is slower on EVERY phase — A total med +19%,
  B +23%, D +47% (draw-bound). ESTABLISHED (modulo the trackb2
  config caveat above): cutting llvmpipe to one raster thread HURTS
  on this VM; the LP-thread-reduction lever is measured-dead. Track
  B effort goes to partial/dirty-region present, not thread count.
- Noted but unused: probes/probe_present-trackb-base.log (08:29 UTC)
  has present medians ~0.3 ms (not llvmpipe-class) and its D phase
  cut after 1 frame; its config is likewise unrecorded, so it is
  NOT used as a comparison baseline.

## VIRGL SERVER RESTART + VERIFICATION (2026-11-13 22:47-22:52 JST, successor agent)
The 22:25 interruption had killed the virgl server (pid 24054) and
both Xvfb displays. Restarted: Xvfb :116 (pid 6965, log
xvfb116-succ1.log); virgl_test_server --use-egl-surfaceless in the
clean env of the revival section (env -i; LD_LIBRARY_PATH =
virgl/usr/lib + virgl-libs/usr/lib x86_64; __EGL_VENDOR_LIBRARY_DIRS
= virgl-libs 50_mesa.json), socket $WP/virgl.sock, **server pid
6989**, log virgl-server-succ1.log EMPTY (= no renderer-init
failure, the healthy signature). VERIFIED before any game boot with
the raw GLX probe (probes/probe_glxswap.py, DISPLAY :116,
GALLIUM_DRIVER=virpipe, VTEST_SOCKET_NAME=$WP/virgl.sock; log
probe_glxswap-succ1.log): legacy ctx created, 5 swaps **21.2 / 0.8
/ 0.6 / 0.6 / 0.5 ms, all err=0x0**. (The probe script then dies in
its cleanup call glXMakeCurrent(None) — a pre-existing script bug
after the measured section; the measurements are complete and
match the expected signature.)

## VIRGL LONG RUN — 30-min stability + fast-text distribution (2026-11-13 22:36- JST, RUNNING)
Launch: scripts-env/launch-sanoba-virgl2.sh (log
game-virgl10-longrun.log, sup 7085) against the restarted server
(pid 6989). Pre-flight: no other qemu/supervisor instances on this
line; Xvfb :116 fresh (pid 6965). Boot to title ~2.5 min, correct
render, 0 assertions. Navigation (window 0xa00005 via xdotool;
scripts/wininfo.py segfaults on this host — do not use):
focus -> Down 0.4 s (START armed, shot-virgl10-armed.png) ->
Return 0.4 s -> Chapter 1-1 first line (shot-virgl10-story1.png)
-> holdkey a 0.4 s -> AUTO on at **22:40:12 JST**
(shot-virgl10-auto-on.png: hallway already reached, Auto ▶).
### Capture A (first 60 s of AUTO, from story start)
logs/cap-virgl10-long60a.mkv (60.0 s, 1,050,058 B). v2 score:
**mean 2.017 pts/s, median 0.5, 0/60 s >= 10, 30/60 s zero**.
analyze_smooth: meaningful frames 121/1200, longest
no-meaningful-change gap **5.25 s**, gap p95 46 frames.
Per-second: [0,0,3,6,0,0,6,0,1,8,0,0,9,1,0,7,4,0,2,5,2,0,5,7,0,
1,0,0,0,6,2,0,0,0,4,4,0,3,4,0,3,3,0,0,0,0,4,0,1,3,0,5,2,0,0,0,0,
6,4,0].
READING (honest, no claim): this distribution is **virgl8-shaped**
(default settings: mean 2.283, median 1.0, zero 25, gap 5.75 s),
NOT virgl9-shaped (max settings: median 2.0, zero 2, gap 1.55 s).
BUT the windows differ: capture A and virgl8 both start at the
story's first line, while virgl9's steady window was later content
(hallway narration -> sprite scene). Surface tells were mixed:
the first line rendered full-line immediately and AUTO reached
the hallway within ~2 s (both seen in virgl9), yet the score
distribution matches the default-speed run. **Settings
persistence across processes is therefore UNDECIDED from this
window.** Capture B near the 30-min mark (later content,
virgl9-like window) is the discriminator; a direct config-UI
value read is planned after the run.

## FIX-FIRST RULE (KK, 2026-11-13 22:59) — fix list and prep state
GOVERNING RULE: before any measurement run, first apply the fixes
existing evidence already identifies as critical; never spend runs
measuring a configuration known to be suboptimal. Measurement
verifies fixes / resolves genuine unknowns only.
Fix list (from tonight's evidence) and state while virgl10 runs:
1. **Settings settled permanently** — after virgl10 ends, read the
   SYSTEM config UI once to settle whether text 100 / auto 100 /
   speed mode persisted from virgl9; from then on every run starts
   by ensuring those values via the UI. (Pending run end.)
2. **QEMU TCG TB cache** — PREPPED: qemu-i386 10.0.2 supports
   -tb-size (verified -h). New launcher scripts-env/
   launch-sanoba-virgl3.sh = virgl2 with `-tb-size 512` added to
   the game qemu command line (512 chosen: VM has ~6-8 GB RAM and
   ~1.5 effective cores; 1024 risks memory pressure alongside the
   game + server + capture). `-cpu max` verified ALREADY present
   on the virgl2/virgl3 path (it was never missing). All future
   game launches use virgl3.
3. **CSMT on prefix-fresh** — CHECKED: prefix-fresh/user.reg has
   NO Direct3D/csmt entries at all, i.e. the state was Wine
   11.21's unrecorded default. Will be set explicitly ON
   (HKCU\Software\Wine\Direct3D, csmt=1) via the stack after
   virgl10 ends and re-read from user.reg to prove it landed.
4. **Virgl server host-side threading** — server (pid 6989) runs
   with forked worker children (7182, 7268) under the clean env;
   its llvmpipe is a native host process, NOT covered by the
   guest-side LP_NUM_THREADS=1 verdict. Will restart it after
   virgl10 with LP_NUM_THREADS=2 in its environment (VM effective
   cores ~1.5-2; llvmpipe default would take host ncpu and
   oversubscribe), and its CPU will be sampled during the next run.
5. **Capture hygiene** — x11grab is a major CPU consumer on this
   VM (Cave Story line evidence: 21% dropped frames at 30 fps).
   virgl10's captures used libx264 default preset; from the next
   measurement: -preset ultrafast, and ffmpeg's own CPU% sampled
   and stated alongside results.

### VIRGL LONG RUN — completion (2026-11-13 23:10 JST)
Mid-run checkpoints: AUTO+7 min (22:47, shot-virgl10-t10.png:
Wakaba sprite scene, hallway), AUTO+19 min (22:59,
shot-virgl10-t20.png: monochrome-filter narration segment — an
in-game scene effect; UI/text stayed coloured, Auto ▶ on).
**30-MIN STABILITY GATE MET**: AUTO ran 22:40:12 -> 23:10:40 JST
(30.5 min; instance up 34 min from 22:36:25 launch), **0 crashes,
0 assertions**, story advanced sky -> hallway -> sprite scenes ->
monochrome narration -> library two-sprite scene (23:10,
shot-virgl10-t30.png, Nene line 「わかりました。ありがとう……
ございます」).
### Capture B (AUTO minutes ~29-30, later content)
logs/cap-virgl10-long60b.mkv (60.0 s, 1,636,868 B). v2 score:
**mean 1.483 pts/s, median 1.0, 0/60 s >= 10, 15/60 s zero**.
analyze_smooth: meaningful frames 89/1200, longest
no-meaningful-change gap **5.0 s**, gap p95 39 frames.
READING: B sits between virgl8 (zero 25, gap 5.75 s) and virgl9
(zero 2, gap 1.55 s) and does NOT reproduce virgl9's steady
distribution on a later-content window either. Combined with
capture A, the weight of evidence shifts to: **the max-speed
settings did NOT persist into this new process** (virgl9's
distribution was measured in the same process that applied
them). The config-UI read that follows settles it directly.

### FIXES APPLIED (2026-11-13 23:1x-23:3x JST, per fix-first rule)
- **Fix 4 (server threading) DONE**: old server (pid 6989) killed;
  new virgl_test_server started in the same clean env **plus
  LP_NUM_THREADS=2** (pid 12378, log virgl-server-succ2.log EMPTY
  = healthy). Re-verified with the raw GLX probe BEFORE any game
  boot (log probe_glxswap-succ2.log): legacy ctx, swaps 16.7 /
  0.7 / 0.7 / 0.5 / 0.5 ms, err=0x0.
- **Fix 3 (CSMT) DONE, with an environment by-finding**: repeated
  `wine reg add` runs reported success in-session yet the value
  NEVER persisted — a query in a separate invocation (even in the
  same exec call, seconds later) found no key, and user.reg was
  never rewritten. In a SINGLE client session (wine cmd /c) add +
  query agree (csmt 0x1 visible). ESTABLISHED for this stack:
  **short-lived separate wine invocations do not carry registry
  state between them** (each appears to get a fresh in-memory
  registry from the files; the server does not flush changes to
  user.reg across such invocations — while the long-lived game
  session DID update user.reg at its launch). One botched attempt
  also created a stray /prefix-fresh (an env-expansion bug in my
  own command: $WP expanded empty inside a single export
  statement); removed, real prefix untouched (user.reg mtime
  proof). FINAL ROUTE: with no wine processes running, the value
  was written directly into prefix-fresh/user.reg in the file's
  own format — [Software\\Wine\\Direct3D] section, "csmt"=dword:
  00000001 — and VERIFIED: a fresh session's `reg query` reads
  **csmt REG_DWORD 0x1**. CSMT is now explicitly ON and recorded;
  it is no longer an unknown on this prefix.
- Fix 2 (TB cache) is live in launcher virgl3 (see fix-list
  section); fix 1 (settings) is settled next via the config UI
  on the virgl3 boot; fix 5 (capture hygiene) applies to the
  fade measurement that follows.
### Repo sync flag (updated 3)
SYNC-WORTHY: Track B probe salvage + virgl server restart +
virgl10 long run (30-min gate, captures A/B) + fix-first rule +
fixes applied (CSMT by-finding, server LP_NUM_THREADS=2, virgl3
launcher). Parent: please re-sync win32-perf.

### FIX 1 SETTLED — settings do NOT persist (2026-11-13 23:2x JST)
On the virgl3 boot (pid sup 13677, log game-virgl11-fixed.log),
title -> SYSTEM -> テキスト tab read DIRECTLY
(shot-virgl11-config-text2.png): **テキスト速度 = 50,
オート速度 = 50, オートモードパターン = ノーマルモード**.
ESTABLISHED: virgl9's 100/100/speed-mode values were same-process
only and did NOT persist into any later process — virgl10
therefore ran its whole 30 min at DEFAULT speeds (consistent
with its virgl8-shaped capture distributions). STANDING RULE
from here: every run sets text 100 / auto 100 / speed mode via
the SYSTEM UI at start, verified by screenshot of the value
boxes, before anything is measured. (Where the game keeps these
values between processes is unresolved — the env/virgl prefixes
evidently do not carry them; not chased, the UI rule covers it.)

## FADE TEST ON THE FIXED VIRGL STACK (2026-11-13 23:22 JST)
Configuration (all fixes in): launcher virgl3 (**-tb-size 512**,
-cpu max), **CSMT=1** in prefix-fresh, virgl server with
**LP_NUM_THREADS=2**, settings set via UI this session and
screenshot-verified (text 100 / auto 100 / speed mode,
shot-virgl11-config-final.png). Capture per fix 5: x11grab
1280x720@20fps, **-preset ultrafast -crf 23**, 2400 frames
(logs/cap-fade-virgl-fixed.mkv, analysis
cap-fade-virgl-fixed-analysis.json). CPU during the 120 s
window (logs/cpusample-virgl11-fade.txt): **ffmpeg 17.9% of one
core** (the capture's own cost, now measured), **virgl render
worker 23.6%**, server main ~0 — the server has ample headroom;
it is not the bottleneck.
### Windows found (fade_analyze.py, eps 0.05)
- Title -> black fade-out (1.5-2.4 s): 18 distinct / 18 slots,
  **0 stalled**.
- Black -> sky FADE-IN (9.15-10.9 s): **25 distinct / 35 slots,
  10 stalled (28.6%), longest internal stall 2 slots**,
  brightness 0 -> 29.9 -> 53.9 -> 83.3 -> 124.3 -> 156.9 -> 150.
- Baseline (pre-fix virgl, cap-fade-virgl) fade-in: 14 distinct /
  22 slots, 8 stalled (36%), longest stall 2, brightness steps
  ~5 levels. **Fixed stack: distinct 14 -> 25, stalled fraction
  36% -> 28.6%, in-window delivery 12.7 -> 14.3 distinct/s.**
- **Black-load time: ~18 s (baseline, both stacks) -> ~6.8 s**
  (black from 2.4 s to 9.15 s in this capture). The load phase
  itself got ~2.7x faster under the fix bundle.
Attribution note: the bundle (TB cache + CSMT + server threads)
was applied together per the fix-first rule; which element did
what is NOT separated, and no claim is made per-element. The
crossfade window is measured next (AUTO on, second capture) —
this capture had AUTO off, so no crossfade occurred in it.

### Crossfade on the fixed stack (2026-11-13 23:25 JST)
Second capture with AUTO on from the first line
(logs/cap-fade-virgl-fixed2.mkv, 1800 frames, ultrafast;
analysis cap-fade-virgl-fixed2-analysis.json): distinct total
333/1800. The sky -> hallway CROSSFADE is the first window
(0.15-2.6 s, brightness 155.2 -> 181.8): **40 distinct / 49
slots, 9 stalled (18%), longest internal stall 2 slots**.
Baseline virgl crossfade window: 11 distinct / 19 slots
(42% stalled, ~8 blend steps). Distinct density during the
transition: **0.58 -> 0.82**; stalled fraction **42% -> 18%**.
Composition caveat (stated, not hidden): at speed-mode AUTO the
first hallway line renders immediately after the fade, so the
fixed-stack window merges fade + first text render, while the
baseline window (default AUTO pace) is closer to a pure fade.
The like-for-like quantities are the density and stalled
fraction, and both improved, consistent with the fade-in
result. Later story windows in the same capture deliver 12-16
distinct per 0.7-0.9 s line change with 0-3 stalled slots.
CPU over this 95 s: virgl worker 7.2% of one core, guest qemu
2.5% (dialogue-dwell content; ffmpeg's 17.9% was measured on
capture 1 — it had exited before this sampler's last snapshot).
### Fixed-stack fade verdict (both transitions)
vs the recorded pre-fix virgl baseline: fade-in distinct
14 -> 25 with stalled 36% -> 28.6%; crossfade density
0.58 -> 0.82 with stalled 42% -> 18%; black-load 18 s -> 6.8 s.
The fix bundle measurably improved transition delivery on the
virgl stack. KK's eye verdict on the footage remains the final
gate; no claim beyond the numbers. virgl11 instance stopped
after this (AUTO off, killed by pid).

## TRACK B — build feasibility verdict (2026-11-13 23:4x JST)
The salvaged probes closed the cheap levers (LP threads dead;
trackb2 = uncontended baseline, no mod effect attributable), so
Track B's first real mod needs a from-scratch i386 llvmpipe
build of mesa-src. Feasibility checked on this VM:
- meson: ABSENT. ninja: ABSENT. (pip-installable, minor.)
- gcc -m32: FAILS — no 32-bit libc dev files on host
  (Scrt1.o / crti.o missing).
- LLVM: sysroot32 has the i386 libLLVM-20 RUNTIME only — no
  llvm-config, no headers, no component libs. Mesa's llvmpipe
  requires an LLVM dev toolchain; llvm-config for i386 would
  itself be an i386 binary (runnable only via qemu-i386).
- No host GL/libdrm dev packages (dpkg).
VERDICT: **Track B's mod build is BLOCKED on toolchain
excavation** — estimated hours of .deb extraction (libc6-dev,
llvm-20-dev, libdrm-dev, expat/zlib/X11 dev, all i386) plus a
meson cross-file driving an emulated llvm-config, for a mod
whose probe payoff is itself uncertain (the Present cost sits
in the swap/copy path; wined3d GL passes no damage rects, so a
"partial Present" would have to guess damage inside Mesa's
winsys). This is a sequencing decision for KK, not a silent
skip: proceed with the excavation, or park Track B behind the
virgl line (which just posted measured gains on every fade
metric). Recorded as the line's open question in line-state.md.

## KK EYE VERDICT ON THE FIXED-STACK FADE FOOTAGE (2026-11-13 23:34-23:35 JST)
After watching logs/cap-fade-virgl-fixed.mkv and
cap-fade-virgl-fixed2.mkv, KK said at 23:34:
**「だいぶ改善してるな」** — the fade improvement is APPROVED by
his eye; the claim now stands on numbers + verdict (the first
footage he has ever approved; all earlier verdicts were
カクカク / かわらん).
QUALIFICATION at 23:35, immediately after: **「まぁでもまだ
かくかくだね」** — "still jerky, though." Overall smoothness is
NOT accepted; the mission continues. The remaining jerkiness,
per the measured record: fade-in still stalls 28.6% of slots;
dialogue delivery is bursty (dwell + bunching); during
transitions the game's own render loop under QEMU TCG is the
ceiling (~14 distinct/s delivered vs the 20 fps grid).
**Metric priority from here: frame-delivery EVENNESS — fewer
stalled slots, shorter longest-gap — not the mean.**
Scope of the approval: the fade footage. The full success gate
(story footage WITH audio on this stack, judged by his eye) is
still open and is the current task.

## AUDIO ON THE VIRGL ROUTE (2026-11-13 23:3x JST)
Fix-first application of the proven sanoba-audio recipe to the
fixed virgl stack — no experiments, the established route only:
- Perf-line PA daemon: win32-perf/pa-bin PulseAudio, own config
  (pa/default.pa), unix socket pa/native + **TCP 127.0.0.1:47135**,
  **null sink "game" 48000 Hz float32le 2ch** (pid 15978, log
  logs/pulseaudio-virgl.log). Default sink = game.
- Guest: prefix-fresh registry **Audio=pulse** (written directly
  into user.reg [Software\\Wine\\Drivers], same method as CSMT);
  launcher **scripts-env/launch-sanoba-virgl4.sh** = virgl3 +
  PULSE_SERVER=tcp:127.0.0.1:47135, **PULSE_LATENCY_MSEC=750**,
  LD_LIBRARY_PATH to the line's i386 libpulse closure (libs32);
  ALSA null dropped.
- Boot (sup 16040, log game-virgl12-audio.log): title renders,
  0 assertions, and the game registered **Sink Input #2,
  application.name "TVP(KIRIKIRI) Z core / Scripting Platform
  for Win32", float32le 2ch 48000 Hz, 100%** — winepulse is
  connected to the game.
- Pre-flight probe (5 s of game.monitor at the title):
  4.98 s captured, **nonzero 99.8%, peak 0.188, RMS 0.0394** —
  title BGM is ACTUALLY PLAYING through the virtual device
  (same range as the audio line's validated R1 probe:
  peak 0.204, RMS 0.048). Audio path on the virgl route: LIVE.
Delivery-ratio verification on a story capture follows.

## TRACK B — toolchain excavation (2026-11-13 23:3x-23:4x JST, Track B agent)
KK decided 23:32 「両方やり」 — Track B proceeds in parallel.
Workspace: trackb/ (own state file trackb/trackb-state.md).
Excavation result: **the i386 build toolchain WORKS** — the
"hours of .deb excavation" estimate collapsed because (a) the
multilib half was already in i386dev/ (libc6-dev-i386 +
lib32gcc-13-dev extracted) and (b) noble-updates ships the full
i386 dev set at versions matching the guest runtime
(llvm-20-dev:i386 1:20.1.2-0ubuntu1~24.04.3 = libllvm20 in the
guest sysroot).
- Method: sandboxed apt (trackb/apt/, archive.ubuntu.com noble +
  noble-updates, arch amd64+i386, download-only) -> dpkg -x into
  ONE merged devroot trackb/root (573 MB). 70 debs total: i386
  libc6/-dev, linux-libc-dev, libstdc++-13-dev, libgcc-13-dev,
  llvm-20-dev + llvm-20 (tools), libdrm-dev, expat/zlib/zstd dev,
  full X11/xcb dev set, libglvnd-dev, plus matching i386 runtimes.
- pip --target trackb/pytools: meson 1.12.1, ninja 1.13.2, mako.
  bison/flex (amd64) extracted to trackb/host-tools/.
- Compiler: wrappers trackb/bin/{gcc32,g++32} = host gcc 13.3
  -m32 --sysroot=trackb/root + -B into extracted libgcc dirs +
  explicit C++ include/lib paths (gcc's libgcc/C++ dirs are NOT
  sysroot-relative — wrappers are REQUIRED, plain --sysroot
  fails).
- llvm-config: the i386 ELF runs under qemu-i386-static -L root
  and reports devroot-prefixed absolute paths natively (LLVM
  derives its prefix from the executable location), so
  trackb/bin/llvm-config is a qemu-forwarding wrapper — zero
  path rewriting needed. --version 20.1.2, --shared-mode shared,
  --libs core -> -lLLVM-20.
- VERIFIED END-TO-END: C and C++ hello-worlds compile, link,
  and EXECUTE under qemu-i386 (exit codes/output correct).
Remaining before the build: meson cross file (trackb/cross.ini,
written) + a minimal Mesa 25.2.8 configure (swrast only, x11
platform, glvnd) and the unmodified-build parity gate.

### Process note — first A/V capture attempt FAILED on a shell bug (no data)
The first 240 s A/V capture attempt produced NO usable data: a
`cd ... && ... &` precedence bug backgrounded the whole chain,
so only the video ffmpeg inherited the cd; the audio ffmpeg,
the CPU sampler and both xtest keypresses ran in the wrong cwd
and failed on relative paths. The game never left the title
(START stayed armed, verified by screenshot). The resulting
240 s title-only video was deleted as a non-measurement. The
re-run uses absolute paths throughout and an explicitly grouped
subshell (cap-virgl12-story-av2.*). No other line was affected;
the PA daemon and sink-input were uninterrupted.
