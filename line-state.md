# Win32 Perf Line — State (watchdog protocol, KK order 2026-11-13 22:37)

- status: RUNNING
- last_update: 2026-11-14 01:00 JST
- phase: Standing AUTO run LIVE at max settings (virgl15, sup 17741; text 100 / auto 100 / スピードモード screenshot-verified; story restored via Q.Load Quick-1 to Ch.1-1, AUTO advancing — verified by 60 s-apart screenshot pair; first post-restore Q.Save written, cadence ~5 min; infrastructure = systemd units xvfb116/virglsrv/perfpa, all active). Listen-paced video DELIVERED (logs/virgl13-story-listen.mp4, 5 min, delivery 0.975, ZERO voice-interior gaps; probe 3 passed at auto speed 41 / ノーマルモード, delivery 0.969). KK verdicts on the fixed stack: 23:34 だいぶ改善してるな (fade footage approved), 23:35 まぁでもまだかくかくだね (still jerky overall — evenness is the metric), 23:56 10点以上の秒がこんだけ出てる時点で64bitでの動作と大差ない (story footage in the 64-bit league), 00:41 virgl12 = best artifact so far. Remaining: KK's ear on the listen video; Track B excavation continues in parallel (separate agent).

## Protocol
- This file is the line's heartbeat. The watchdog cron (win32perf-watchdog,
  every 20 min) relaunches a successor agent when: status is RUNNING AND
  last_update is more than 25 minutes old AND no perf-line run is
  demonstrably active AND no unexpired `claimed` stamp exists.
- The active agent MUST update last_update (JST) and phase at least every
  15 minutes while working, and write results into RESULTS.md immediately
  after each measurement.
- Set status: COMPLETE only when KK's success gate is genuinely met.
  Set status: NEEDS_KK only for a decision only KK can make (write the
  question below). Otherwise leave status RUNNING.
- claimed: (watchdog writes a JST timestamp here before relaunching;
  expires after 25 minutes)

## KK question (only when status is NEEDS_KK)
(none)
