# Track B state (llvmpipe mod line, parallel to virgl line)

status: RUNNING
agent: Track B successor agent (resumed 2026-11-14 after VM replacement)
phase: BUILD #1 (stock Mesa 25.2.8) — resumed after coordination pause; [364/962] and advancing (verified 00:53 JST).
last_update: 2026-11-14 00:53 JST
pause_window: PAUSED-BY-COORDINATION 2026-11-14 ~00:41–00:53 JST (~12 min). Build SIGSTOPped at [361/962]; zero compile CPU while the virgl line recorded the listen-paced deliverable (logs/virgl13-story-listen.mp4, 299.93 s; probe 3 delivery 0.969 — the pause created the exclusivity window). Released 00:52 by main chat; SIGCONT -4469 -14582 at 00:53, verified ninja SN + cc1 RN and log [361]->[364]. Smoke-probe A/B/C numbers from the paused run are contention-poisoned and must not be quoted as parity numbers (see RESULTS.md).

## RESUME SEQUENCE (exact, in order)
1. Probe: `trackb/bin/gcc32 /tmp/h.c -o /tmp/h32` — DONE, PASS (14,908 B ELF32).
2. Build #1: env per trackb/configure-mesa.sh exports, then `nice -n 10 trackb/pytools/bin/ninja -C trackb/build -j1` — RUNNING, resumed at [361/962]. Then `DESTDIR=trackb/stage1 ninja -C trackb/build install`.
3. guestroot: DONE — rm -rf + dpkg -x ALL trackb/debs/*.deb (pool repaired: 28 zero-byte debs re-downloaded + mesa runtime set added, 86 debs via sandboxed apt; mesa = 25.2.8-0ubuntu0.24.04.4). Verified: 0 failures, 781 MB, 0 zero-size .so, libgallium 45,575,628 B, ldconfig rc=0. PLUS usrmerge symlinks added (lib->usr/lib, bin->usr/bin) — without them qemu cannot open /lib/ld-linux.so.2.
4. `sh trackb/overlay-mesa.sh trackb/stage1` (overlays built mesa set, verifies sizes).
5. Prefix boot on :115: DONE — wineboot --init rc=0 (~5.3 min), trackb/prefix populated, wineserver exited. Xvfb :115 up via systemd-run (unit xvfb115).
6. PROBE PARITY (stock build): `timeout 900 trackb/run-wine.sh 'Z:\home\hatch\workspace\win32-perf\probes\probe_present.exe'` — compare A/B/D vs recorded uncontended stock (A 205.5 / B 184.6 / D 766.2 ms/fr; source probes/probe_present-trackb2.log, wall_ms/90 frames).
7. MOD BUILD: configure trackb/build-mod from trackb/src-mod (same options as configure-mesa.sh, different source/build dirs), build, install to stage2, overlay, re-run probe with MESA_XLIB_DAMAGE unset(=on) and =0 (stock path in same .so) — gate: B phase must move strongly; then game fade test on :115 vs llvmpipe baseline (2 frames/fade).
Env notes: check :116 ffmpeg before compiles (contention); compiles nice -n 10 -j1.

## Rules in force
- Own workspace trackb/; own prefix under trackb/; display :115 only at game-test stage.
- NEVER touch :116, virgl server/socket, prefix-fresh, other lines' processes.
- Compiles: nice -n 10, -j2 max; check :116 ffmpeg capture before long compiles.
- Results -> RESULTS.md under "TRACK B" headings, immediately.
- Gate: modified build must move in-guest D3D9 probe AND beat llvmpipe fade baseline (2 frames/fade) in game; no data-dropping "fixes".
