# Sanoba audio / performance investigation — RESULTS

Workspace: `~/workspace/sanoba-audio/` (own Xvfb :113, own prefix, own PulseAudio).
Isolation: no other line's processes/displays/prefixes were touched at any point.
Game is always the **unmodified** trial (`sanoba_trial.exe`, copy in `game/sanoba/`).

Metric definitions (canonical tool: `win32-env/tools/delivery_ratio.py`):
- **Delivery ratio** = music_seconds / total_seconds of a capture, where a *gap* is a
  maximal run of exact-0.0 frames ≥5 ms. Duration alone is misleading: a wall-clock-paced
  device inserts digital silence when the producer cannot keep up.
- **Underrun delta** = PulseAudio log lines matching "underrun" during the capture window.

---

## 1. Original A/V glitch — root cause and the PulseAudio pacing fix

Old route (ALSA null/file device): the device consumes samples instantly, so the guest's
audio clock free-ran — measured **164.4 audio-seconds inside a 72.9 s video (2.26×)**,
rate CPU-load-dependent (atempo cannot fix it). The capture was also corrupt in content:
self-similarity scan of the muxed `bgm-sync.wav` found **28 exact-duplicate 0.5 s-window
pairs, 39/145 windows with a near-duplicate within 20 s, all at exactly +1.0 s offset**
(re-fed buffer segments).

Fix built and verified (mission 1):
- **PulseAudio 16.1 daemon, 100 % workspace-resident** in `pa-bin/` (extracted .debs from
  the noble pool incl. universe; system apt was wedged). Custom config `pa/default.pa`:
  private unix socket + TCP 127.0.0.1:47130 (auth-anonymous), `module-null-sink
  sink_name=game rate=48000 format=float32le channels=2`. Clients use
  `PULSE_SERVER=tcp:127.0.0.1:47130`.
- **Guest route (a) winepulse WORKS**: i386 libpulse closure (18 libs, dlopen-probed) in
  `libs32/`; Wine `HKCU\Software\Wine\Drivers` `Audio=pulse` (note: `wine reg add` did
  not persist under this qemu stack — the key was hand-appended to `user.reg` while no
  wineserver ran; winepulse device enumeration keys in `user.reg` prove the connection).
  Log evidence: `pulse_test_connect libpulse protocol version: 35`, sink-input
  `float32le 2ch 48000Hz` from `TVP(KIRIKIRI) Z`.
- Pacing proof (60 s monitor capture): **59.99 audio-s per 60.18 wall-s = 1.00×**,
  0 exact-duplicate pairs, 0/119 near-duplicate windows (vs the old capture above).
- A VM swap wiped all processes mid-session once; the stack was rebuilt fully
  workspace-resident and re-verified (daemon, Xvfb, game, sink-input all restored).

## 2. Quality gate v1 failure — delivery ratio exposes silence-stretching

KK rejected the pacing proof by ear ("ぶぶぶぶ途切れてるし遅い"). He was right:
the 60 s capture contains only **23.54 s of actual music** (delivery ratio **0.39**),
741 silence gaps >5 ms totalling 36.4 s, ~19.6 k underrun log lines. The sink inserts
silence faster than the emulated game can produce samples; the music is time-stretched,
and once the engine's play cursor overtakes its write cursor, chunks are genuinely
**skipped** (KK's later verdict on a de-gapped join proof: 「微妙、なんかちょっととんでる」
— de-gapping is demoted to a diagnostic, never a deliverable method).

### Experiment log (PulseAudio route, title-screen BGM, 60 s captures)

| run | change vs previous | gaps >5 ms | gap total | delivery ratio | underrun Δ | longest gap |
|-----|--------------------|-----------|-----------|----------------|-----------|-------------|
| cap60 (baseline) | tlength 30 ms (Wine default), 1600×900, heavy VM contention | 738 | 36.50 s | **0.39** | ~19.6 k total in log | 0.168 s |
| E1 | `PULSE_LATENCY_MSEC=750` (log-verified: "Requested tlength=750.00 ms") | 58 | 22.14 s | **0.63** | 114 | 0.560 s |
| E2 | + Xvfb 1280×720, `LP_NUM_THREADS=1` | 51 | 19.28 s | **0.68** | 100 | 0.395 s |
| E3 | + renice PA/qemu to −15 → **permission denied** (no CAP_SYS_NICE in this sandbox; `nice -n -15` also denied) — effectively E2 re-run | 49 | 19.17 s | **0.68** | 100 | 0.395 s |
| E4 | tlength 3000 ms | 22 | 32.94 s | **0.43** | 46 | 1.520 s |
| F1 | E4 + game window **unmapped** (xdotool windowunmap; BGM keeps playing) | 22 | 33.28 s | **0.44** | 46 | 1.520 s |

Findings:
- Bigger client buffer (750 ms) reshapes holes (fewer, longer) and improves the ratio,
  but 3000 ms makes it worse again. Buffer size is **not** the bottleneck.
- Waveform of E3 at 100 ms resolution is a metronome: **ON ≈0.90 s / OFF ≈0.30 s**
  (OFF median = max = 0.30 s) at tlength 750 — deterministic, load-independent
  (E2 vs E3 identical numbers at load 11.5 vs 2.4). At tlength 3000 the cycle rescales
  (22 gaps, longest 1.520 s in both E4 and F1) — the cadence tracks the stream-buffer
  geometry, but total delivered fraction does not improve.
- **F1 falsifies the simple "rendering is the bottleneck" hypothesis** for window
  presentation: unmapping the window changed nothing (Kirikiri keeps drawing into its
  surface regardless; presentation was never the cost — the guest's production itself is).

### F2 — non-realtime capture (ALSA file plugin, winealsa → `type file` → null slave)

- Production pace at title (115 s wall window, byte delta): **2.57× realtime**
  (294.9 audio-s of f32le 48 k stereo) — the engine *can* produce much faster than
  realtime when unthrottled.
- BUT content is corrupt the same way: **123 exact-duplicate 0.5 s-window pairs, all at
  exactly +1.0 s offset** (near-dup pairs 163); zero-runs >5 ms only 62 (1.21 s total).
  The file route re-feeds 1-second-old segments whenever the engine loop stalls —
  the same defect family as the original ALSA capture. **F2 rejected as a deliverable
  source** (would need the production stalls themselves fixed).
- Tempo-slope fingerprint check vs `ref48.f32`: **blocked** — 0/148 segment windows
  matched the reference at the distance threshold used (low-band spectral fingerprints);
  slope could not be fitted. Open item (reference provenance / matcher strictness).
- **F2 CLOSED as a deliverable method** (KK's verdict after listening: 「バッファ再送り
  込み」 — buffer re-feeding; parent's independent count: 25/120 exact-duplicate windows
  at +1 s, 99.6 % nonzero samples — no silence insertion, pure re-fed content).

#### F2 gate-v2 — full measured verdict (segment = 115 s wall window at title,
#### bytes 57,563,136–171,076,608 of the session capture; script `scripts/f2gate.py`)

| gate item | measured value |
|---|---|
| format | float32le, stereo, 48,000 Hz (engine-negotiated); 14,155,776 frames = **294.91 s** of content from 115 wall-s → production pace **2.57×** |
| levels | peak 0.2042, RMS 0.0464 — sane, matches the BGM's known level |
| silence insertion | exact-zero frames **0.41 %** (99.59 % nonzero); 62 zero-runs >5 ms totalling 1.21 s, scattered across the timeline — no systematic padding |
| **duplication** | **123 of 589 windows (20.9 %) are bit-exact copies of the window exactly 1.0 s earlier** (waveform MD5 equality, not spectral similarity); involved regions span 2.0 s → 294.5 s — **pervasive, not localized** |
| omission | not directly countable without a trusted reference (see tempo row); structurally implied: with the play cursor advancing on schedule while writes re-feed old buffers, later content is displaced/skipped — the same skip KK heard on the realtime path |
| tempo / pitch vs ref | **indeterminate**: 0/589 windows fingerprint-match `ref48.f32` **or** `ref44.f32` under two independent methods (low-band FFT fingerprints; 32-band log fingerprints, threshold 0.10, median min-distance 0.42) → the references do not correspond to the in-game title BGM; slope cannot be fitted against them |
| sync relationship | none by construction: clockless production runs 2.57× ahead of the screen; alignable only by scene markers, and the re-feeding destroys even that locally |

**Verdict: FAIL.** The deciding item is duplication — systematic buffer re-feeding
across the whole timeline (KK's 「バッファ再送り込み」 confirmed numerically).
F2 is closed; no de-gapping/repair is permitted on it (content is repeated *and*
displaced, repair is impossible in principle).

**Unifying model (agreed with KK/parent):** both capture families fail from one root —
*the game's audio production cadence under emulation cannot sustain realtime.* The
realtime (PulseAudio) path pads the shortfall with silence and skips chunks once the
play cursor overtakes the write cursor; the clockless (file-plugin) path re-feeds
buffers instead. No capture-method variant can fix this; the only valid fix is raising
production itself — investigation tracks A–E below. All effort goes there.

### In-game settings state (for the queued BGM clips)

Applied on the サウンド screen and verified by screenshots (`logs/snd*.png`):
SE（ゲーム）0, SE（システム）0, BGV（通常）0, BGV（H）0, **all 11 individual voices OFF**
(name list dimmed + OFF toggle verified per character), BGM 50, マスター 100.
VOICE master slider and ムービー音量 resisted synthetic clicks for a long time (the
config UI lands events ≈+25 px below aim in the upper rows — found empirically);
last confirmed values before the quality pivot: VOICE 2, ムービー 8 (near-zero;
all voices are OFF individually regardless). To be re-verified before recording.

## 3. Performance investigation (formal mission, 2026-11-12 23:39)

Unverified factors prioritised; every setting's effect verified in the log/process
state before its numbers count. One variable per run. Bench harness:
`win32-env/tools/launch2.sh` (own q32sup build `q32sup-mine`, own wrap dir `mywrap/`,
Q32_QEMU selectable per run), `win32-env/tools/fpsprobe.sh`.

### Track A — QEMU TCG
- **`-tb-size` does not exist in Linux user-mode qemu**: both 8.2.2-static and 10.0.2
  exit rc=1 with `qemu: unknown option 'tb-size'`. The rung is closed — no TB tuning
  is available on this route.
- Version micro-bench (guest python3.12 float loop, 10 guest-s, host wall ≈11.8 s each):
  qemu-i386-static **8.2.2: 90,000 ops/s**; qemu-i386 **10.0.2: 92,000 ops/s (+2 %)**.
  Note the process topology: the first Wine process runs under qemu10 (10.0.2) while
  **child processes — including the game itself — run under 8.2.2-static** through the
  q32sup wrapper scripts. "10.0.2 everywhere" is testable via `Q32_QEMU` (ladder R2).

### Track B — q32sup supervisor cost
- Source audit (`win32-env/src/q32sup.c`): ptrace+seccomp interception fires **only on
  execve** of 32-bit ELFs, which it reroutes through generated wrapper scripts
  (`exec <QEMU> -cpu max -L <sysroot> <target>`). No per-syscall steady-state tracing.
- Micro-bench: same guest python loop under `q32sup + qemu10` = **90,000 ops/s** vs
  92,000 plain — **steady-state overhead ≈ 0 (within ±2 % noise)**.
- A "without supervisor" game run is **impossible in this sandbox**, not merely
  untested: without interception, qemu passes child execve to the host kernel, where
  the 32-bit transition is disabled and children die (win32-env
  `docs/TROUBLESHOOTING.md`). The supervisor is load-bearing infrastructure.

### Track E — VM CPU limits
- 4 vCPUs visible (`nproc`, /proc/cpuinfo). cgroup v2 is mounted but the visible node
  has **no `cpu.max`/`cpu.weight` files and `cpu.stat` carries no throttling counters**
  (only usage counters) — the ≈1.5-core effective limit (runtime header
  `cell_shared_cpus=1.500`, 6 GiB) is enforced outside this namespace's view, so
  throttling cannot be read from cpu.stat here; it must be inferred from scheduling
  behaviour. Displayed cores (4) overstate usable compute by ≈2.7×.

### Ladder (in progress)

Base config: driver=pulse, `PULSE_LATENCY_MSEC=750`, LP_NUM_THREADS=1, Xvfb 1280×720,
PA via TCP, wrappers→qemu 8.2.2-static, WINEDEBUG=-all, logs→/dev/null
(game log at -all was 1,314 bytes — logging overhead already negligible).

| run | variable | fps (title) | delivery ratio | underrun Δ | notes |
|-----|----------|-------------|----------------|-----------|-------|
| R1 attempt 1 | base | — | 0.000 (invalid) | 0 | **Harness failure, not a game measurement.** My self-built `q32sup-mine` derived the sysroot from its own path (it lives in `sanoba-audio/`, so generated wrappers used `-L /home/hatch/workspace/sysroot32/root` — nonexistent); the guest died at exec (`/lib/ld-linux.so.2: could not open`), no sink-input ever appeared, and parec recorded 56.29 s of idle-sink silence (that file was later overwritten by the rerun before it could be preserved; its stats are recorded here). **Fix:** `launch2.sh` now exports `Q32_SYSROOT=$VT/sysroot32/root`; stale wrappers deleted and regenerated content verified. A second invalid capture (`cap-r1-invalid2.raw`, 60.23 s of zeros) came from a re-run launched while no game instance was alive (the first instance had been killed by a `process.kill` tree teardown of its bench session — see operational lessons). Both are labelled INVALID; neither is a game measurement. |
| **R1 final** | base (8.2.2 wrappers, LP=1, PLM=750, TCP, 1280×720) | 1.00 distinct/s (title content-change rate; grab 20 fps) | **1.000** | **0** | **PASS — first fully clean run. KK EAR-TEST: 「最高だね」 (2026-11-13 00:42, on the mp3 of this capture) — gate v2's ear-test item is satisfied for the base config; the realtime PulseAudio route is validated end-to-end (numbers + ears).** Pre-flight: sink-input present; probe 5.80 audio-s, nonzero 1.000, peak 0.204, RMS 0.048. Timed window 61.02 s wall → 59.77 s capture, 0 gap runs. Game CPU during window ≈17 % of one core total (top thread 701 ticks = 7.0 s). Video verify: 10 s/200 frames valid. Conditions: VM load 0.40 (compat line frozen, VM effectively exclusive). **Interpretation: the 0.68 plateau of E2/E3 was contention from the other line's then-running Geminism process (~70–90 % CPU), not an intrinsic ceiling of this stack.** Artifacts: `logs/run-r1.log`, `logs/cap-r1.raw`, `logs/r1-vid.mp4`. |
| R2 | wrappers → qemu 10.0.2 | 1.00 | **1.000** | **0** | No measurable difference vs R1 (top thread 735 ticks vs 701; pre-flight PASS, probe 5.77 s, nonzero 1.000). QEMU version is not a lever on this workload (micro-bench said +2 %). Artifacts: `logs/run-r2.log`, `logs/cap-r2.raw`. |
| R3 | LP_NUM_THREADS=2 | 1.00 | **1.000** | **0** | Identical profile to R1 (top thread 716 ticks). llvmpipe thread count is not a lever at title-screen load. Artifacts: `logs/run-r3.log`, `logs/cap-r3.raw`. |
| R4 | LP_NUM_THREADS=4 | 1.00 | **1.000** | **0** | Identical again (top thread 711 ticks). LP thread count 1/2/4 makes no difference at this load. Artifacts: `logs/run-r4.log`, `logs/cap-r4.raw`. |
| R5 | PA transport unix socket | 1.00 | **1.000** | **0** | Transport verified in effect (launch env `PS=unix:…/pa/native`; the guest had no other server string, stream live, probe PASS). No measurable difference vs TCP at this load. Artifacts: `logs/run-r5.log`, `logs/cap-r5.raw`. |
| R6 | vblank_mode=3 | 1.00 | **1.000** | **0** | No measurable change (CPU profile and content-change rate identical). Whether Mesa honoured the setting is not independently observable here — there is no excess frame rate to throttle at title (content changes ~1/s). Artifacts: `logs/run-r6.log`, `logs/cap-r6.raw`. |

**Ladder conclusion:** on an exclusive VM, *every* rung delivers 1.000 / 0 underruns.
The differentiators (qemu version, LP threads, transport, vblank) are all inert at
this load. The base config stands as the reference configuration; the one variable
that ever mattered was **VM contention** (plus the 750 ms stream buffer vs the 30 ms
default under contention).

### Comparison matrix (base config, one instance, title, 60 s windows, 2026-11-13 00:46–00:52)

| condition | game CPU (ticks/60 s) | recording fps | content-change rate | delivery ratio | underrun Δ |
|---|---|---|---|---|---|
| M1 game only | 1038 (≈17 % of 1 core) | — (not measurable without a capture channel) | — | — | — |
| M2 game + video (x11grab 20 fps ultrafast) | 1104 | 20/1 delivered (1200 frames) | 0.23 distinct/s (60 s window) | — | — |
| M3 game + audio | 985 | — | — | **0.829** | **52** |
| M4 game + video + audio | 1092 | ≈19.98 delivered (1199 frames) | 0.23 distinct/s | **0.886** | **38** |

**M3/M4 shortfall — stated plainly:** in this session the audio did NOT hold the
R1–R6 standard (gaps 26 runs/10.18 s in M3, 18 runs/7.04 s in M4; longest gap
0.395 s — the old metronome signature). Differences vs the clean R-runs: session
start load 1.47 (vs 0.40–0.63), and M3 ran ~6–7 min after boot, after M2's 60 s
x264 encode in the same session. Two candidate causes: (a) external contention
returned during the matrix windows; (b) session-age/order effect (TCG translation
cache pressure growing over minutes). **Until it is explained and a same-session
M4 ≥0.98 is measured, the Policy B clips remain locked** (per KK's condition:
clips unlock only if M4 holds clean). Artifacts: `logs/run-matrix.log`,
`logs/cap-m3.raw`, `logs/cap-m4.raw`, `logs/m2-vid.mp4`, `logs/m4-vid.mp4`.

**Diagnostic follow-up (partial, 2026-11-13 00:52–00:55):** fresh base instance;
audio window at ~4 min session age measured **1.000 / underrun Δ0** (top-process
snapshot: the game itself was the only heavy process). The run's later windows
were lost when the bench shell was terminated (SIGTERM), so the age/order
question stays open; the deciding experiment is the alternating M3/M4 repeat
under the VM quiet protocol (Phase 4). Artifacts: `logs/run-diag.log`,
`logs/cap-dA.raw`.

**Facts / causes / unverified — formal separation:** see
`win32-env/docs/PERFORMANCE.md` (committed). Short form — *measured:* §2/§3
tables above; *estimated cause:* VM CPU contention is the leading hypothesis for
the E-era plateau and the matrix shortfall (correlational evidence only; no
specific job is named as the proven culprit); *unverified:* tempo slope vs the
parent's references, true render fps, in-game `-cpu` sensitivity, session-age
effect.

## 4. Phase 3 — quiet-protocol M4 retest + M3/M4 delta (2026-11-13, continuation agent)

Context: VM restarted ~00:55 JST; previous game instance died. Quiet protocol
stayed ACTIVE across the restart (state file intact; jobs vn-arcade-dev-loop,
bluesky-continuous-posting, agentic-feature-tour paused; restore due 06:57 JST).
m4q1/m4q2 (previous agent) = pre-flight failures (0-byte files, no sink-input) —
logged as such, never overwritten; numbering continues at m4q3.
Stack relaunched 01:02–01:04 JST: Xvfb :113 (1280x720), workspace PulseAudio
(sink "game" f32le/48k), game via win32-env/tools/launch2.sh, base config
(wrappers→qemu 8.2.2-static, LP_NUM_THREADS=1, PULSE_LATENCY_MSEC=750, TCP).
Title screen screenshot-verified (`logs/relaunch-title.png`); sink-input live
(protocol-native.c, f32le 2ch 48 kHz). Window sequence interleaves M4/M3 on this
one instance for the Phase-4 delta: m4q3, m3q1, m4q4, m3q2, m4q5.

### Phase 3 interim — concurrency incident + first valid windows (01:04–01:07 JST)

**Incident (disclosed):** the previous agent's `m4q-driver.sh` (detached, PID 6308)
was still alive and running its own window sequence in parallel with this agent.
The two harnesses share `pkill -f "parec -d game.monitor"`, so overlapping windows
killed each other's captures. The driver was terminated (this line's own process;
game/PA/Xvfb untouched). Consequences, per the run-m4q.log timeline:
- *driver m4q3* (16:01:24 UTC): pre-flight FAIL (game still booting); its idle-sink
  silence file `cap-m4q3.raw` was later truncated/rewritten by this agent's m4q3
  window — an overwrite of an invalid no-data artifact whose stats are preserved
  in `logs/run-m4q.log`. Recorded as a discipline breach; numbering discipline
  tightened (see below).
- *driver m4a* (16:04:11): pre-flight PASS, but its parec was killed at 18.57 s by
  this agent's m4q3 pre-flight → **INVALID (truncated)**; content of the 18.57 s
  was clean (1.000, 0 gaps); its video completed (1200 frames).
- *agent m4q3* (16:04:31): pre-flight PASS; parec killed at 39.51 s by m4a's
  teardown pkill → **INVALID as a 60 s window (truncated)**; captured content
  clean (1.000, 0 gaps, underrun Δ0); video complete (1199 frames).
- *driver m3a* (16:02:47): pre-flight PASS (probe 4.81 s, nonzero 0.872, peak
  0.198); full window 59.79 s, **delivery 1.000, gaps 0, underrun Δ0 — VALID M3**.
- *driver m3b* (16:05:36): pre-flight PASS (probe shortened to 1.88 s by the
  racing teardown pkill; nonzero 1.000, peak 0.188); full window 59.79 s,
  **delivery 1.000, gaps 0, underrun Δ0 — VALID M3**.
Note: `m4window.sh`'s game_cpu_ticks read 0 in all these windows (its pgrep
matched the supervisor PID) — CPU figures for Phase 3 windows are taken from
/proc/<game-qemu-pid>/stat snapshots by the coordinating agent instead.
Remaining M4 windows run strictly one-at-a-time under this agent only:
m4q4, m3q1 (delta interleave), m4q5, m4q6 — all fresh files.
- *agent m4q4* (16:07:43 UTC, M4): pre-flight PASS (probe 4.68 s, nonzero 1.000,
  peak 0.197). **FULL PASS: 59.78 s, delivery 1.000, gaps 0, underrun Δ0,
  exact-dup pairs 0, near-dup 0/119 windows, silent windows 0; video 1200
  frames/60.000 s; A/V start offset 0.002 s; game CPU 1248 ticks (coordinator
  snapshot, pid 6860, incl. probe/teardown); load at start 1.37.** VALID M4 #1.
  (Harness note: m4window's analyze.py grep pattern misses the underscore
  format `exact_dup_pairs` — duplicate figures here are from a direct
  `scripts/analyze.py` run.)
- *agent m3q1* (16:09:04 UTC, M3): pre-flight PASS (probe 4.76 s, nonzero 1.000,
  peak 0.204). **FULL PASS: 59.76 s, delivery 1.000, gaps 0, underrun Δ0,
  exact-dup 0, near-dup 0; game CPU 1178 ticks; load at start 1.89.** VALID M3 #3.
- *agent m4q5* (16:10:16 UTC, M4): pre-flight PASS (probe 4.72 s, nonzero 1.000,
  peak 0.204). **FULL PASS: 59.76 s, delivery 1.000, gaps 0, underrun Δ0,
  exact-dup 0, near-dup 0; video 1200 frames/60.000 s; A/V start offset 0.002 s;
  game CPU 1248 ticks; load at start 2.36.** VALID M4 #2 — reproducibility met
  (2 clean M4 windows, plus 3 clean M3 windows this session).
- *agent m4q6* (16:11:32 UTC, M4): pre-flight PASS (probe 5.12 s, nonzero 1.000,
  peak 0.204). **FULL PASS: 59.75 s, delivery 1.000, gaps 0, underrun Δ0,
  exact-dup 0, near-dup 0; video 1200 frames/60.000 s; A/V start offset 0.002 s;
  game CPU 1214 ticks; load at start 2.27.** VALID M4 #3.

### Phase 3 summary — quiet-M4 verdict (2026-11-13 01:13 JST)

Quiet-protocol windows on one instance (launched 16:01:57 UTC), interleaved:
M3 = m3a 1.000, m3b 1.000, m3q1 1.000 (3/3 clean, all gaps 0, underrun Δ0,
exact-dup 0). M4 = m4q4 1.000, m4q5 1.000, m4q6 1.000 (3/3 clean full windows,
video 1200 frames each, A/V start offset 0.002 s). Plus two truncated-invalid
M4 attempts (m4a 18.57 s, m4q3 39.51 s — harness race, content clean).
**Gate v2 (audio): PASS with reproducibility** for both M3 and M4 under the
quiet protocol. Tempo: captures are wall-clock-paced monitor recordings of a
realtime sink; 59.75–59.79 audio-s per 60 s window (pace 1.00×); slope vs the
parent's reference files remains indeterminate (references do not match this
BGM — see F2 verdict). Session age at windows: 1–11 min — no age effect
observed in this range.

### Phase 4 — M3 vs M4 delta verdict

FACTS: (i) original matrix (uncontrolled background, start load 1.47, n=1 per
condition): M3 0.829, M4 0.886. (ii) quiet protocol, interleaved, same instance:
M3 3/3 = 1.000, M4 3/3 = 1.000 — no difference in delivery, gaps, underruns,
duplicates, or game CPU (M3 1178 ticks; M4 1214–1248 ticks, the excess ≈ the
known x11grab cost). CONCLUSION: the matrix-era M4>M3 ordering was **not a real
effect of recording**; with the background term removed the conditions are
indistinguishable. The 0.829 vs 0.886 difference is consistent with run-to-run
variance of two degraded windows under a fluctuating background (both windows
were short of clean; the later one happened to be less short). ESTIMATE (not
proven): the shared cause of both shortfalls was CPU contention from unmanaged
background fluctuation during the matrix session — the same mechanism as the
E-series plateau; no specific job is identified as culprit. No mechanism by
which adding x264 encoding would improve game audio production exists or is
evidenced. **Policy B clips are UNLOCKED** (quiet-M4 passes gate v2 with
reproducibility, per KK's condition).

### Phase 5 pre-work — in-game sound settings re-verified (01:15–01:29 JST)

**Settings had NOT persisted from the earlier session**: on entering SYSTEM →
サウンド this session, values were the defaults (VOICE 100, SE 80/50, BGV 70/70,
ムービー 50, 綾地寧々 voice ON). All values were therefore set fresh in this
session (drag technique; track clicks do not move these sliders):
マスター 100, BGM 50, SE（ゲーム）0, SE（システム）0, BGV（通常）0, BGV（H）0,
**ムービー 0 and VOICE master 0 — both open items resolved by direct setting**
(screenshots `logs/cfg-snd-test3.png`, `logs/cfg-snd-final.png`). All 11
individual voices set OFF and then **verified per character** by re-selecting
each radio and pixel-classifying the OFF button (RGB (144,115,231) purple =
selected, identical for all 11; frames in `logs/voice-vfy/v1..v11.png`).
Note for the record: the earlier accidental title click started the story
(Chapter 1-1) before these settings were applied — no recording was running;
no deliverable is affected. Settings persistence across leaving the config
screen is re-checked on the サウンド screen immediately before Clip 1.

### Phase 5' — seg01 gate analysis (01:37–01:41 JST)

seg01 (480 s tnav: title → SYSTEM/サウンド → title → START → Ch.1-1) recorded
and muxed (`full/seg01.mp4`, 480.0 s). Raw gate: ratio 0.929, 21 gap runs
(35.82 s), underrun Δ42, analyze.py exact-dup pairs 1326. Decomposition:
- The 27.97 s gap at t=45.1 is GENUINE scene silence (RMS-verified quiet range
  46–73 s: START transition + the music-less opening of Ch.1-1).
- All 1326 "exact-dup pairs" are silence-window artifacts: restricted to
  music-active windows, exact-dups at +1.0 s = **0** and windows with any later
  exact dup = **0** (953 music windows). No re-feeding.
- The real defect: **20 holes of exactly 0.395 s** (the known buffer quantum)
  spread over the segment (~2.4/min), i.e. production dropouts — defect-gap
  fraction 1.65 % of the music-active span; full-span ratio excluding the
  scene silence = 0.984. seg01 therefore does NOT meet the strict gate
  (gaps <1 %) despite no duplication and correct tempo.
- Control: a 60 s audio window on the same instance immediately after
  (age ~39 min, story BGM, `cap-age1.raw`) measured **1.000 / 0 gaps / Δ0** —
  session age alone does not explain the holes; they are intermittent
  production shortfalls during long story-phase recording (story render load
  ≈69 % CPU vs ≈26 % at title). seg02 (same director, story phase) is being
  recorded as the deciding comparison.

### Phase 5'' — continuous take prep findings (02:10–02:20 JST)

- During AUTO playback the engine IGNORES menu invocations (System button
  click and F8 both no-ops, dialogue clicks still advance). Stop AUTO with
  the A key first; menus then open normally. Mid-take quick saves therefore
  run: A (stop) -> F11 -> はい (537,413) -> A (resume). Quick save verified
  end-to-end (data_quick_01.bmp + datasc/datasu written 17:07:09 UTC).
- Config tab memory: SYSTEM reopens on the LAST used tab; a single tab click
  may not switch (focus quirk) — click the tab twice.
- Continuous take attempt 1 (17:08:35 UTC start) aborted at ~2 min: head
  settings visit showed the shortcut-list tab instead of サウンド.
  Attempt-1 split files kept; take restarted as attempt 2.
