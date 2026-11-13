# win32-perf line state (watchdog heartbeat)

status: RUNNING
phase: ALL LINE PROCESSES DOWN after VM shutdown event ~01:05 JST (PID 1 in systemd-shutdown, systemctl bus unreachable; Xvfb/PA/virgl server all dead). PROVEN RECOVERY: systemd-run starts Xvfb fine (clean fd table from PID 1) — full recovery sequence written in RESULTS.md "INCIDENT UPDATE 3" (Xvfb -nolock -extension MIT-SHM as unit, then virgl server + PA as units, then virgl4). Resume as soon as systemctl responds again. Blocked meanwhile: KK's AUTO run + listen-paced video (00:01 order). KK verdicts recorded (23:34 improved / 23:35 still jerky / 23:56 same league as 64-bit native)
last_update: 2026-11-14 01:20 JST
claimed: 2026-11-13 22:37 JST (successor spawned by parent)

## Protocol (binding for every perf-line agent and the watchdog)
- The working agent updates `last_update` (and `phase` when it changes) at least every 15 minutes while working, and writes results into RESULTS.md immediately after obtaining them.
- Set `status: COMPLETE` only when KK's success gate is met (story progressing with input/audio/rendering, measured smoothness + stability, footage KK approves). Set `status: NEEDS_KK` only for a decision only KK can make, with the question written under this section.
- The watchdog (cron `win32perf-watchdog`, every 20 min) relaunches a successor when: status is RUNNING, `last_update` is >25 min old, no perf-line run is demonstrably active, and no unexpired `claimed` timestamp (<25 min) exists. Before relaunching it stamps `claimed` with its own timestamp to prevent duplicates.
- NEEDS_KK question: KK's eye verdict on the fixed-stack footage is the final gate for the perf goal (fade footage delivered 23:2x; story footage with audio in production now). Track B question RESOLVED by KK 23:32 ("do both") — excavation proceeds in parallel under its own agent.
