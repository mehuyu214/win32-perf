# win32-perf line state (watchdog heartbeat)

status: RUNNING
phase: KK eye verdicts recorded (23:34 fade footage APPROVED 「だいぶ改善してるな」; 23:35 qualified 「まぁでもまだかくかくだね」 — evenness is the metric now). AUDIO ON VIRGL: LIVE — PA daemon on 47135 (pid 15978), game sink-input registered (Kirikiri), title probe nonzero 99.8% peak 0.188. virgl12: settings set 100/100/speed (verified), START armed; 240 s simultaneous A/V story capture IN PROGRESS (video ultrafast + PA monitor raw), then delivery ratio + v2/fade analysis + mp4 mux for KK
last_update: 2026-11-13 23:52 JST
claimed: 2026-11-13 22:37 JST (successor spawned by parent)

## Protocol (binding for every perf-line agent and the watchdog)
- The working agent updates `last_update` (and `phase` when it changes) at least every 15 minutes while working, and writes results into RESULTS.md immediately after obtaining them.
- Set `status: COMPLETE` only when KK's success gate is met (story progressing with input/audio/rendering, measured smoothness + stability, footage KK approves). Set `status: NEEDS_KK` only for a decision only KK can make, with the question written under this section.
- The watchdog (cron `win32perf-watchdog`, every 20 min) relaunches a successor when: status is RUNNING, `last_update` is >25 min old, no perf-line run is demonstrably active, and no unexpired `claimed` timestamp (<25 min) exists. Before relaunching it stamps `claimed` with its own timestamp to prevent duplicates.
- NEEDS_KK question: KK's eye verdict on the fixed-stack footage is the final gate for the perf goal (fade footage delivered 23:2x; story footage with audio in production now). Track B question RESOLVED by KK 23:32 ("do both") — excavation proceeds in parallel under its own agent.
