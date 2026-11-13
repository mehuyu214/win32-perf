# win32-perf

Rendering-performance investigation for the unmodified 32-bit Windows game
environment built in [win32-env](https://github.com/mehuyu214/win32-env)
(QEMU user-mode + q32sup + 32-bit Wine 11.21 + Mesa 25.2.8 on a GPU-less VM).

**Goal:** get the *Sanoba Witch* trial (Kirikiri engine, unmodified) running
stably at normal speed on a fast software rendering path (softpipe or
equivalent), verified in the actual game — not just in probes.

**Status (2026-11-13): work in progress.** The softpipe boot crash is
characterised at instruction level and one configuration now boots the game
past it (see below); a post-warning white screen is the current blocker.

## Key measured findings

All numbers are from our own masters and live instances; the full record is
[RESULTS.md](RESULTS.md), per-run evidence in `logs/`.

1. **The bottleneck is game-side presentation, not recording.** The shipped
   llvmpipe stack produces ≈0.29 presents/s and ≈0.25 content changes/s in a
   dialogue scene, with freezes up to ~8 s, while the recorder drops nothing.
2. **Present probe (in-guest D3D9, 1280×720, 90 frames/phase):**
   llvmpipe Present-only ≈ 373 ms/frame (scales with pixel count);
   softpipe Present-only ≈ 3.3 ms/frame, Clear+Present ≈ 8.8 ms/frame
   (~48× faster). The cost lives in the llvmpipe path under QEMU
   (the double-JIT tax), not in the EGL→X presentation path.
3. **Timers/clocks are healthy** (QPC/GetTickCount/timeGetTime track wall
   clock; Sleep/WFSO medians accurate). Thread sampling shows the delay
   inside running guest code: 2 of 42 threads do nearly all the work,
   ~always in R state.
4. **softpipe crash, pinpointed by the exception record:** the faulting copy
   in `wined3d_context_gl_copy_bo_address` runs with **EDI = NULL** (a
   512 KiB copy whose destination BO has no CPU address). `REP MOVSB` itself
   is exonerated: an isolation probe passes 13/13 cases including
   texture-sized, page-crossing and misaligned copies. The delivered NT
   exception is `c000001d` (illegal instruction) for what is a memory fault —
   Wine's log shows `segv_handler: Got unexpected trap -1`, i.e. the fault is
   mistranslated somewhere in the QEMU/Wine signal chain.
5. **Why the address is NULL:** the game's log shows the chain
   `wined3d_allocator_chunk_gl_map Failed to map chunk memory` →
   `wined3d_bo_gl_map Failed to map chunk` →
   `wined3d_context_gl_map_bo_address Failed to map bo`.
   WGL probes reproduce the failure family: persistent `BufferStorage`
   buffers fail creation (`GL_OUT_OF_MEMORY`) under shared GL contexts from
   16 MiB up, and mapping an already-mapped shared BO from a second context
   returns NULL with `GL_INVALID_OPERATION (0x502)`. A single-context
   control passes cleanly.
6. **Wine MR !9956** ("wined3d: Check invalid addresses when copying buffer
   objects") covers the same symptom class but a different proximate cause;
   its fix is not applied as a guess (see RESULTS.md).
7. **In-game lever matrix (softpipe):**
   - CSMT off alone: dies at boot with a QEMU-level `signal 11`.
   - `GL_ARB_buffer_storage` masked, CSMT on: crashes 3/3 at `0x1F9FE0C4`.
   - **Mask + CSMT off: boots past the crash point** — the age-warning
     screen renders correctly (`logs/shot-maskcsmt0-t180.png`) — then holds
     a white screen after the warning (≥90 s, zero content change, process
     alive ~29% CPU). Heavy-vs-stuck discrimination and the next fix
     (a wined3d mapping-state patch, or the virgl architecture) are in
     progress.

## Layout

- `RESULTS.md` — the investigation record (established / excluded /
  hypothesis kept separate).
- `probes/` — in-guest micro-benchmarks (D3D9 present probe, REP MOVSB
  isolation, WGL buffer/context experiments, timers) with sources and logs.
- `scripts/` — launch/measurement tooling for this line (thread sampler,
  XDamage/content pollers, click driver).
- `tools/` — this line's `q32sup` variant source and QEMU wrapper injector.
- `logs/` — per-run logs and screenshots cited by RESULTS.md.
- `analyze_frames.py`, `analyze2.py`, `results_frames.jsonl`,
  `results_change.jsonl` — frame-change analysis of published footage.

## Notes

- No game data is included. The game itself is never modified; all work is
  environment-side (QEMU / Wine / Mesa configuration, tooling, and —
  in progress — Wine-side patches), per the win32-env project policy.
- Running the probes requires the win32-env stack (32-bit Wine prefix,
  sysroot, q32sup); see that repository for setup.

## License

Original code and documentation in this repository are under the MIT
License (see [LICENSE](LICENSE)). Third-party components referenced or
required (QEMU, Wine, Mesa) remain under their own licenses.
