# Track B state (llvmpipe mod line, parallel to virgl line)

status: DONE — gate failed on evidence; line closed (see RESULTS.md "TRACK B — DISCRIMINATOR + FINAL GATE VERDICT")
agent: Track B successor agent
phase: CLOSED. Mission sequence executed in full: toolchain probe PASS -> build #1 (stock Mesa 25.2.8) DONE -> parity gate PASS (functional: probe all phases + Sanoba title on self-built stock, logs/shot-stockbuild-title.png; numeric parity indeterminate under contention) -> mod v1 (xlib winsys) caught as NO-OP (never compiled in this config) -> mod v2 (GLX drisw damage-diff) built/verified, probe gate NO MOVEMENT -> mod v3 (EGL platform_x11 damage-diff) built/verified, probe gate NO MOVEMENT -> discriminator: raw GLX swaps on this stack are ~2-8 ms (mod off: 4.2/2.2/4.3/2.0 ms steady) vs the D3D9 probe's ~250 ms/fr Present. ESTABLISHED: Present cost is guest GL pipeline work (wined3d present + deferred llvmpipe rasterization under the QEMU double-JIT), NOT the X copy. Partial Present is a dead lever here; the fade test was not run (same machinery, proven pipeline-bound). Mods remain in trackb/src-mod, env-gated by MESA_XLIB_DAMAGE (unset=on, =0=stock), correct but ineffective on this stack.
last_update: 2026-11-14 (line closed)

## Key facts for any successor
- Fresh builds need M4=$TB/host-tools/usr/bin/m4 in env (Debian bison has /usr/bin/m4 baked in; host lacks /usr/bin/m4).
- guestroot (trackb/guestroot) = runtime sysroot with stage-built Mesa overlaid; usrmerge symlinks (lib->usr/lib, bin->usr/bin) are REQUIRED or qemu cannot open /lib/ld-linux.so.2. i386 python3.12 was added to guestroot (pyprobe recipe works: qemu-i386-static -L guestroot guestroot/usr/bin/python3.12). The deb pool trackb/debs is all-i386 (an accidental amd64 python set was removed).
- Builds: trackb/build (stock, from win32-perf/mesa-src), trackb/build-mod (from trackb/src-mod); stage1 = stock install, stage2 = mod install; overlay via trackb/overlay-mesa.sh <stage>.
- Probe baselines (quiet window, this line): stock D3D9 probe A 257.9 / B 247.5 / C 2.5 / D 986.6 ms/fr (mod-off run, load ~0.5-2.6). Raw GLX swap ~2-8 ms.
- Coordination history: build was SIGSTOP-paused 2026-11-14 ~00:41-00:53 JST so the virgl line could record the listen deliverable (delivery 0.969 under the exclusivity window).

## Rules in force (unchanged)
- Own workspace trackb/; own prefix under trackb/; display :115 only.
- NEVER touch :116, virgl server/socket, prefix-fresh, other lines' processes.
- Results -> RESULTS.md under "TRACK B" headings.
