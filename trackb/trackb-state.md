# Track B state (llvmpipe mod line, parallel to virgl line)

status: RUNNING
agent: Track B subagent (spawned 2026-11-13 23:32 JST after KK 「両方やり」)
phase: BLOCKED — VM write gate (since ~23:48 JST, still hard-down at 00:17: gcc temp-file close denied on every probe 00:02-00:17; dpkg -x payloads zero; brief flaps only). A ninja retry-grind also died with an agent-runtime restart at 00:16 having made zero progress. Build dir verified INTACT after all incidents (99 .o, none zero-size). Track B agent standing down; resume when exec writes recover.
last_update: 2026-11-14 00:19 JST

## RESUME SEQUENCE (exact, in order)
1. Probe: `trackb/bin/gcc32 /tmp/h.c -o /tmp/h32` (recreate /tmp/h.c first) must produce a ~15 KB ELF. If "error closing ... Operation not permitted" -> still gated, wait.
2. Build #1: env per trackb/configure-mesa.sh exports, then `nice -n 10 trackb/pytools/bin/ninja -C trackb/build -j1` (resumes at 161/1122). Then `DESTDIR=trackb/stage1 ninja -C trackb/build install`.
3. guestroot: rm -rf trackb/guestroot; dpkg -x ALL trackb/debs/*.deb into it; VERIFY zero .so count == 0 and libc/libgallium/libLLVM sizes real; `ldconfig -r trackb/guestroot`. (guestroot currently holds a corrupt 1.4 MB extraction — discard it.)
4. `sh trackb/overlay-mesa.sh trackb/stage1` (overlays built mesa set, verifies sizes).
5. Prefix boot on :115 (Xvfb :115 must be started if down): `timeout 900 trackb/run-wine.sh wineboot --init` then wait for wineserver exit.
6. PROBE PARITY (stock build): `timeout 900 trackb/run-wine.sh 'Z:\home\hatch\workspace\win32-perf\probes\probe_present.exe'` — compare A/B/D vs recorded uncontended stock (A 205.5 / B 184.6 / D 766.2 ms/fr).
7. MOD BUILD: configure trackb/build-mod from trackb/src-mod (same options as configure-mesa.sh, different source/build dirs), build, install to stage2, overlay, re-run probe with MESA_XLIB_DAMAGE unset(=on) and =0 (stock path in same .so) — gate: B phase must move strongly; then game fade test on :115 vs llvmpipe baseline (2 frames/fade).
Env notes: check :116 ffmpeg before compiles (contention); compiles nice -n 10 -j1 (RAM ~400 MB free typical, swapon not permitted).

## Rules in force
- Own workspace trackb/; own prefix under trackb/; display :115 only at game-test stage.
- NEVER touch :116, virgl server/socket, prefix-fresh, other lines' processes.
- Compiles: nice -n 10, -j2 max; check :116 ffmpeg capture before long compiles.
- Results -> RESULTS.md under "TRACK B" headings, immediately.
- Gate: modified build must move in-guest D3D9 probe AND beat llvmpipe fade baseline (2 frames/fade) in game; no data-dropping "fixes".
