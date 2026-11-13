# Track B state (llvmpipe mod line, parallel to virgl line)

status: RUNNING
agent: Track B subagent (spawned 2026-11-13 23:32 JST after KK 「両方やり」)
phase: Toolchain EXCAVATION COMPLETE (devroot trackb/root, wrappers gcc32/g++32/llvm-config verified, C/C++ run under qemu). Waiting for virgl agent's :116 capture (virgl12, 240 s, started ~23:36) to finish before the nice'd Mesa configure+build.
last_update: 2026-11-13 23:40 JST

## Rules in force
- Own workspace trackb/; own prefix under trackb/; display :115 only at game-test stage.
- NEVER touch :116, virgl server/socket, prefix-fresh, other lines' processes.
- Compiles: nice -n 10, -j2 max; check :116 ffmpeg capture before long compiles.
- Results -> RESULTS.md under "TRACK B" headings, immediately.
- Gate: modified build must move in-guest D3D9 probe AND beat llvmpipe fade baseline (2 frames/fade) in game; no data-dropping "fixes".
