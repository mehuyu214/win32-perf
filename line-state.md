# Win32 Perf Line — State (watchdog protocol, KK order 2026-11-13 22:37)

- status: STOPPED — KK order 2026-11-14 18:27 JST 「サノバ消して」: the Sanoba standing run is FULLY STOPPED (not frozen). Watchdog: do NOT relaunch the perf line or Sanoba under any staleness condition; this stop stands until KK personally countermands it in chat. Deletion of files is a separate step being confirmed with KK in the main chat — no files have been deleted.
- last_update: 2026-11-14 22:04 JST (rotation agent, VM clock verified). Sanoba STOPPED per KK 18:27 order — NO relaunch, NO file deletion (status/phase untouched by this heartbeat). KK 22:02 order: #5 RIDDLE JOKER launched and HELD at story screen on :118 for KK to play via game panel (pgid 29397, virgl, fresh fixed-template prefix; first line '8月下旬…' legible, shots/riddle2-title.png). NO further input from this line while KK plays. #2 Realive retry interrupted mid-PV (virgl server fixed + CMVS dialog verified legible; title not yet re-reached). Remaining before 24:00: #2/#6/#14 title-stuck, #4/#10/#19 shared-SEGV group, #7/#16/#18 boot-fail. Processed: #1-#19 (story OK x9, title-only x3, boot-fail x5, config-dialog x1, logo/OP x1).
- phase: STOPPED-BY-KK-ORDER (2026-11-14 18:27 JST) — Sanoba fully stopped per KK's 「サノバ消して」; NOT a freeze; do NOT resume, unfreeze or relaunch Sanoba when the rotation ends. Former phase: FROZEN-SANOBA (DMM rotation, EXTENDED past 15:00 by KK order 2026-11-14 14:05 — font fix + per-title measurement mandate) — DMM trial rotation line holds the VM's one-game slot. NOTE: the VM was replaced at ~10:04 JST and the virgl17 processes were already GONE when the rotation agent checked at 10:05 (no q32sup/qemu/wine/Xvfb/virgl processes exist) — there was nothing to SIGSTOP and there is nothing to SIGCONT. No Sanoba run is active during the rotation. [SUPERSEDED 2026-11-14 18:27 JST: the former plan to relaunch the standing run after the rotation is CANCELLED by KK's 「サノバ消して」 order — do NOT relaunch.] Prior context: audio delivery 1.000 uncontended vs 0.646 contended — crackle tracks contention; one AUTO stall on the Ayumu line (~60 s, resolved by manual Return, see RESULTS.md).
- heartbeat-note 10:53 JST (proactivity research run, not the rotation agent): rotation is demonstrably alive — Criminal Border 2nd trial (q32sup-var + max,-avx2) launched 10:41 JST on Xvfb :118, processes still running at 10:53; two KiriKiri crash dumps preceded it (10:36, 10:39) and no title verdict is recorded yet. Watchdog: do NOT relaunch the perf line during this window — the FROZEN phase is intentional until 15:00, and a second agent would break the one-game rule and add contention. This heartbeat only refreshes last_update; the rotation agent should resume its own 15-min updates.

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
- EXCEPTION (KK direct order, 2026-11-14 18:27 JST): status is STOPPED.
  While status is STOPPED, the watchdog must NOT relaunch the perf line
  or Sanoba for any reason (staleness included). Only KK personally
  countermanding this in chat ends the stop.
- claimed: 2026-11-14 08:09 JST (watchdog writes a JST timestamp here before relaunching;
  expires after 25 minutes)

## KK question (only when status is NEEDS_KK)
(none)
