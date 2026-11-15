# Sanoba Witch trial — CONTINUOUS TAKE (single-session full playthrough)

Per KK's override (2026-11-13 02:06 JST): one uninterrupted take, crash-tolerant
split recording. Video: continuous-video.mkv (x11grab 1280x720@20, libx264
ultrafast). Audio: continuous-audio.raw (parec on game.monitor, float32le
48 kHz stereo). Conditions: base config (PULSE_LATENCY_MSEC=750,
LP_NUM_THREADS=1, PA via TCP), quiet protocol ACTIVE, in-game sound settings
as verified for the segments (BGM-only; see SEGMENTS.md). AUTO text-advance
(A key) throughout; choices handled manually without stopping the capture;
quick saves (F11 -> confirm) made periodically without stopping the capture.
Underrun count at start: 417.

## Start
- audio_start_epoch=1794503315.954849671 (2026-11-12 17:08:35 UTC)
- video_start_epoch=1794503315.965522996 (2026-11-12 17:08:35 UTC)
- video_minus_audio_offset_s=0.011 (video started 0.011 s after audio)
- director 2026-11-12 17:08:35 UTC epoch=1794503315: head sequence start (game on title)
- director 2026-11-12 17:08:47 UTC epoch=1794503327: settings screen on camera
- director 2026-11-12 17:09:07 UTC epoch=1794503347: returned to title; pressing START
- director 2026-11-12 17:09:28 UTC epoch=1794503368: AUTO toggled on (A key); head sequence done
- ATTEMPT 1 ABORTED at 17:10 UTC (~2 min in): the head settings visit showed
  the wrong config tab (ショートカット一覧 — the config remembered the last tab
  from an earlier exploration, and the director's single tab click did not
  switch). Files kept as continuous-video.attempt1.mkv (7.7 MB) /
  continuous-audio.attempt1.raw (44.7 MB). Director fixed (tab clicked twice,
  AUTO pressed later) and the take restarted as attempt 2 below.
  (Operational note: the first stop attempt self-matched its own pkill
  pattern via plain filenames elsewhere in the same command line and killed
  the operator shell — SIGTERM, 176 ms — after both captures were already
  stopped. No data lost; procedure split into separate commands since.)

## Attempt 2 start
- underrun count at start: 429
- audio_start_epoch=1794503613.4978707 (2026-11-12 17:13:33 UTC)
- video_start_epoch=1794503613.5095751 (2026-11-12 17:13:33 UTC)
- video_minus_audio_offset_s=0.012
- director 2026-11-12 17:13:33 UTC epoch=1794503613: head sequence start (game on title)
- director 2026-11-12 17:13:47 UTC epoch=1794503627: settings screen on camera
- director 2026-11-12 17:14:07 UTC epoch=1794503647: returned to title; pressing START
- director 2026-11-12 17:14:38 UTC epoch=1794503678: AUTO toggled on (A key); head sequence done
- ATTEMPT 2 ABORTED at 17:15 UTC (~1.5 min in): operator error in the launch
  line — a duplicated stdout redirect sent parec's output to /dev/null, so
  continuous-audio.raw stayed 0 bytes while the video recorded normally.
  Pre-flight had passed; the sink was live; only the file plumbing was wrong.
  Attempt-2 files kept (video-only artifact). Relaunch rule added: verify
  BOTH files are growing before the director starts.

## Attempt 3 start
- underrun count at start: 433
- audio_start_epoch=1794503760.8308372 (2026-11-12 17:16:00 UTC)
- video_start_epoch=1794503760.8332546 (2026-11-12 17:16:00 UTC)
- video_minus_audio_offset_s=0.002
- director 2026-11-12 17:16:41 UTC epoch=1794503801: head sequence start (game on title)
- director 2026-11-12 17:16:55 UTC epoch=1794503815: settings screen on camera
- director 2026-11-12 17:17:15 UTC epoch=1794503835: returned to title; pressing START
- director 2026-11-12 17:17:46 UTC epoch=1794503866: AUTO toggled on (A key); head sequence done
- health #1 2026-11-12 17:20:09 UTC epoch=1794504009: audio_bytes=94725376 audio_s~246 video_bytes=12320768 underruns_total=457 load=[0.77, 1.50, 1.88] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- health #2 2026-11-12 17:29:21 UTC epoch=1794504561: audio_bytes=306722080 audio_s~798 video_bytes=30146560 underruns_total=497 load=[0.84, 1.97, 2.12] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- health #3 2026-11-12 17:38:32 UTC epoch=1794505112: audio_bytes=518310912 audio_s~1349 video_bytes=50593792 underruns_total=511 load=[2.74, 2.30, 2.38] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- health #4 2026-11-12 17:47:46 UTC epoch=1794505666: audio_bytes=730674592 audio_s~1902 video_bytes=74973184 underruns_total=535 load=[3.71, 2.65, 2.60] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- quick save #1 at 17:52 UTC (take age ~36 min): written (data_quick_01.bmp
  refreshed). Procedure corrected: the first blind attempt raced (F11 dialog
  not yet open when the confirm click fired; no save resulted, AUTO state
  verified at each step instead). Working sequence: A (stop, verify parked)
  -> F11 (verify dialog on screen) -> はい (537,413) -> verify file mtime ->
  A (resume, verify Auto indicator).
- correction to the quick-save #1 note: the save DID land at 17:49:13 UTC
  (data_quick_01 refreshed; quick save uses rotating slots — the previous
  save moved to data_quick_02 with its original 17:07 mtime). The mtime
  check raced the write. The resume-A press was eaten by the still-closing
  dialog, leaving the game parked on one line for ~2 min (static hold in
  the footage, no content lost); AUTO re-enabled and verified afterwards.
  Lesson: after はい, wait for the write + verify before pressing A.
- health #5 2026-11-12 17:59:40 UTC epoch=1794506380: audio_bytes=1005224488 audio_s~2617 video_bytes=104857600 underruns_total=577 load=[2.85, 3.01, 2.83] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]

## VM RESTART — take interrupted (18:02 UTC)
- The VM restarted at ~18:02 UTC (uptime 1 min at 18:02:51; the operator's
  health-wait process was SIGTERM'd as it went down). Game, PulseAudio,
  Xvfb and both capture processes died.
- SURVIVED intact: continuous-audio.raw = 2767.6 s (46.1 min);
  continuous-video.mkv = 2765.9 s by ffprobe (valid Matroska, ~1.8 s cluster
  tail difference). The crash-tolerant split format worked as designed.
- Saves on disk intact: data_quick_01 @17:49:13 UTC (take age 33.2 min,
  parked line: Wakaba's "人の頼みばっかり…" line) — the resume/splice point.
  Part 1 covers through take age 46.1 min, so the final edit can splice at
  the quick-save dialog in part 1 and continue with part 2's replay.
- Recovery: relaunch stack, verify settings, Q.Load the quick save, record
  part 2 to continuous-*.part2.* with its own start epochs.

## Part 2 (resume after VM restart)
- resumed from data_quick_01 (17:49:13 UTC) via START -> F12 quick load; position = the boundary-save line (Wakaba, hallway). Settings verified intact after restart (screenshot relaunch1-sound.png).
- underrun count at part2 start: 163
- part2 audio_start_epoch=1794506962.058359 (2026-11-12 18:09:22 UTC)
- part2 video_start_epoch=1794506962.068112 (2026-11-12 18:09:22 UTC)
- part2 video_minus_audio_offset_s=0.010
- AUTO resumed for part 2 at 18:10:12 UTC (A key after captures started; splice line = Wakaba's boundary-save line).
- quick save P2 #1 2026-11-12 18:13:49 UTC epoch=1794507173: wrote=no cycle_s=56 part2_audio_age_s~267 shot=cont-saveP2-1.png
- quick save P2 #2 2026-11-12 18:15:49 UTC: wrote=yes confirm_cycle_s=25 part2_audio_age_s~387 shot=cont-saveP2-2.png
- note on save P2 #2: the resume-A in the confirm half was eaten by the
  still-closing dialog (same failure as save #1 in part 1); the game held
  the splice line statically for ~4 min in total across the cycle's
  verification rounds, then AUTO was re-pressed and verified. Fix baked
  into cont-save-b.sh: wait 6 s after the write before pressing A.
  Also learned: the first F11 right after parking can be dropped while
  the engine settles — if the dialog shot shows no dialog, press F11
  again (worked immediately in both occurrences).
- quick save P2 #7 2026-11-12 18:18:26 UTC: wrote=yes confirm_cycle_s=31 part2_audio_age_s~544 shot=cont-saveP2-7.png
- health P2 #1 2026-11-12 18:18:38 UTC epoch=1794507518: audio_bytes=212851904 audio_s~554 video_bytes=20709376 underruns_total=1183 load=[4.55, 3.72, 2.59] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- health P2 #2 2026-11-12 18:19:31 UTC epoch=1794507571: audio_bytes=232870952 audio_s~606 video_bytes=23330816 underruns_total=1215 load=[4.79, 3.86, 2.70] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- health P2 #1 (18:18 UTC): underruns 163 -> 1183 since part-2 start.
  Spot gate on continuous-audio.part2.raw at 572 s: delivery 0.528 overall;
  gap census = 509 runs ALL in the 0.2-0.6 s buffer-hole band (198.9 s of
  holes, ~53/min) + one 72.1 s park. Active-span delivery ~0.60 — far below
  part 1's standard. Cause read: post-restart contention (load 4.89 and
  rising; the whole VM's tenants resumed at once) on a cold instance.
  Mitigation: this span is still inside part 1's recorded range (part 2
  resumed at story-age 33.2 min; part 1 covers to 46.1 min; part 2's story
  frontier is ~6 story-min short of that), so no unique content is at risk
  yet. Plan: keep recording + saving; re-measure a fresh window before the
  frontier crossing; if holes persist into unique content, park and wait
  for the load to settle / redo from the current quick save.
- quick save P2 #10 2026-11-12 18:21:22 UTC: wrote=yes confirm_cycle_s=32 part2_audio_age_s~720 shot=cont-saveP2-10.png
- frontier checkpoint (18:21 UTC, part-2 tail window 240 s): 45 buffer
  holes (17.6 s) + one 55.9 s modal silence (save cycle #4's dialog/settle
  stretch); in-flow delivery ~0.904, ~11 holes/min — still below part 1's
  standard but improving fast (first window was ~53/min; load 4.89 -> 3.30).
  Decision: keep recording; re-measure at the next checkpoint; escalate to
  park-and-wait only if the rate stops improving. F11 rule refined: presses
  are dropped while the parked line is still type-writing — retry until
  the dialog is screenshot-verified (needed 3 presses in cycle #4).
- quick save P2 #14 2026-11-12 18:23:21 UTC: wrote=yes confirm_cycle_s=32 part2_audio_age_s~839 shot=cont-saveP2-14.png
- health P2 #3 2026-11-12 18:30:31 UTC epoch=1794508231: audio_bytes=486527304 audio_s~1266 video_bytes=50331648 underruns_total=1324 load=[2.93, 3.27, 2.84] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- recovery checkpoint (18:30 UTC): fresh tail-240 s window = 6 holes
  (2.3 s), no long gaps, in-flow delivery 0.991; load 2.48; underrun rate
  collapsed. Part 2's audio is back at part-1 quality. The degraded region
  is confined to part 2's first ~13 min (replay span, duplicated in part 1)
  plus a short ~0.90 stretch after it. Continuing the take.
- quick save P2 #17 2026-11-12 18:32:04 UTC: wrote=yes confirm_cycle_s=33 part2_audio_age_s~1362 shot=cont-saveP2-17.png
- quick save P2 #20 2026-11-12 18:33:31 UTC: wrote=yes confirm_cycle_s=34 part2_audio_age_s~1448 shot=cont-saveP2-20.png
- health P2 #4 2026-11-12 18:41:39 UTC epoch=1794508899: audio_bytes=743163304 audio_s~1935 video_bytes=81002496 underruns_total=1378 load=[0.24, 1.64, 2.24] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- quick save P2 #23 2026-11-12 18:43:16 UTC: wrote=yes confirm_cycle_s=33 part2_audio_age_s~2034 shot=cont-saveP2-23.png
- quick save P2 #25 2026-11-12 18:44:20 UTC: wrote=yes confirm_cycle_s=33 part2_audio_age_s~2097 shot=cont-saveP2-25.png
- health P2 #5 2026-11-12 18:52:29 UTC epoch=1794509549: audio_bytes=992643368 audio_s~2585 video_bytes=108003328 underruns_total=1418 load=[3.56, 2.57, 2.48] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- quick save P2 #27 2026-11-12 18:54:39 UTC: wrote=yes confirm_cycle_s=34 part2_audio_age_s~2717 shot=cont-saveP2-27.png
- quick save P2 #30 2026-11-12 18:56:32 UTC: wrote=yes confirm_cycle_s=34 part2_audio_age_s~2830 shot=cont-saveP2-30.png
- health P2 #6 2026-11-12 19:04:42 UTC epoch=1794510282: audio_bytes=1274018672 audio_s~3317 video_bytes=137887744 underruns_total=1450 load=[1.35, 2.25, 2.34] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- quick save P2 #33 2026-11-12 19:06:07 UTC: wrote=yes confirm_cycle_s=32 part2_audio_age_s~3405 shot=cont-saveP2-33.png
- quick save P2 #35 2026-11-12 19:07:33 UTC: wrote=yes confirm_cycle_s=32 part2_audio_age_s~3490 shot=cont-saveP2-35.png
- health P2 #7 2026-11-12 19:15:48 UTC epoch=1794510948: audio_bytes=1529411912 audio_s~3982 video_bytes=165937152 underruns_total=1476 load=[1.56, 1.80, 2.17] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- quick save P2 #37 2026-11-12 19:17:27 UTC: wrote=yes confirm_cycle_s=35 part2_audio_age_s~4084 shot=cont-saveP2-37.png
- health P2 #8 2026-11-12 19:25:39 UTC epoch=1794511539: audio_bytes=1756719504 audio_s~4574 video_bytes=190578688 underruns_total=1504 load=[4.28, 2.73, 2.51] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- quick save P2 #40 2026-11-12 19:27:06 UTC: wrote=yes confirm_cycle_s=34 part2_audio_age_s~4664 shot=cont-saveP2-40.png
- quick save P2 #43 2026-11-12 19:28:27 UTC: wrote=yes confirm_cycle_s=32 part2_audio_age_s~4744 shot=cont-saveP2-43.png
- health P2 #9 2026-11-12 19:36:34 UTC epoch=1794512194: audio_bytes=2008293848 audio_s~5229 video_bytes=216006656 underruns_total=1546 load=[3.85, 3.42, 2.84] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]

## Save procedure change (KK order, 2026-11-13 04:28 JST)
- KK: the F11 + confirmation-dialog ceremony is over-engineered; use the
  game's Q.Save — a single action, no modal dialog, ~2 s instead of ~33 s.
- Findings: the bottom-bar Q.Save BUTTON registers hover (highlight +
  クイックセーブ caption) but synthetic clicks never activate it — instant,
  hover-settled, and 1 s-held clicks all produced no write, parked or in
  AUTO (nothing in the game dir changed). F11 also stays locked out during
  AUTO. What works: the F11 dialog's own 次回から確認しない option, now
  enabled in-game (checkbox verified on screen) — F11 now writes INSTANTLY
  with the game's save toast (Quick N timestamp card, itself a splice
  marker) and no modal, so the eaten-resume failure mode is gone.
- New cycle (cont-qsave-loop.sh): A (park) -> F11 (instant, mtime-verified)
  -> A (resume), ~10 s per save, repeated every ~60 s. First no-dialog
  saves: 19:35:5x UTC (parked, instant) — dialog-era saves ended at #43.
- qsave 2026-11-12 19:37:28 UTC epoch=1794512236: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:38:25 UTC epoch=1794512293: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:39:22 UTC epoch=1794512350: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:40:19 UTC epoch=1794512407: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:41:16 UTC epoch=1794512464: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:42:13 UTC epoch=1794512521: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:43:10 UTC epoch=1794512578: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:44:07 UTC epoch=1794512635: wrote=no part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)

## VM RESTART #2 — part 2 ended (19:37 UTC)
- The VM restarted again at ~19:37 UTC (uptime 7 min at 19:44). The new
  qsave loop's first cycle was caught in it (xdotool/display failures,
  all cycles wrote=no — logged as-is; the loop itself was not the cause).
- SURVIVED: continuous-audio.part2.raw = 5255.2 s (87.6 min, last write
  19:36:57); continuous-video.part2.mkv last write 19:36:45 (duration
  verified at mux time). Newest quick save data_quick_01 @19:35:53 UTC —
  the library scene, ~1 min before the crash: KK's save-density rule kept
  the resume point ~1 min stale, as designed.
- Recovery #2: relaunch stack, F12 quick-load the 19:35:53 save, record
  part 3 (continuous-*.part3.*) with its own epochs.
- pre-flight note: the in-scene probe is digital silence because the library scene is music-less by design (cross-verified: part 2 recorded this same scene as exact zeros from ~19:31 UTC while the chain was healthy); the chain was instead verified end-to-end at the title (probe nonzero 1.000, peak 0.196) minutes before part 3 started. Sink-input live.
- part3 audio_start_epoch=1794513051.8845181 (2026-11-12 19:50:51 UTC)
- part3 video_start_epoch=1794513051.8864205 (2026-11-12 19:50:51 UTC)
- part3 video_minus_audio_offset_s=0.002
- qsave 2026-11-12 19:51:49 UTC epoch=1794513102: wrote=yes part2_audio_age_s~5255 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:52:08 UTC epoch=1794513116: wrote=no part2_audio_age_s~75 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:53:27 UTC epoch=1794513194: wrote=no part2_audio_age_s~154 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:54:24 UTC epoch=1794513252: wrote=no part2_audio_age_s~212 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:55:21 UTC epoch=1794513309: wrote=no part2_audio_age_s~269 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:56:18 UTC epoch=1794513366: wrote=no part2_audio_age_s~326 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:57:15 UTC epoch=1794513423: wrote=no part2_audio_age_s~383 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:58:13 UTC epoch=1794513480: wrote=no part2_audio_age_s~440 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 19:59:10 UTC epoch=1794513538: wrote=no part2_audio_age_s~498 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:00:07 UTC epoch=1794513595: wrote=no part2_audio_age_s~555 (A-park -> F11 instant -> A-resume)
- INPUT FOCUS finding (20:05 UTC): after ~19:51 the X input focus drifted
  off the game window (bare Xvfb, no WM), so xdotool key events went
  nowhere while mouse clicks kept working — 8 loop cycles + manual cycles
  failed at the park step (F11 then hit the AUTO lockout, wrote=no; the
  story/captures were never at risk). Fix: xdotool windowfocus on the game
  window before key input; verified — focused park -> F11 wrote=YES ->
  resume OK. The loop script now refocuses at every cycle start.
- qsave 2026-11-12 20:06:04 UTC epoch=1794513958: wrote=yes part2_audio_age_s~912 (A-park -> F11 instant -> A-resume)
- health #1 2026-11-12 20:06:08 UTC epoch=1794513968: audio_bytes=351047984 audio_s~914 video_bytes=32505856 underruns_total=73 load=[0.86, 2.01, 1.85] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 20:06:55 UTC epoch=1794514009: wrote=yes part2_audio_age_s~963 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:07:47 UTC epoch=1794514060: wrote=yes part2_audio_age_s~1014 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:08:38 UTC epoch=1794514112: wrote=yes part2_audio_age_s~1065 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:09:35 UTC epoch=1794514163: wrote=no part2_audio_age_s~1123 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:10:32 UTC epoch=1794514220: wrote=no part2_audio_age_s~1180 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:11:30 UTC epoch=1794514277: wrote=no part2_audio_age_s~1237 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:12:21 UTC epoch=1794514335: wrote=yes part2_audio_age_s~1288 (A-park -> F11 instant -> A-resume)
- qsave 2026-11-12 20:16:31 UTC epoch=1794514553: wrote=yes part3_audio_age_s~1539 
- qsave 2026-11-12 20:17:47 UTC epoch=1794514631: wrote=yes part3_audio_age_s~1614 
- qsave 2026-11-12 20:18:55 UTC epoch=1794514707: wrote=yes part3_audio_age_s~1682 
- qsave 2026-11-12 20:20:03 UTC epoch=1794514775: wrote=yes part3_audio_age_s~1751 
- qsave 2026-11-12 20:21:15 UTC epoch=1794514843: wrote=yes part3_audio_age_s~1822 
- qsave 2026-11-12 20:22:25 UTC epoch=1794514915: wrote=yes part3_audio_age_s~1893 
- qsave 2026-11-12 20:23:45 UTC epoch=1794514986: wrote=yes part3_audio_age_s~1973 
- qsave 2026-11-12 20:24:56 UTC epoch=1794515065: wrote=yes part3_audio_age_s~2044 
- health #2 2026-11-12 20:25:39 UTC epoch=1794515139: audio_bytes=800837392 audio_s~2085 video_bytes=88342528 underruns_total=135 load=[3.21, 1.90, 1.90] quiet=[started_epoch=1794499060 restore_due_epoch=1794520660 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- QUIET PROTOCOL EXTENDED (20:27 UTC): the take continues past the
  original restore deadline, so restore_due_epoch moved 1794520660
  (06:57 JST) -> 1794535060 (10:57 JST); the old watchdog sleep was killed and
  a new one started for the new deadline. Jobs stay paused (vn-arcade-
  dev-loop, bluesky-continuous-posting, agentic-feature-tour).
- qsave 2026-11-12 20:26:40 UTC epoch=1794515160: wrote=yes part3_audio_age_s~2148 
- qsave 2026-11-12 20:27:46 UTC epoch=1794515240: wrote=yes part3_audio_age_s~2214 
- qsave 2026-11-12 20:28:55 UTC epoch=1794515306: wrote=yes part3_audio_age_s~2283 
- qsave 2026-11-12 20:30:15 UTC epoch=1794515375: wrote=yes part3_audio_age_s~2362 
- qsave 2026-11-12 20:31:34 UTC epoch=1794515455: wrote=yes part3_audio_age_s~2442 
- qsave 2026-11-12 20:32:55 UTC epoch=1794515534: wrote=yes part3_audio_age_s~2523 
- qsave 2026-11-12 20:34:05 UTC epoch=1794515615: wrote=yes part3_audio_age_s~2593 
- qsave 2026-11-12 20:35:24 UTC epoch=1794515685: wrote=no part3_audio_age_s~2672 
- health #3 2026-11-12 20:35:37 UTC epoch=1794515737: audio_bytes=1030413824 audio_s~2683 video_bytes=116654080 underruns_total=227 load=[3.61, 2.63, 2.27] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 20:36:19 UTC epoch=1794515747: wrote=yes part3_audio_age_s~2727 
- qsave 2026-11-12 20:37:37 UTC epoch=1794515819: wrote=yes part3_audio_age_s~2805 
- qsave 2026-11-12 20:38:47 UTC epoch=1794515897: wrote=yes part3_audio_age_s~2874 
- qsave 2026-11-12 20:40:05 UTC epoch=1794515967: wrote=yes part3_audio_age_s~2953 
- qsave 2026-11-12 20:41:18 UTC epoch=1794516045: wrote=yes part3_audio_age_s~3025 
- qsave 2026-11-12 20:42:30 UTC epoch=1794516118: wrote=yes part3_audio_age_s~3098 
- qsave 2026-11-12 20:43:50 UTC epoch=1794516190: wrote=yes part3_audio_age_s~3178 
- qsave 2026-11-12 20:45:08 UTC epoch=1794516270: wrote=yes part3_audio_age_s~3256 
- health #4 2026-11-12 20:45:18 UTC epoch=1794516318: audio_bytes=1253818160 audio_s~3265 video_bytes=142606336 underruns_total=321 load=[4.60, 3.30, 2.65] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 20:46:09 UTC epoch=1794516331: wrote=yes part3_audio_age_s~3317 
- qsave 2026-11-12 20:47:28 UTC epoch=1794516409: wrote=yes part3_audio_age_s~3395 
- qsave 2026-11-12 20:48:37 UTC epoch=1794516488: wrote=yes part3_audio_age_s~3465 
- qsave 2026-11-12 20:49:47 UTC epoch=1794516557: wrote=yes part3_audio_age_s~3535 
- qsave 2026-11-12 20:50:57 UTC epoch=1794516627: wrote=yes part3_audio_age_s~3604 
- qsave 2026-11-12 20:52:15 UTC epoch=1794516697: wrote=yes part3_audio_age_s~3683 
- qsave 2026-11-12 20:53:33 UTC epoch=1794516775: wrote=yes part3_audio_age_s~3761 
- qsave 2026-11-12 20:54:42 UTC epoch=1794516853: wrote=yes part3_audio_age_s~3830 
- health #5 2026-11-12 20:55:03 UTC epoch=1794516903: audio_bytes=1478077072 audio_s~3849 video_bytes=169082880 underruns_total=385 load=[1.82, 2.78, 2.61] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 20:55:49 UTC epoch=1794516913: wrote=yes part3_audio_age_s~3897 
- qsave 2026-11-12 20:56:58 UTC epoch=1794516989: wrote=yes part3_audio_age_s~3966 
- qsave 2026-11-12 20:58:16 UTC epoch=1794517058: wrote=yes part3_audio_age_s~4044 
- qsave 2026-11-12 20:59:35 UTC epoch=1794517136: wrote=no part3_audio_age_s~4123 
- qsave 2026-11-12 21:00:46 UTC epoch=1794517215: wrote=yes part3_audio_age_s~4193 
- qsave 2026-11-12 21:01:56 UTC epoch=1794517286: wrote=yes part3_audio_age_s~4264 
- qsave 2026-11-12 21:03:16 UTC epoch=1794517356: wrote=no part3_audio_age_s~4344 
- qsave 2026-11-12 21:04:33 UTC epoch=1794517436: wrote=yes part3_audio_age_s~4421 
- health #6 2026-11-12 21:04:44 UTC epoch=1794517484: audio_bytes=1701542024 audio_s~4431 video_bytes=198967296 underruns_total=449 load=[0.52, 1.94, 2.27] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 21:05:25 UTC epoch=1794517495: wrote=yes part3_audio_age_s~4473 
- qsave 2026-11-12 21:06:39 UTC epoch=1794517565: wrote=no part3_audio_age_s~4547 resume-needed-2-presses
- qsave 2026-11-12 21:07:47 UTC epoch=1794517639: wrote=yes part3_audio_age_s~4615 
- qsave 2026-11-12 21:09:07 UTC epoch=1794517707: wrote=no part3_audio_age_s~4694 
- qsave 2026-11-12 21:10:16 UTC epoch=1794517787: wrote=yes part3_audio_age_s~4764 
- qsave 2026-11-12 21:11:24 UTC epoch=1794517856: wrote=yes part3_audio_age_s~4832 
- qsave 2026-11-12 21:12:41 UTC epoch=1794517924: wrote=yes part3_audio_age_s~4909 
- qsave 2026-11-12 21:13:52 UTC epoch=1794518001: wrote=yes part3_audio_age_s~4980 
- health #7 2026-11-12 21:14:27 UTC epoch=1794518067: audio_bytes=1924970288 audio_s~5012 video_bytes=222822400 underruns_total=513 load=[0.21, 1.49, 2.00] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 21:15:15 UTC epoch=1794518078: wrote=no part3_audio_age_s~5063 
- qsave 2026-11-12 21:16:26 UTC epoch=1794518155: wrote=yes part3_audio_age_s~5134 
- qsave 2026-11-12 21:17:35 UTC epoch=1794518226: wrote=yes part3_audio_age_s~5203 
- qsave 2026-11-12 21:18:45 UTC epoch=1794518295: wrote=yes part3_audio_age_s~5273 
- qsave 2026-11-12 21:19:55 UTC epoch=1794518365: wrote=yes part3_audio_age_s~5343 
- qsave 2026-11-12 21:21:03 UTC epoch=1794518435: wrote=yes part3_audio_age_s~5411 
- qsave 2026-11-12 21:22:12 UTC epoch=1794518503: wrote=yes part3_audio_age_s~5479 
- qsave 2026-11-12 21:23:22 UTC epoch=1794518572: wrote=yes part3_audio_age_s~5549 
- health #8 2026-11-12 21:24:10 UTC epoch=1794518650: audio_bytes=2148824080 audio_s~5595 video_bytes=244318208 underruns_total=573 load=[4.08, 2.33, 2.25] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 21:24:49 UTC epoch=1794518659: wrote=yes part3_audio_age_s~5636 
- qsave 2026-11-12 21:25:57 UTC epoch=1794518729: wrote=yes part3_audio_age_s~5705 
- qsave 2026-11-12 21:27:16 UTC epoch=1794518797: wrote=yes part3_audio_age_s~5783 
- qsave 2026-11-12 21:28:34 UTC epoch=1794518876: wrote=yes part3_audio_age_s~5862 
- qsave 2026-11-12 21:29:42 UTC epoch=1794518954: wrote=yes part3_audio_age_s~5930 
- qsave 2026-11-12 21:30:52 UTC epoch=1794519022: wrote=yes part3_audio_age_s~6000 
- qsave 2026-11-12 21:32:11 UTC epoch=1794519092: wrote=yes part3_audio_age_s~6079 
- qsave 2026-11-12 21:33:22 UTC epoch=1794519171: wrote=yes part3_audio_age_s~6150 
- health #9 2026-11-12 21:33:50 UTC epoch=1794519230: audio_bytes=2371996864 audio_s~6177 video_bytes=267124736 underruns_total=633 load=[3.51, 2.72, 2.44] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 21:34:37 UTC epoch=1794519238: wrote=no part3_audio_age_s~6224 
- qsave 2026-11-12 21:35:47 UTC epoch=1794519317: wrote=yes part3_audio_age_s~6295 
- qsave 2026-11-12 21:37:04 UTC epoch=1794519387: wrote=yes part3_audio_age_s~6372 
- qsave 2026-11-12 21:38:22 UTC epoch=1794519464: wrote=yes part3_audio_age_s~6450 
- qsave 2026-11-12 21:39:33 UTC epoch=1794519542: wrote=yes part3_audio_age_s~6520 
- qsave 2026-11-12 21:40:52 UTC epoch=1794519613: wrote=no part3_audio_age_s~6600 
- qsave 2026-11-12 21:42:11 UTC epoch=1794519692: wrote=yes part3_audio_age_s~6678 
- qsave 2026-11-12 21:43:28 UTC epoch=1794519771: wrote=yes part3_audio_age_s~6756 
- health #10 2026-11-12 21:43:29 UTC epoch=1794519810: audio_bytes=2594276008 audio_s~6755 video_bytes=289931264 underruns_total=698 load=[5.10, 3.48, 2.79] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 21:44:56 UTC epoch=1794519866: wrote=yes part3_audio_age_s~6843 
- qsave 2026-11-12 21:46:14 UTC epoch=1794519936: wrote=yes part3_audio_age_s~6922 
- qsave 2026-11-12 21:47:24 UTC epoch=1794520014: wrote=yes part3_audio_age_s~6992 
- qsave 2026-11-12 21:48:43 UTC epoch=1794520084: wrote=no part3_audio_age_s~7071 
- qsave 2026-11-12 21:50:02 UTC epoch=1794520163: wrote=no part3_audio_age_s~7150 
- qsave 2026-11-12 21:51:22 UTC epoch=1794520242: wrote=no part3_audio_age_s~7230 
- qsave 2026-11-12 21:52:32 UTC epoch=1794520322: wrote=yes part3_audio_age_s~7299 

## VM RESTART #3 — part 3 ended (21:53 UTC)
- The VM restarted a third time at ~21:53 UTC. SURVIVED intact:
  continuous-audio.part3.raw = 7345.9 s (122.4 min, last write 21:53:17);
  continuous-video.part3.mkv last write 21:53:15. The newest quick save
  (loop12 cycle 7) landed ~20-50 s before the crash — the resume point is
  under a minute stale again. Story frontier: Chapter 1-4, classroom.
- Net story coverage so far: P1 46.1 + P2 87.6 + P3 122.4 - ~13 overlap
  = ~243 min (~4.05 h). Recovery #3: relaunch, F12 quick load, part 4.

## Part 4 (resume after VM restart #3)
- resumed from data_quick_01 (21:52:14 UTC) via START -> F12 (first F12 dropped, focused re-press loaded instantly); position = Ch.1-4 classroom, Kanae scene. Title probe before start: nonzero 1.000, peak 0.196 — chain verified.
- underrun count at part4 start: 52
- part4 audio_start_epoch=1794520632.6321092 (2026-11-12 21:57:12 UTC)
- part4 video_start_epoch=1794520632.6346786 (2026-11-12 21:57:12 UTC)
- part4 video_minus_audio_offset_s=0.003
- qsave 2026-11-12 21:58:19 UTC epoch=1794520673: wrote=yes part3_audio_age_s~66 

## VM RESTART #4 — part 4 cut short (21:59 UTC)
- The VM restarted again at ~21:59 UTC, only ~6 min after restart #3 —
  the restart cadence is accelerating (18:02, 19:37, 21:53, 21:59).
- SURVIVED: continuous-audio.part4.raw = 118.3 s (the Kanae scene head);
  one qsave landed in part 4 (21:58:19). Resume point still ~1-2 min
  stale. Recovery #4 proceeds on the same drill (part 5); if restarts
  keep landing minutes apart, the parts simply get shorter — every part
  is preserved on disk and spliceable.

## Part 5 (resume after VM restart #4)
- part 4 survived as a 118.3 s fragment (Kanae scene head, spliceable); resumed from the 21:58:19 quick save via START -> F12 (focused, second press).
- TOOLING FINDING: xdotool is the pa-bin copy (/home/hatch/workspace/sanoba-audio/pa-bin/usr/bin/xdotool, needs libxdo via the pa-bin LD_LIBRARY_PATH); bare 'xdotool' is not on PATH in this boot. The loop script now invokes it by absolute path with the pa-bin library path; ffmpeg keeps the clean env.
- underrun count at part5 start: 4
- part5 audio_start_epoch=1794521055.928038 (2026-11-12 22:04:15 UTC)
- part5 video_start_epoch=1794521055.9339788 (2026-11-12 22:04:15 UTC)
- part5 video_minus_audio_offset_s=0.006
- qsave 2026-11-12 22:05:19 UTC epoch=1794521092: wrote=yes part3_audio_age_s~63 
- qsave 2026-11-12 22:06:35 UTC epoch=1794521159: wrote=yes part3_audio_age_s~139 
- qsave 2026-11-12 22:07:42 UTC epoch=1794521235: wrote=yes part3_audio_age_s~206 
- qsave 2026-11-12 22:08:59 UTC epoch=1794521302: wrote=no part3_audio_age_s~283 
- qsave 2026-11-12 22:10:18 UTC epoch=1794521379: wrote=no part3_audio_age_s~361 
- qsave 2026-11-12 22:11:27 UTC epoch=1794521458: wrote=yes part3_audio_age_s~431 
- qsave 2026-11-12 22:12:45 UTC epoch=1794521527: wrote=yes part3_audio_age_s~509 
- qsave 2026-11-12 22:13:55 UTC epoch=1794521605: wrote=yes part3_audio_age_s~578 
- health #1 2026-11-12 22:14:24 UTC epoch=1794521664: audio_bytes=232814608 audio_s~606 video_bytes=27000832 underruns_total=64 load=[5.89, 3.32, 1.84] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 22:15:04 UTC epoch=1794521673: wrote=yes part3_audio_age_s~648 
- qsave 2026-11-12 22:16:19 UTC epoch=1794521744: wrote=yes part3_audio_age_s~723 
- qsave 2026-11-12 22:17:36 UTC epoch=1794521819: wrote=no part3_audio_age_s~800 
- qsave 2026-11-12 22:18:47 UTC epoch=1794521896: wrote=yes part3_audio_age_s~871 
- qsave 2026-11-12 22:20:05 UTC epoch=1794521967: wrote=yes part3_audio_age_s~949 
- qsave 2026-11-12 22:21:16 UTC epoch=1794522045: wrote=yes part3_audio_age_s~1019 
- qsave 2026-11-12 22:22:38 UTC epoch=1794522116: wrote=yes part3_audio_age_s~1102 
- qsave 2026-11-12 22:23:50 UTC epoch=1794522198: wrote=yes part3_audio_age_s~1174 
- health #2 2026-11-12 22:24:05 UTC epoch=1794522245: audio_bytes=455835448 audio_s~1187 video_bytes=50593792 underruns_total=268 load=[7.66, 4.46, 2.76] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 22:24:49 UTC epoch=1794522254: wrote=yes part3_audio_age_s~1233 
- qsave 2026-11-12 22:26:11 UTC epoch=1794522329: wrote=yes part3_audio_age_s~1315 
- qsave 2026-11-12 22:27:31 UTC epoch=1794522411: wrote=no part3_audio_age_s~1395 
- qsave 2026-11-12 22:28:50 UTC epoch=1794522491: wrote=yes part3_audio_age_s~1473 
- qsave 2026-11-12 22:29:58 UTC epoch=1794522570: wrote=yes part3_audio_age_s~1542 
- qsave 2026-11-12 22:31:07 UTC epoch=1794522638: wrote=yes part3_audio_age_s~1610 
- qsave 2026-11-12 22:32:15 UTC epoch=1794522707: wrote=yes part3_audio_age_s~1679 
- qsave 2026-11-12 22:33:27 UTC epoch=1794522775: wrote=yes part3_audio_age_s~1751 resume-needed-2-presses
- health #3 2026-11-12 22:33:46 UTC epoch=1794522826: audio_bytes=679148936 audio_s~1768 video_bytes=74186752 underruns_total=595 load=[3.12, 3.74, 3.16] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- INCIDENT (part 5, ~22:32-22:36 UTC): loop16 cycle 8's two resume
  presses were both eaten; AUTO stayed OFF ~3-4 min (story parked at the
  Ch.1-4 classroom transition — no content lost, captures kept rolling).
  Resumed manually with focus + verified. The loop now retries the
  resume up to 3 times with a state check after each press.
- AUDIO SPOT GATE (part 5): 600-840 s nonzero 0.974, 16 holes (6.3 s);
  1300-1540 s nonzero 0.852, 91 holes (35.6 s, all the 0.39 s buffer
  signature) — a contention-degraded span (VM load ~3.1-3.7 in that
  window, post-restart herd). In-flow delivery ~0.85 there vs ~0.97 in
  the earlier span. Logged as a known characteristic; final gate will
  map all such spans.
- qsave 2026-11-12 22:35:15 UTC epoch=1794522889: wrote=yes part3_audio_age_s~1859 resume-press-1
- qsave 2026-11-12 22:36:31 UTC epoch=1794522955: wrote=yes part3_audio_age_s~1934 resume-press-1
- qsave 2026-11-12 22:37:47 UTC epoch=1794523031: wrote=no part3_audio_age_s~2011 resume-press-1
- qsave 2026-11-12 22:39:02 UTC epoch=1794523107: wrote=yes part3_audio_age_s~2086 resume-press-1
- qsave 2026-11-12 22:40:09 UTC epoch=1794523182: wrote=yes part3_audio_age_s~2152 resume-press-1
- qsave 2026-11-12 22:41:16 UTC epoch=1794523249: wrote=yes part3_audio_age_s~2220 resume-press-1
- qsave 2026-11-12 22:42:21 UTC epoch=1794523316: wrote=yes part3_audio_age_s~2285 resume-press-1
- qsave 2026-11-12 22:43:31 UTC epoch=1794523381: wrote=yes part3_audio_age_s~2354 resume-press-1
- health #4 2026-11-12 22:44:23 UTC epoch=1794523463: audio_bytes=923848160 audio_s~2405 video_bytes=97517568 underruns_total=687 load=[1.07, 2.31, 2.67] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 22:45:04 UTC epoch=1794523477: wrote=yes part3_audio_age_s~2448 resume-press-1
- qsave 2026-11-12 22:46:12 UTC epoch=1794523544: wrote=yes part3_audio_age_s~2516 resume-press-1
- qsave 2026-11-12 22:47:28 UTC epoch=1794523612: wrote=yes part3_audio_age_s~2592 resume-press-1
- qsave 2026-11-12 22:48:46 UTC epoch=1794523688: wrote=yes part3_audio_age_s~2670 resume-press-1
- qsave 2026-11-12 22:49:55 UTC epoch=1794523767: wrote=yes part3_audio_age_s~2739 resume-press-1
- qsave 2026-11-12 22:51:14 UTC epoch=1794523835: wrote=no part3_audio_age_s~2817 resume-press-1
- qsave 2026-11-12 22:52:31 UTC epoch=1794523914: wrote=no part3_audio_age_s~2895 resume-press-1
- qsave 2026-11-12 22:53:49 UTC epoch=1794523991: wrote=yes part3_audio_age_s~2973 resume-press-1
- health #5 2026-11-12 22:54:09 UTC epoch=1794524049: audio_bytes=1148848824 audio_s~2991 video_bytes=119799808 underruns_total=767 load=[0.17, 1.54, 2.28] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 22:55:01 UTC epoch=1794524062: wrote=no part3_audio_age_s~3045 resume-press-1
- qsave 2026-11-12 22:56:13 UTC epoch=1794524141: wrote=yes part3_audio_age_s~3117 resume-press-1
- qsave 2026-11-12 22:57:29 UTC epoch=1794524213: wrote=yes part3_audio_age_s~3193 resume-press-1
- qsave 2026-11-12 22:58:46 UTC epoch=1794524289: wrote=yes part3_audio_age_s~3270 resume-press-1
- qsave 2026-11-12 22:59:55 UTC epoch=1794524366: wrote=yes part3_audio_age_s~3339 resume-press-1
- qsave 2026-11-12 23:01:13 UTC epoch=1794524435: wrote=no part3_audio_age_s~3417 resume-press-1
- qsave 2026-11-12 23:02:22 UTC epoch=1794524513: wrote=yes part3_audio_age_s~3486 resume-press-1
- qsave 2026-11-12 23:03:31 UTC epoch=1794524582: wrote=yes part3_audio_age_s~3555 resume-press-1
- health #6 2026-11-12 23:03:54 UTC epoch=1794524634: audio_bytes=1373279024 audio_s~3576 video_bytes=147587072 underruns_total=839 load=[4.33, 2.52, 2.55] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 23:04:43 UTC epoch=1794524645: wrote=yes part3_audio_age_s~3627 resume-press-1
- qsave 2026-11-12 23:06:01 UTC epoch=1794524723: wrote=no part3_audio_age_s~3705 resume-press-1
- qsave 2026-11-12 23:07:19 UTC epoch=1794524801: wrote=no part3_audio_age_s~3783 resume-press-1
- qsave 2026-11-12 23:08:39 UTC epoch=1794524879: wrote=no part3_audio_age_s~3862 resume-press-1
- qsave 2026-11-12 23:09:59 UTC epoch=1794524959: wrote=no part3_audio_age_s~3943 resume-press-1
- qsave 2026-11-12 23:11:10 UTC epoch=1794525039: wrote=yes part3_audio_age_s~4014 resume-press-1
- qsave 2026-11-12 23:12:28 UTC epoch=1794525110: wrote=yes part3_audio_age_s~4092 resume-press-1
- health #7 2026-11-12 23:13:37 UTC epoch=1794525217: audio_bytes=1597255688 audio_s~4159 video_bytes=173539328 underruns_total=901 load=[3.85, 2.88, 2.60] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 23:13:38 UTC epoch=1794525188: wrote=yes part3_audio_age_s~4162 resume-press-1
- qsave 2026-11-12 23:14:23 UTC epoch=1794525239: wrote=no part3_audio_age_s~4207 
- qsave 2026-11-12 23:15:41 UTC epoch=1794525303: wrote=yes part3_audio_age_s~4285 resume-press-1
- qsave 2026-11-12 23:16:50 UTC epoch=1794525381: wrote=yes part3_audio_age_s~4354 resume-press-1
- qsave 2026-11-12 23:18:07 UTC epoch=1794525450: wrote=yes part3_audio_age_s~4431 resume-press-1
- qsave 2026-11-12 23:19:24 UTC epoch=1794525527: wrote=yes part3_audio_age_s~4508 resume-press-1
- qsave 2026-11-12 23:20:34 UTC epoch=1794525604: wrote=yes part3_audio_age_s~4578 resume-press-1
- qsave 2026-11-12 23:21:48 UTC epoch=1794525674: wrote=yes part3_audio_age_s~4652 resume-press-1
- qsave 2026-11-12 23:23:09 UTC epoch=1794525748: wrote=no part3_audio_age_s~4732 resume-press-1
- health #8 2026-11-12 23:23:34 UTC epoch=1794525814: audio_bytes=1826516000 audio_s~4756 video_bytes=197656576 underruns_total=977 load=[2.96, 2.76, 2.57] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 23:24:14 UTC epoch=1794525824: wrote=yes part3_audio_age_s~4798 resume-press-1
- qsave 2026-11-12 23:25:22 UTC epoch=1794525894: wrote=yes part3_audio_age_s~4866 resume-press-1
- qsave 2026-11-12 23:26:40 UTC epoch=1794525962: wrote=no part3_audio_age_s~4944 resume-press-1
- qsave 2026-11-12 23:27:56 UTC epoch=1794526040: wrote=yes part3_audio_age_s~5020 resume-press-1
- qsave 2026-11-12 23:29:11 UTC epoch=1794526116: wrote=yes part3_audio_age_s~5095 resume-press-1
- qsave 2026-11-12 23:30:20 UTC epoch=1794526191: wrote=yes part3_audio_age_s~5164 resume-press-1
- qsave 2026-11-12 23:31:36 UTC epoch=1794526260: wrote=yes part3_audio_age_s~5240 resume-press-1
- qsave 2026-11-12 23:32:52 UTC epoch=1794526336: wrote=yes part3_audio_age_s~5316 resume-press-1
- health #9 2026-11-12 23:33:16 UTC epoch=1794526396: audio_bytes=2049871072 audio_s~5338 video_bytes=223608832 underruns_total=1039 load=[1.29, 2.35, 2.40] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 23:33:54 UTC epoch=1794526406: wrote=yes part3_audio_age_s~5378 resume-press-1
- qsave 2026-11-12 23:35:10 UTC epoch=1794526474: wrote=yes part3_audio_age_s~5454 resume-press-1
- qsave 2026-11-12 23:36:20 UTC epoch=1794526551: wrote=yes part3_audio_age_s~5524 resume-press-1
- qsave 2026-11-12 23:37:29 UTC epoch=1794526620: wrote=yes part3_audio_age_s~5593 resume-press-1
- qsave 2026-11-12 23:38:38 UTC epoch=1794526689: wrote=yes part3_audio_age_s~5662 resume-press-1
- qsave 2026-11-12 23:39:47 UTC epoch=1794526758: wrote=yes part3_audio_age_s~5731 resume-press-1
- qsave 2026-11-12 23:41:08 UTC epoch=1794526827: wrote=yes part3_audio_age_s~5812 resume-press-1
- qsave 2026-11-12 23:42:19 UTC epoch=1794526908: wrote=yes part3_audio_age_s~5882 resume-press-1
- health #10 2026-11-12 23:42:57 UTC epoch=1794526977: audio_bytes=2273288072 audio_s~5920 video_bytes=247726080 underruns_total=1151 load=[0.34, 1.97, 2.33] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 23:44:10 UTC epoch=1794527023: wrote=yes part3_audio_age_s~5994 resume-press-1
- qsave 2026-11-12 23:45:17 UTC epoch=1794527090: wrote=yes part3_audio_age_s~6061 resume-press-1
- qsave 2026-11-12 23:46:34 UTC epoch=1794527157: wrote=no part3_audio_age_s~6138 resume-press-1
- qsave 2026-11-12 23:47:52 UTC epoch=1794527235: wrote=no part3_audio_age_s~6216 resume-press-1
- qsave 2026-11-12 23:49:01 UTC epoch=1794527312: wrote=yes part3_audio_age_s~6285 resume-press-1
- qsave 2026-11-12 23:50:13 UTC epoch=1794527381: wrote=yes part3_audio_age_s~6357 resume-press-1
- qsave 2026-11-12 23:51:20 UTC epoch=1794527453: wrote=yes part3_audio_age_s~6424 resume-press-1
- qsave 2026-11-12 23:52:27 UTC epoch=1794527520: wrote=yes part3_audio_age_s~6491 resume-press-1
- health #12 2026-11-12 23:53:15 UTC epoch=1794527595: audio_bytes=2510392608 audio_s~6537 video_bytes=287309824 underruns_total=1194 load=[2.44, 2.13, 2.37] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-12 23:54:02 UTC epoch=1794527605: wrote=yes part3_audio_age_s~6585 resume-press-1
- qsave 2026-11-12 23:55:09 UTC epoch=1794527682: wrote=yes part3_audio_age_s~6653 resume-press-1
- qsave 2026-11-12 23:56:20 UTC epoch=1794527749: wrote=yes part3_audio_age_s~6724 resume-press-1
- qsave 2026-11-12 23:57:28 UTC epoch=1794527820: wrote=yes part3_audio_age_s~6792 resume-press-1
- qsave 2026-11-12 23:58:37 UTC epoch=1794527888: wrote=yes part3_audio_age_s~6861 resume-press-1
- qsave 2026-11-12 23:59:54 UTC epoch=1794527957: wrote=yes part3_audio_age_s~6938 resume-press-1
- qsave 2026-11-13 00:01:03 UTC epoch=1794528034: wrote=yes part3_audio_age_s~7007 resume-press-1
- qsave 2026-11-13 00:02:15 UTC epoch=1794528103: wrote=yes part3_audio_age_s~7079 resume-press-1
- health #13 2026-11-13 00:02:58 UTC epoch=1794528178: audio_bytes=2734004424 audio_s~7119 video_bytes=325058560 underruns_total=1262 load=[3.60, 2.51, 2.43] quiet=[started_epoch=1794499060 restore_due_epoch=1794535060 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour ]
- qsave 2026-11-13 00:03:38 UTC epoch=1794528190: wrote=yes part3_audio_age_s~7162 resume-press-1
- qsave 2026-11-13 00:04:48 UTC epoch=1794528258: wrote=yes part3_audio_age_s~7232 resume-press-1
- qsave 2026-11-13 00:05:51 UTC epoch=1794528328: wrote=no part3_audio_age_s~7295 
- qsave 2026-11-13 00:07:08 UTC epoch=1794528391: wrote=yes part3_audio_age_s~7371 resume-press-1
- qsave 2026-11-13 00:08:24 UTC epoch=1794528468: wrote=yes part3_audio_age_s~7448 resume-press-1
- qsave 2026-11-13 00:09:32 UTC epoch=1794528544: wrote=yes part3_audio_age_s~7516 resume-press-1
- qsave 2026-11-13 00:10:41 UTC epoch=1794528612: wrote=yes part3_audio_age_s~7585 resume-press-1
- qsave 2026-11-13 00:11:51 UTC epoch=1794528682: wrote=yes part3_audio_age_s~7655 resume-press-1
- health #14 2026-11-13 00:12:41 UTC epoch=1794528761: audio_bytes=2958432848 audio_s~7704 video_bytes=358612992 underruns_total=1328 load=[2.93, 2.73, 2.51] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 00:13:27 UTC epoch=1794528770: wrote=yes part3_audio_age_s~7751 resume-press-1
- qsave 2026-11-13 00:14:46 UTC epoch=1794528847: wrote=no part3_audio_age_s~7829 resume-press-1

## VM RESTART #5 — part 5 ended (00:15 UTC)
- Fifth restart, ~00:15:5x UTC. SURVIVED: continuous-audio.part5.raw =
  7896.2 s (131.6 min, last write 00:15:51); video mkv last write
  00:15:50. Newest quick save 00:15:37 — 14 s before the end. Story
  frontier: Chapter 1-4 club room, Akiko conversation.
- Net story: P1 46.1 + P2 87.6 + P3 122.4 + P4 2.0 + P5 131.6 - ~13
  overlap = ~377 min (~6.3 h). Recovery #5 -> part 6.

## Part 6 (resume after VM restart #5)
- resumed from data_quick_01 (00:15:37 UTC) via START -> F12 (focused, first press); position = Ch.1-4 club room, Akiko. Chain was verified by the live sink-input + title state at relaunch.
- underrun count at part6 start: 3
- part6 audio_start_epoch=1794529120.5626435 (2026-11-13 00:18:40 UTC)
- part6 video_start_epoch=1794529120.565064 (2026-11-13 00:18:40 UTC)
- part6 video_minus_audio_offset_s=0.002
- qsave 2026-11-13 00:19:54 UTC epoch=1794529158: wrote=yes part3_audio_age_s~73 resume-press-1
- qsave 2026-11-13 00:21:12 UTC epoch=1794529234: wrote=no part3_audio_age_s~151 resume-press-1
- qsave 2026-11-13 00:22:19 UTC epoch=1794529312: wrote=yes part3_audio_age_s~218 resume-press-1
- qsave 2026-11-13 00:23:34 UTC epoch=1794529379: wrote=yes part3_audio_age_s~293 resume-press-1
- qsave 2026-11-13 00:24:50 UTC epoch=1794529454: wrote=yes part3_audio_age_s~369 resume-press-1
- qsave 2026-11-13 00:26:08 UTC epoch=1794529530: wrote=yes part3_audio_age_s~447 resume-press-1
- qsave 2026-11-13 00:27:21 UTC epoch=1794529608: wrote=yes part3_audio_age_s~520 resume-press-1
- qsave 2026-11-13 00:28:43 UTC epoch=1794529681: wrote=yes part3_audio_age_s~603 resume-press-1
- health #1 2026-11-13 00:28:50 UTC epoch=1794529730: audio_bytes=233442208 audio_s~607 video_bytes=23855104 underruns_total=221 load=[4.78, 2.48, 1.48] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 00:29:32 UTC epoch=1794529739: wrote=yes part3_audio_age_s~652 resume-press-1
- qsave 2026-11-13 00:30:54 UTC epoch=1794529812: wrote=yes part3_audio_age_s~733 resume-press-1
- qsave 2026-11-13 00:32:06 UTC epoch=1794529894: wrote=yes part3_audio_age_s~805 resume-press-1
- qsave 2026-11-13 00:33:19 UTC epoch=1794529966: wrote=yes part3_audio_age_s~878 resume-press-1
- qsave 2026-11-13 00:34:27 UTC epoch=1794530039: wrote=yes part3_audio_age_s~947 resume-press-1
- qsave 2026-11-13 00:35:35 UTC epoch=1794530107: wrote=yes part3_audio_age_s~1015 resume-press-1
- qsave 2026-11-13 00:36:51 UTC epoch=1794530175: wrote=yes part3_audio_age_s~1090 resume-press-1
- qsave 2026-11-13 00:38:00 UTC epoch=1794530251: wrote=yes part3_audio_age_s~1159 resume-press-1
- health #2 2026-11-13 00:38:31 UTC epoch=1794530311: audio_bytes=456540656 audio_s~1188 video_bytes=46137344 underruns_total=585 load=[3.99, 2.86, 2.27] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 00:39:13 UTC epoch=1794530326: wrote=yes part3_audio_age_s~1233 resume-press-1
- qsave 2026-11-13 00:40:30 UTC epoch=1794530394: wrote=yes part3_audio_age_s~1309 resume-press-1
- qsave 2026-11-13 00:41:49 UTC epoch=1794530470: wrote=no part3_audio_age_s~1388 resume-press-1
- qsave 2026-11-13 00:42:58 UTC epoch=1794530549: wrote=yes part3_audio_age_s~1457 resume-press-1
- qsave 2026-11-13 00:44:15 UTC epoch=1794530618: wrote=no part3_audio_age_s~1535 resume-press-1
- qsave 2026-11-13 00:45:33 UTC epoch=1794530696: wrote=yes part3_audio_age_s~1613 resume-press-1
- qsave 2026-11-13 00:46:43 UTC epoch=1794530774: wrote=yes part3_audio_age_s~1682 resume-press-1
- qsave 2026-11-13 00:47:58 UTC epoch=1794530843: wrote=no part3_audio_age_s~1757 resume-press-1
- health #3 2026-11-13 00:48:17 UTC epoch=1794530897: audio_bytes=681757384 audio_s~1775 video_bytes=74448896 underruns_total=639 load=[3.15, 2.72, 2.32] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 00:49:02 UTC epoch=1794530915: wrote=yes part3_audio_age_s~1821 resume-press-1
- qsave 2026-11-13 00:50:11 UTC epoch=1794530982: wrote=yes part3_audio_age_s~1890 resume-press-1
- qsave 2026-11-13 00:51:28 UTC epoch=1794531051: wrote=yes part3_audio_age_s~1967 resume-press-1
- qsave 2026-11-13 00:52:37 UTC epoch=1794531128: wrote=yes part3_audio_age_s~2036 resume-press-1
- qsave 2026-11-13 00:53:45 UTC epoch=1794531197: wrote=yes part3_audio_age_s~2105 resume-press-1
- qsave 2026-11-13 00:55:15 UTC epoch=1794531265: wrote=yes part3_audio_age_s~2195 resume-press-3
- qsave 2026-11-13 00:56:26 UTC epoch=1794531355: wrote=yes part3_audio_age_s~2265 resume-press-1
- qsave 2026-11-13 00:57:43 UTC epoch=1794531426: wrote=yes part3_audio_age_s~2343 resume-press-1
- health #4 2026-11-13 00:58:07 UTC epoch=1794531487: audio_bytes=908026808 audio_s~2364 video_bytes=94633984 underruns_total=697 load=[2.90, 2.95, 2.55] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 00:58:57 UTC epoch=1794531499: wrote=yes part3_audio_age_s~2417 resume-press-1
- qsave 2026-11-13 01:00:08 UTC epoch=1794531577: wrote=yes part3_audio_age_s~2487 resume-press-1
- qsave 2026-11-13 01:01:19 UTC epoch=1794531648: wrote=yes part3_audio_age_s~2558 resume-press-1
- qsave 2026-11-13 01:02:27 UTC epoch=1794531719: wrote=yes part3_audio_age_s~2626 resume-press-1
- qsave 2026-11-13 01:03:44 UTC epoch=1794531787: wrote=yes part3_audio_age_s~2703 resume-press-1
- qsave 2026-11-13 01:04:55 UTC epoch=1794531864: wrote=yes part3_audio_age_s~2774 resume-press-1
- qsave 2026-11-13 01:06:11 UTC epoch=1794531935: wrote=yes part3_audio_age_s~2850 resume-press-1
- qsave 2026-11-13 01:07:19 UTC epoch=1794532011: wrote=yes part3_audio_age_s~2918 resume-press-1
- health #5 2026-11-13 01:07:50 UTC epoch=1794532070: audio_bytes=1132340504 audio_s~2948 video_bytes=123207680 underruns_total=747 load=[0.66, 1.96, 2.23] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 01:08:28 UTC epoch=1794532080: wrote=yes part3_audio_age_s~2988 resume-press-1
- qsave 2026-11-13 01:09:36 UTC epoch=1794532148: wrote=yes part3_audio_age_s~3056 resume-press-1
- qsave 2026-11-13 01:10:54 UTC epoch=1794532216: wrote=yes part3_audio_age_s~3133 resume-press-1
- qsave 2026-11-13 01:12:11 UTC epoch=1794532294: wrote=yes part3_audio_age_s~3210 resume-press-1
- qsave 2026-11-13 01:13:20 UTC epoch=1794532371: wrote=yes part3_audio_age_s~3279 resume-press-1
- qsave 2026-11-13 01:14:28 UTC epoch=1794532440: wrote=yes part3_audio_age_s~3347 resume-press-1
- qsave 2026-11-13 01:15:36 UTC epoch=1794532508: wrote=yes part3_audio_age_s~3415 resume-press-1
- qsave 2026-11-13 01:16:43 UTC epoch=1794532576: wrote=yes part3_audio_age_s~3483 resume-press-1
- health #6 2026-11-13 01:17:31 UTC epoch=1794532651: audio_bytes=1355279304 audio_s~3529 video_bytes=148373504 underruns_total=809 load=[0.36, 1.92, 2.22] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 01:18:11 UTC epoch=1794532661: wrote=yes part3_audio_age_s~3570 resume-press-1
- qsave 2026-11-13 01:19:29 UTC epoch=1794532731: wrote=yes part3_audio_age_s~3648 resume-press-1
- qsave 2026-11-13 01:20:40 UTC epoch=1794532809: wrote=yes part3_audio_age_s~3719 resume-press-1
- qsave 2026-11-13 01:21:59 UTC epoch=1794532880: wrote=no part3_audio_age_s~3798 resume-press-1
- qsave 2026-11-13 01:23:10 UTC epoch=1794532959: wrote=yes part3_audio_age_s~3869 resume-press-1
- qsave 2026-11-13 01:24:19 UTC epoch=1794533030: wrote=yes part3_audio_age_s~3938 resume-press-1
- qsave 2026-11-13 01:25:28 UTC epoch=1794533099: wrote=yes part3_audio_age_s~4007 resume-press-1
- qsave 2026-11-13 01:26:37 UTC epoch=1794533168: wrote=yes part3_audio_age_s~4077 resume-press-1
- health #7 2026-11-13 01:27:13 UTC epoch=1794533233: audio_bytes=1578554632 audio_s~4110 video_bytes=173801472 underruns_total=867 load=[3.42, 2.22, 2.36] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 01:28:01 UTC epoch=1794533242: wrote=no part3_audio_age_s~4160 resume-press-1
- qsave 2026-11-13 01:29:10 UTC epoch=1794533321: wrote=yes part3_audio_age_s~4229 resume-press-1
- qsave 2026-11-13 01:30:19 UTC epoch=1794533390: wrote=yes part3_audio_age_s~4298 resume-press-1
- qsave 2026-11-13 01:31:29 UTC epoch=1794533459: wrote=yes part3_audio_age_s~4368 resume-press-1
- qsave 2026-11-13 01:32:49 UTC epoch=1794533529: wrote=no part3_audio_age_s~4448 resume-press-1
- qsave 2026-11-13 01:34:11 UTC epoch=1794533609: wrote=no part3_audio_age_s~4530 resume-press-1
- qsave 2026-11-13 01:35:19 UTC epoch=1794533691: wrote=yes part3_audio_age_s~4599 resume-press-1
- qsave 2026-11-13 01:36:27 UTC epoch=1794533759: wrote=yes part3_audio_age_s~4666 resume-press-1
- health #8 2026-11-13 01:36:54 UTC epoch=1794533814: audio_bytes=1801807920 audio_s~4692 video_bytes=199491584 underruns_total=933 load=[4.56, 2.90, 2.59] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 01:37:43 UTC epoch=1794533826: wrote=yes part3_audio_age_s~4743 resume-press-1
- qsave 2026-11-13 01:38:51 UTC epoch=1794533903: wrote=yes part3_audio_age_s~4811 resume-press-1
- qsave 2026-11-13 01:39:59 UTC epoch=1794533971: wrote=yes part3_audio_age_s~4878 resume-press-1
- qsave 2026-11-13 01:41:15 UTC epoch=1794534039: wrote=yes part3_audio_age_s~4954 resume-press-1
- qsave 2026-11-13 01:42:24 UTC epoch=1794534115: wrote=yes part3_audio_age_s~5024 resume-press-1
- qsave 2026-11-13 01:43:42 UTC epoch=1794534184: wrote=yes part3_audio_age_s~5101 resume-press-1
- qsave 2026-11-13 01:45:02 UTC epoch=1794534262: wrote=no part3_audio_age_s~5182 resume-press-1
- qsave 2026-11-13 01:46:19 UTC epoch=1794534342: wrote=yes part3_audio_age_s~5259 resume-press-1
- health #9 2026-11-13 01:46:37 UTC epoch=1794534397: audio_bytes=2025781144 audio_s~5275 video_bytes=227016704 underruns_total=997 load=[2.94, 2.70, 2.59] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 01:47:14 UTC epoch=1794534405: wrote=yes part3_audio_age_s~5313 resume-press-1
- qsave 2026-11-13 01:48:25 UTC epoch=1794534474: wrote=yes part3_audio_age_s~5384 resume-press-1
- qsave 2026-11-13 01:49:35 UTC epoch=1794534545: wrote=yes part3_audio_age_s~5454 resume-press-1
- qsave 2026-11-13 01:50:53 UTC epoch=1794534615: wrote=yes part3_audio_age_s~5533 resume-press-1
- qsave 2026-11-13 01:52:13 UTC epoch=1794534693: wrote=yes part3_audio_age_s~5612 resume-press-1
- qsave 2026-11-13 01:53:23 UTC epoch=1794534773: wrote=yes part3_audio_age_s~5682 resume-press-1
- qsave 2026-11-13 01:54:43 UTC epoch=1794534843: wrote=no part3_audio_age_s~5763 resume-press-1
- qsave 2026-11-13 01:56:02 UTC epoch=1794534923: wrote=yes part3_audio_age_s~5841 resume-press-1
- health #10 2026-11-13 01:56:16 UTC epoch=1794534976: audio_bytes=2248048584 audio_s~5854 video_bytes=251658240 underruns_total=1069 load=[2.97, 2.99, 2.66] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 01:57:02 UTC epoch=1794534984: wrote=no part3_audio_age_s~5902 resume-press-1
- qsave 2026-11-13 01:58:12 UTC epoch=1794535062: wrote=yes part3_audio_age_s~5971 resume-press-1
- qsave 2026-11-13 01:59:30 UTC epoch=1794535132: wrote=yes part3_audio_age_s~6049 resume-press-1
- qsave 2026-11-13 02:00:40 UTC epoch=1794535210: wrote=yes part3_audio_age_s~6119 resume-press-1
- qsave 2026-11-13 02:01:58 UTC epoch=1794535280: wrote=yes part3_audio_age_s~6197 resume-press-1
- qsave 2026-11-13 02:03:08 UTC epoch=1794535358: wrote=yes part3_audio_age_s~6268 resume-press-1
- qsave 2026-11-13 02:04:20 UTC epoch=1794535428: wrote=yes part3_audio_age_s~6339 resume-press-1
- qsave 2026-11-13 02:05:27 UTC epoch=1794535500: wrote=yes part3_audio_age_s~6407 resume-press-1
- health #11 2026-11-13 02:05:56 UTC epoch=1794535556: audio_bytes=2470674888 audio_s~6434 video_bytes=278659072 underruns_total=1133 load=[1.11, 2.39, 2.48] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 02:06:39 UTC epoch=1794535569: wrote=yes part3_audio_age_s~6479 resume-press-1
- qsave 2026-11-13 02:07:57 UTC epoch=1794535640: wrote=yes part3_audio_age_s~6556 resume-press-1
- qsave 2026-11-13 02:09:08 UTC epoch=1794535717: wrote=yes part3_audio_age_s~6627 resume-press-1
- qsave 2026-11-13 02:10:20 UTC epoch=1794535788: wrote=yes part3_audio_age_s~6699 resume-press-1
- qsave 2026-11-13 02:11:31 UTC epoch=1794535860: wrote=yes part3_audio_age_s~6770 resume-press-1
- qsave 2026-11-13 02:12:40 UTC epoch=1794535931: wrote=yes part3_audio_age_s~6840 resume-press-1
- qsave 2026-11-13 02:13:58 UTC epoch=1794536000: wrote=no part3_audio_age_s~6917 resume-press-1
- qsave 2026-11-13 02:15:15 UTC epoch=1794536078: wrote=no part3_audio_age_s~6995 resume-press-1
- health #12 2026-11-13 02:15:40 UTC epoch=1794536140: audio_bytes=2695152344 audio_s~7018 video_bytes=307232768 underruns_total=1209 load=[0.41, 1.86, 2.28] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 02:16:23 UTC epoch=1794536154: wrote=yes part3_audio_age_s~7063 resume-press-1
- qsave 2026-11-13 02:17:39 UTC epoch=1794536223: wrote=yes part3_audio_age_s~7139 resume-press-1
- qsave 2026-11-13 02:18:57 UTC epoch=1794536299: wrote=yes part3_audio_age_s~7216 resume-press-1
- qsave 2026-11-13 02:20:06 UTC epoch=1794536377: wrote=yes part3_audio_age_s~7285 resume-press-1
- qsave 2026-11-13 02:21:23 UTC epoch=1794536446: wrote=yes part3_audio_age_s~7363 resume-press-1
- qsave 2026-11-13 02:22:42 UTC epoch=1794536523: wrote=yes part3_audio_age_s~7441 resume-press-1
- qsave 2026-11-13 02:24:03 UTC epoch=1794536602: wrote=no part3_audio_age_s~7522 resume-press-1
- qsave 2026-11-13 02:25:20 UTC epoch=1794536683: wrote=yes part3_audio_age_s~7599 resume-press-1
- health #13 2026-11-13 02:25:25 UTC epoch=1794536725: audio_bytes=2919754216 audio_s~7603 video_bytes=331612160 underruns_total=1275 load=[4.16, 2.22, 2.31] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 02:26:23 UTC epoch=1794536741: wrote=no part3_audio_age_s~7662 resume-press-1
- qsave 2026-11-13 02:27:31 UTC epoch=1794536823: wrote=yes part3_audio_age_s~7730 resume-press-1
- qsave 2026-11-13 02:28:46 UTC epoch=1794536891: wrote=yes part3_audio_age_s~7805 resume-press-1
- qsave 2026-11-13 02:30:01 UTC epoch=1794536966: wrote=yes part3_audio_age_s~7880 resume-press-1
- qsave 2026-11-13 02:31:16 UTC epoch=1794537041: wrote=yes part3_audio_age_s~7956 resume-press-1
- qsave 2026-11-13 02:32:34 UTC epoch=1794537116: wrote=no part3_audio_age_s~8033 resume-press-1
- qsave 2026-11-13 02:33:43 UTC epoch=1794537194: wrote=yes part3_audio_age_s~8102 resume-press-1
- qsave 2026-11-13 02:35:01 UTC epoch=1794537263: wrote=yes part3_audio_age_s~8180 resume-press-1
- health #14 2026-11-13 02:35:12 UTC epoch=1794537312: audio_bytes=3145228080 audio_s~8190 video_bytes=359137280 underruns_total=1337 load=[5.18, 3.04, 2.61] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 02:36:04 UTC epoch=1794537325: wrote=yes part3_audio_age_s~8243 resume-press-1
- qsave 2026-11-13 02:37:11 UTC epoch=1794537404: wrote=no part3_audio_age_s~8310 
- qsave 2026-11-13 02:38:17 UTC epoch=1794537471: wrote=no part3_audio_age_s~8377 

## VM RESTART #6 — part 6 ended (02:38 UTC)
- Sixth restart, ~02:38:5x UTC. SURVIVED: continuous-audio.part6.raw =
  8406.7 s (140.1 min, last write 02:38:47); video mkv 02:38:46. Newest
  quick save 02:35:44 — this splice replays ~3 min (the part-6 tail
  itself is intact in the recording; part 7 will overlap it). Story
  frontier: Chapter 1-5 cafe, the light/magic event.
- Net story: P1 46.1 + P2 87.6 + P3 122.4 + P4 2.0 + P5 131.6 + P6 140.1
  - ~13 overlap = ~517 min (~8.6 h). Recovery #6 -> part 7.

## Part 7 (resume after VM restart #6)
- resumed from data_quick_01 (02:35:44 UTC) via START -> F12 (focused, second press); position = Ch.1-5 cafe, just before the light event (part 7 overlaps part 6's last ~3 min).
- underrun count at part7 start: 3
- part7 audio_start_epoch=1794537723.574725 (2026-11-13 02:42:03 UTC)
- part7 video_start_epoch=1794537723.5768557 (2026-11-13 02:42:03 UTC)
- part7 video_minus_audio_offset_s=0.002
- qsave 2026-11-13 02:43:13 UTC epoch=1794537765: wrote=yes part3_audio_age_s~69 resume-press-1
- qsave 2026-11-13 02:44:21 UTC epoch=1794537833: wrote=yes part3_audio_age_s~137 resume-press-1
- qsave 2026-11-13 02:45:27 UTC epoch=1794537901: wrote=yes part3_audio_age_s~204 resume-press-1
- qsave 2026-11-13 02:46:35 UTC epoch=1794537967: wrote=yes part3_audio_age_s~271 resume-press-1
- qsave 2026-11-13 02:47:41 UTC epoch=1794538035: wrote=yes part3_audio_age_s~338 resume-press-1
- qsave 2026-11-13 02:48:48 UTC epoch=1794538101: wrote=yes part3_audio_age_s~405 resume-press-1
- qsave 2026-11-13 02:50:04 UTC epoch=1794538168: wrote=yes part3_audio_age_s~480 resume-press-1
- qsave 2026-11-13 02:51:21 UTC epoch=1794538244: wrote=yes part3_audio_age_s~557 resume-press-1
- health #1 2026-11-13 02:52:17 UTC epoch=1794538337: audio_bytes=235081456 audio_s~612 video_bytes=26214400 underruns_total=86 load=[1.46, 2.30, 1.43] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 02:52:51 UTC epoch=1794538348: wrote=no part3_audio_age_s~647 
- qsave 2026-11-13 02:54:14 UTC epoch=1794538411: wrote=no part3_audio_age_s~730 resume-press-1
- qsave 2026-11-13 02:55:37 UTC epoch=1794538494: wrote=yes part3_audio_age_s~813 resume-press-1
- qsave 2026-11-13 02:57:00 UTC epoch=1794538577: wrote=no part3_audio_age_s~896 resume-press-1
- qsave 2026-11-13 02:58:23 UTC epoch=1794538660: wrote=no part3_audio_age_s~979 resume-press-1
- qsave 2026-11-13 02:59:37 UTC epoch=1794538743: wrote=yes part3_audio_age_s~1054 resume-press-1
- qsave 2026-11-13 03:00:46 UTC epoch=1794538817: wrote=yes part3_audio_age_s~1122 resume-press-1
- health #2 2026-11-13 03:01:59 UTC epoch=1794538919: audio_bytes=458638984 audio_s~1194 video_bytes=53477376 underruns_total=554 load=[0.78, 2.28, 1.97] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 03:02:06 UTC epoch=1794538886: wrote=no part3_audio_age_s~1202 resume-press-1
- qsave 2026-11-13 03:03:27 UTC epoch=1794538979: wrote=yes part3_audio_age_s~1283 resume-press-1
- qsave 2026-11-13 03:04:44 UTC epoch=1794539047: wrote=yes part3_audio_age_s~1360 resume-press-1
- qsave 2026-11-13 03:06:01 UTC epoch=1794539124: wrote=no part3_audio_age_s~1437 resume-press-1
- qsave 2026-11-13 03:07:20 UTC epoch=1794539201: wrote=no part3_audio_age_s~1516 resume-press-1
- qsave 2026-11-13 03:08:31 UTC epoch=1794539280: wrote=yes part3_audio_age_s~1587 resume-press-1
- qsave 2026-11-13 03:09:41 UTC epoch=1794539351: wrote=yes part3_audio_age_s~1657 resume-press-1
- qsave 2026-11-13 03:11:01 UTC epoch=1794539421: wrote=no part3_audio_age_s~1737 resume-press-1
- qsave 2026-11-13 03:12:19 UTC epoch=1794539501: wrote=yes part3_audio_age_s~1815 resume-press-1
- health #3 2026-11-13 03:12:30 UTC epoch=1794539550: audio_bytes=700887576 audio_s~1825 video_bytes=77856768 underruns_total=622 load=[2.96, 2.27, 2.21] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 03:13:19 UTC epoch=1794539563: wrote=yes part3_audio_age_s~1876 resume-press-1
- qsave 2026-11-13 03:14:28 UTC epoch=1794539640: wrote=yes part3_audio_age_s~1944 resume-press-1
- qsave 2026-11-13 03:15:50 UTC epoch=1794539708: wrote=no part3_audio_age_s~2026 resume-press-1
- qsave 2026-11-13 03:17:07 UTC epoch=1794539790: wrote=yes part3_audio_age_s~2103 resume-press-1
- qsave 2026-11-13 03:18:24 UTC epoch=1794539867: wrote=yes part3_audio_age_s~2181 resume-press-1
- qsave 2026-11-13 03:19:33 UTC epoch=1794539944: wrote=yes part3_audio_age_s~2248 resume-press-1
- qsave 2026-11-13 03:20:42 UTC epoch=1794540013: wrote=yes part3_audio_age_s~2318 resume-press-1
- qsave 2026-11-13 03:22:00 UTC epoch=1794540082: wrote=yes part3_audio_age_s~2396 resume-press-1
- health #4 2026-11-13 03:22:15 UTC epoch=1794540135: audio_bytes=925236112 audio_s~2409 video_bytes=99614720 underruns_total=690 load=[3.72, 2.78, 2.50] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 03:24:00 UTC epoch=1794540202: wrote=yes part3_audio_age_s~2516 resume-press-1
- qsave 2026-11-13 03:25:09 UTC epoch=1794540280: wrote=yes part3_audio_age_s~2586 resume-press-1
- qsave 2026-11-13 03:26:28 UTC epoch=1794540349: wrote=no part3_audio_age_s~2664 resume-press-1
- qsave 2026-11-13 03:27:38 UTC epoch=1794540428: wrote=yes part3_audio_age_s~2735 resume-press-1
- qsave 2026-11-13 03:28:58 UTC epoch=1794540498: wrote=yes part3_audio_age_s~2814 resume-press-1
- qsave 2026-11-13 03:30:15 UTC epoch=1794540578: wrote=yes part3_audio_age_s~2892 resume-press-1
- qsave 2026-11-13 03:31:33 UTC epoch=1794540655: wrote=yes part3_audio_age_s~2969 resume-press-1
- qsave 2026-11-13 03:32:51 UTC epoch=1794540733: wrote=yes part3_audio_age_s~3047 resume-press-1
- health #5 2026-11-13 03:32:53 UTC epoch=1794540773: audio_bytes=1170763512 audio_s~3048 video_bytes=119537664 underruns_total=745 load=[2.55, 2.52, 2.46] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 03:33:40 UTC epoch=1794540782: wrote=yes part3_audio_age_s~3096 resume-press-1
- qsave 2026-11-13 03:34:47 UTC epoch=1794540860: wrote=yes part3_audio_age_s~3163 resume-press-1
- qsave 2026-11-13 03:36:03 UTC epoch=1794540927: wrote=yes part3_audio_age_s~3239 resume-press-1
- qsave 2026-11-13 03:37:12 UTC epoch=1794541003: wrote=yes part3_audio_age_s~3308 resume-press-1
- qsave 2026-11-13 03:38:20 UTC epoch=1794541072: wrote=yes part3_audio_age_s~3377 resume-press-1
- qsave 2026-11-13 03:39:38 UTC epoch=1794541140: wrote=yes part3_audio_age_s~3454 resume-press-1
- qsave 2026-11-13 03:40:48 UTC epoch=1794541218: wrote=yes part3_audio_age_s~3524 resume-press-1
- qsave 2026-11-13 03:42:00 UTC epoch=1794541288: wrote=yes part3_audio_age_s~3596 resume-press-1
- health #6 2026-11-13 03:42:34 UTC epoch=1794541354: audio_bytes=1393327664 audio_s~3628 video_bytes=138149888 underruns_total=811 load=[1.19, 2.24, 2.31] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 03:43:10 UTC epoch=1794541362: wrote=yes part3_audio_age_s~3666 resume-press-1
- qsave 2026-11-13 03:44:32 UTC epoch=1794541430: wrote=yes part3_audio_age_s~3748 resume-press-3
- qsave 2026-11-13 03:46:02 UTC epoch=1794541512: wrote=yes part3_audio_age_s~3839 resume-press-3
- qsave 2026-11-13 03:47:19 UTC epoch=1794541602: wrote=yes part3_audio_age_s~3915 resume-press-1
- qsave 2026-11-13 03:48:36 UTC epoch=1794541679: wrote=yes part3_audio_age_s~3992 resume-press-1
- qsave 2026-11-13 03:49:46 UTC epoch=1794541756: wrote=yes part3_audio_age_s~4062 resume-press-1
- qsave 2026-11-13 03:51:03 UTC epoch=1794541826: wrote=yes part3_audio_age_s~4139 resume-press-1
- health #7 2026-11-13 03:52:13 UTC epoch=1794541933: audio_bytes=1616052848 audio_s~4208 video_bytes=164888576 underruns_total=865 load=[0.76, 2.14, 2.28] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 03:52:20 UTC epoch=1794541903: wrote=yes part3_audio_age_s~4217 resume-press-1
- qsave 2026-11-13 03:52:52 UTC epoch=1794541943: wrote=yes part3_audio_age_s~4248 resume-press-1
- qsave 2026-11-13 03:54:09 UTC epoch=1794542012: wrote=yes part3_audio_age_s~4326 resume-press-1
- qsave 2026-11-13 03:55:28 UTC epoch=1794542089: wrote=no part3_audio_age_s~4404 resume-press-1
- qsave 2026-11-13 03:56:38 UTC epoch=1794542168: wrote=yes part3_audio_age_s~4474 resume-press-1
- qsave 2026-11-13 03:57:56 UTC epoch=1794542238: wrote=yes part3_audio_age_s~4552 resume-press-1
- qsave 2026-11-13 03:59:06 UTC epoch=1794542316: wrote=yes part3_audio_age_s~4622 resume-press-1
- qsave 2026-11-13 04:00:07 UTC epoch=1794542386: wrote=no part3_audio_age_s~4684 
- qsave 2026-11-13 04:01:21 UTC epoch=1794542448: wrote=yes part3_audio_age_s~4757 resume-press-1
- health #8 2026-11-13 04:01:54 UTC epoch=1794542514: audio_bytes=1839131632 audio_s~4789 video_bytes=189005824 underruns_total=931 load=[1.67, 1.82, 2.18] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 04:02:30 UTC epoch=1794542521: wrote=yes part3_audio_age_s~4826 resume-press-1
- qsave 2026-11-13 04:03:39 UTC epoch=1794542590: wrote=yes part3_audio_age_s~4896 resume-press-1
- qsave 2026-11-13 04:04:49 UTC epoch=1794542659: wrote=yes part3_audio_age_s~4965 resume-press-1
- qsave 2026-11-13 04:06:00 UTC epoch=1794542729: wrote=yes part3_audio_age_s~5036 resume-press-1
- qsave 2026-11-13 04:07:20 UTC epoch=1794542800: wrote=yes part3_audio_age_s~5116 resume-press-1
- qsave 2026-11-13 04:08:36 UTC epoch=1794542880: wrote=no part3_audio_age_s~5192 resume-press-1
- qsave 2026-11-13 04:09:47 UTC epoch=1794542956: wrote=yes part3_audio_age_s~5263 resume-press-1
- qsave 2026-11-13 04:10:49 UTC epoch=1794543027: wrote=no part3_audio_age_s~5325 
- health #9 2026-11-13 04:11:32 UTC epoch=1794543092: audio_bytes=2061238168 audio_s~5367 video_bytes=216530944 underruns_total=991 load=[3.17, 2.40, 2.37] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 04:12:08 UTC epoch=1794543099: wrote=yes part3_audio_age_s~5404 resume-press-1
- qsave 2026-11-13 04:13:25 UTC epoch=1794543168: wrote=yes part3_audio_age_s~5481 resume-press-1
- qsave 2026-11-13 04:14:42 UTC epoch=1794543245: wrote=yes part3_audio_age_s~5558 resume-press-1
- qsave 2026-11-13 04:15:51 UTC epoch=1794543322: wrote=yes part3_audio_age_s~5627 resume-press-1
- qsave 2026-11-13 04:17:10 UTC epoch=1794543391: wrote=yes part3_audio_age_s~5706 resume-press-1
- qsave 2026-11-13 04:18:19 UTC epoch=1794543470: wrote=yes part3_audio_age_s~5775 resume-press-1
- qsave 2026-11-13 04:19:39 UTC epoch=1794543539: wrote=no part3_audio_age_s~5855 resume-press-1
- qsave 2026-11-13 04:20:48 UTC epoch=1794543619: wrote=yes part3_audio_age_s~5925 resume-press-1
- health #10 2026-11-13 04:21:10 UTC epoch=1794543670: audio_bytes=2282967080 audio_s~5945 video_bytes=241434624 underruns_total=1049 load=[4.30, 2.77, 2.50] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 04:21:57 UTC epoch=1794543678: wrote=no part3_audio_age_s~5994 resume-press-1
- qsave 2026-11-13 04:23:05 UTC epoch=1794543758: wrote=yes part3_audio_age_s~6062 resume-press-1
- qsave 2026-11-13 04:24:23 UTC epoch=1794543826: wrote=yes part3_audio_age_s~6139 resume-press-1
- qsave 2026-11-13 04:25:40 UTC epoch=1794543903: wrote=yes part3_audio_age_s~6216 resume-press-1
- qsave 2026-11-13 04:26:57 UTC epoch=1794543980: wrote=yes part3_audio_age_s~6293 resume-press-1

## PART FINALIZATION RECORDS (per KK rule 2026-11-13 13:26 — parts upload individually)
Audio seconds are EXACT (raw float32 48kHz stereo = 384000 B/s). Video
duration is the ffprobe header value; parts cut by VM restarts have no
finalized header (N/A) — take their video length from frame timestamps
at mux time. Offsets: video start minus audio start.

### Part 1 — FINAL (VM restart #1)
- files: continuous-video.mkv / continuous-audio.raw
- audio_start_epoch=1794503760.831, video_start_epoch=1794503760.833, offset_s=+0.002
- video_duration_s=2765.850 (ffprobe), audio_s=2767.562
- frontier: Chapter 1-2, school hallway / Nene entrance stretch (part 2
  resumes from the 33.2-min boundary save inside this part's span)

### Part 2 — FINAL (VM restart #2)
- files: continuous-video.part2.mkv / continuous-audio.part2.raw
- audio_start_epoch=1794506962.058, video_start_epoch=1794506962.068, offset_s=+0.010
- video_duration_s=N/A (unfinalized header), audio_s=5255.176
- frontier: Chapter 1-2, library scene; last line at newest save
  (19:35:53 UTC): Shuuji "それなら多分。わからないことが出たら、訊いてもいいんだよね？"

### Part 3 — FINAL (VM restart #3)
- files: continuous-video.part3.mkv / continuous-audio.part3.raw
- audio_start_epoch=1794513051.885, video_start_epoch=1794513051.886, offset_s=+0.002
- video_duration_s=N/A (unfinalized header), audio_s=7345.704
- frontier: Chapter 1-4, classroom — Kanae (teacher) introduction scene
  (newest save 21:52:14 UTC)

### Part 4 — FINAL fragment (VM restart #4, ~6 min after start)
- files: continuous-video.part4.mkv / continuous-audio.part4.raw
- audio_start_epoch=1794520632.632, video_start_epoch=1794520632.635, offset_s=+0.003
- video_duration_s=N/A (unfinalized header), audio_s=118.259
- frontier: same Chapter 1-4 Kanae classroom scene (save 21:58:19 UTC);
  fully overlapped by part 5 — splice note: part 4 may be skipped in
  assembly, part 5 covers this span from the same save.

### Part 5 — FINAL (VM restart #5)
- files: continuous-video.part5.mkv / continuous-audio.part5.raw
- audio_start_epoch=1794521055.928, video_start_epoch=1794521055.934, offset_s=+0.006
- video_duration_s=N/A (unfinalized header), audio_s=7895.972
- frontier: Chapter 1-4, occult club room — Akiko conversation (Shuuji
  on the feelings carried through his power); newest save 00:15:37 UTC,
  14 s before the cut.

### Part 6 — FINAL (VM restart #6)
- files: continuous-video.part6.mkv / continuous-audio.part6.raw
- audio_start_epoch=1794529120.563, video_start_epoch=1794529120.565, offset_s=+0.002
- video_duration_s=N/A (unfinalized header), audio_s=8406.746
- frontier: Chapter 1-5, cafe Schwarz Katze — the light event
  (white-flash) and its immediate aftermath; newest save 02:35:44 UTC
  sits ~3 min before the cut, so part 7 overlaps the flash span.

### Part 7 — FINAL (VM restart #7)
- files: continuous-video.part7.mkv / continuous-audio.part7.raw
- audio_start_epoch=1794537723.575, video_start_epoch=1794537723.577, offset_s=+0.002
- video_duration_s=N/A (unfinalized header), audio_s=8957.769
- frontier: Chapter 2-1 — Wakaba hallway/classroom stretch; newest
  quick save 05:11:02 UTC, 19 s before the cut.
- qsave 2026-11-13 04:28:08 UTC epoch=1794544057: wrote=yes part3_audio_age_s~6364 resume-press-1
- qsave 2026-11-13 04:29:24 UTC epoch=1794544128: wrote=yes part3_audio_age_s~6441 resume-press-1
- qsave 2026-11-13 04:30:42 UTC epoch=1794544204: wrote=yes part3_audio_age_s~6518 resume-press-1
- health #11 2026-11-13 04:30:49 UTC epoch=1794544249: audio_bytes=2505378328 audio_s~6524 video_bytes=262668288 underruns_total=1127 load=[3.08, 3.40, 2.85] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 04:31:27 UTC epoch=1794544257: wrote=yes part3_audio_age_s~6563 resume-press-1
- qsave 2026-11-13 04:32:38 UTC epoch=1794544327: wrote=yes part3_audio_age_s~6634 resume-press-1
- qsave 2026-11-13 04:33:46 UTC epoch=1794544398: wrote=yes part3_audio_age_s~6702 resume-press-1
- qsave 2026-11-13 04:34:57 UTC epoch=1794544466: wrote=yes part3_audio_age_s~6773 resume-press-1
- qsave 2026-11-13 04:36:14 UTC epoch=1794544537: wrote=yes part3_audio_age_s~6850 resume-press-1
- qsave 2026-11-13 04:37:17 UTC epoch=1794544614: wrote=no part3_audio_age_s~6913 
- qsave 2026-11-13 04:38:34 UTC epoch=1794544677: wrote=yes part3_audio_age_s~6990 resume-press-1
- qsave 2026-11-13 04:39:43 UTC epoch=1794544754: wrote=yes part3_audio_age_s~7059 resume-press-1
- health #12 2026-11-13 04:40:29 UTC epoch=1794544829: audio_bytes=2727829328 audio_s~7103 video_bytes=285999104 underruns_total=1195 load=[1.32, 2.79, 2.78] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 04:41:14 UTC epoch=1794544836: wrote=yes part3_audio_age_s~7151 resume-press-1
- qsave 2026-11-13 04:42:23 UTC epoch=1794544915: wrote=yes part3_audio_age_s~7220 resume-press-1
- qsave 2026-11-13 04:43:41 UTC epoch=1794544983: wrote=yes part3_audio_age_s~7297 resume-press-1
- qsave 2026-11-13 04:44:51 UTC epoch=1794545061: wrote=yes part3_audio_age_s~7367 resume-press-1
- qsave 2026-11-13 04:46:00 UTC epoch=1794545131: wrote=yes part3_audio_age_s~7436 resume-press-1
- qsave 2026-11-13 04:47:17 UTC epoch=1794545200: wrote=yes part3_audio_age_s~7513 resume-press-1
- qsave 2026-11-13 04:48:36 UTC epoch=1794545277: wrote=no part3_audio_age_s~7592 resume-press-1
- qsave 2026-11-13 04:49:45 UTC epoch=1794545356: wrote=yes part3_audio_age_s~7662 resume-press-1
- health #13 2026-11-13 04:50:08 UTC epoch=1794545408: audio_bytes=2950040280 audio_s~7682 video_bytes=305922048 underruns_total=1289 load=[0.88, 2.43, 2.66] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 04:50:45 UTC epoch=1794545416: wrote=yes part3_audio_age_s~7721 resume-press-1
- qsave 2026-11-13 04:51:54 UTC epoch=1794545485: wrote=yes part3_audio_age_s~7790 resume-press-1
- qsave 2026-11-13 04:53:03 UTC epoch=1794545554: wrote=yes part3_audio_age_s~7860 resume-press-1
- qsave 2026-11-13 04:54:12 UTC epoch=1794545623: wrote=yes part3_audio_age_s~7928 resume-press-1
- qsave 2026-11-13 04:55:19 UTC epoch=1794545692: wrote=yes part3_audio_age_s~7995 resume-press-1
- qsave 2026-11-13 04:56:37 UTC epoch=1794545759: wrote=yes part3_audio_age_s~8073 resume-press-1
- qsave 2026-11-13 04:57:47 UTC epoch=1794545837: wrote=yes part3_audio_age_s~8143 resume-press-1
- qsave 2026-11-13 04:59:04 UTC epoch=1794545907: wrote=yes part3_audio_age_s~8220 resume-press-1
- health #14 2026-11-13 04:59:49 UTC epoch=1794545989: audio_bytes=3173099000 audio_s~8263 video_bytes=329777152 underruns_total=1519 load=[0.57, 2.22, 2.73] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 05:00:30 UTC epoch=1794545997: wrote=yes part3_audio_age_s~8306 resume-press-1
- qsave 2026-11-13 05:01:45 UTC epoch=1794546070: wrote=yes part3_audio_age_s~8382 resume-press-1
- qsave 2026-11-13 05:02:55 UTC epoch=1794546145: wrote=yes part3_audio_age_s~8451 resume-press-1
- qsave 2026-11-13 05:04:13 UTC epoch=1794546215: wrote=yes part3_audio_age_s~8529 resume-press-1
- qsave 2026-11-13 05:05:30 UTC epoch=1794546293: wrote=no part3_audio_age_s~8606 resume-press-1
- qsave 2026-11-13 05:06:38 UTC epoch=1794546370: wrote=yes part3_audio_age_s~8674 resume-press-1
- qsave 2026-11-13 05:07:55 UTC epoch=1794546438: wrote=yes part3_audio_age_s~8751 resume-press-1
- qsave 2026-11-13 05:09:12 UTC epoch=1794546515: wrote=no part3_audio_age_s~8829 resume-press-1
- health #15 2026-11-13 05:09:29 UTC epoch=1794546569: audio_bytes=3395977056 audio_s~8843 video_bytes=357040128 underruns_total=1761 load=[4.53, 3.30, 3.31] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 05:10:12 UTC epoch=1794546576: wrote=yes part3_audio_age_s~8888 resume-press-1

## VM RESTART #7 — part 7 ended (05:11 UTC)
- Seventh restart, ~05:11:3x UTC (it also interrupted this line's exec
  service mid-command). SURVIVED: continuous-audio.part7.raw = 8957.769 s
  (149.3 min, last write 05:11:21); video mkv intact. Newest quick save 05:11:02 UTC — 19 s before the cut. Story
  frontier: Chapter 2-1 (Wakaba hallway / classroom stretch).
- Net story: P1 46.1 + P2 87.6 + P3 122.4 + P4 2.0 + P5 131.6 + P6 140.1
  + P7 149.3 - ~16 overlaps = ~663 min (~11.1 h). Recovery #7 -> part 8.

## Part 8 (resume after VM restart #7)
- resumed from data_quick_01 (05:11:02 UTC) via START -> F12 (focused, second press); position = Ch.2-1 hallway, Wakaba. Title + sink-input verified at relaunch.
- underrun count at part8 start: 325
- part8 audio_start_epoch=1794547012.744517 (2026-11-13 05:16:52 UTC)
- part8 video_start_epoch=1794547012.7485535 (2026-11-13 05:16:52 UTC)
- part8 video_minus_audio_offset_s=0.004

### Part 8 — RECORDING (finalizes at next cut / take end)
- files: continuous-video.part8.mkv / continuous-audio.part8.raw
- audio_start_epoch=1794547012.744517104, video_start_epoch=1794547012.748553609
- qsave 2026-11-13 05:18:24 UTC epoch=1794547052: wrote=no part3_audio_age_s~91 resume-press-2
- qsave 2026-11-13 05:19:54 UTC epoch=1794547144: wrote=yes part3_audio_age_s~180 resume-press-2
- qsave 2026-11-13 05:21:11 UTC epoch=1794547234: wrote=yes part3_audio_age_s~258 resume-press-1
- qsave 2026-11-13 05:22:20 UTC epoch=1794547311: wrote=yes part3_audio_age_s~327 resume-press-1
- qsave 2026-11-13 05:23:36 UTC epoch=1794547380: wrote=yes part3_audio_age_s~403 resume-press-1
- qsave 2026-11-13 05:24:53 UTC epoch=1794547456: wrote=no part3_audio_age_s~480 resume-press-1
- qsave 2026-11-13 05:26:10 UTC epoch=1794547534: wrote=yes part3_audio_age_s~557 resume-press-1
- health #1 2026-11-13 05:27:04 UTC epoch=1794547624: audio_bytes=234066584 audio_s~609 video_bytes=23068672 underruns_total=971 load=[3.93, 3.70, 2.56] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 05:27:29 UTC epoch=1794547610: wrote=yes part3_audio_age_s~636 resume-press-1
- qsave 2026-11-13 05:27:41 UTC epoch=1794547632: wrote=yes part3_audio_age_s~648 resume-press-2
- qsave 2026-11-13 05:28:50 UTC epoch=1794547701: wrote=yes part3_audio_age_s~717 resume-press-1
- qsave 2026-11-13 05:30:23 UTC epoch=1794547770: wrote=yes part3_audio_age_s~810 resume-press-3
- qsave 2026-11-13 05:31:32 UTC epoch=1794547863: wrote=yes part3_audio_age_s~878 resume-press-1
- qsave 2026-11-13 05:32:40 UTC epoch=1794547932: wrote=yes part3_audio_age_s~946 resume-press-1
- qsave 2026-11-13 05:33:48 UTC epoch=1794548000: wrote=yes part3_audio_age_s~1015 resume-press-1
- qsave 2026-11-13 05:34:58 UTC epoch=1794548068: wrote=yes part3_audio_age_s~1085 resume-press-1
- qsave 2026-11-13 05:36:07 UTC epoch=1794548138: wrote=yes part3_audio_age_s~1154 resume-press-1
- health #2 2026-11-13 05:36:44 UTC epoch=1794548204: audio_bytes=456535400 audio_s~1188 video_bytes=46923776 underruns_total=1101 load=[3.15, 3.50, 2.83] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 05:37:22 UTC epoch=1794548212: wrote=yes part3_audio_age_s~1228 resume-press-1
- qsave 2026-11-13 05:38:37 UTC epoch=1794548282: wrote=yes part3_audio_age_s~1304 resume-press-1
- qsave 2026-11-13 05:39:47 UTC epoch=1794548358: wrote=yes part3_audio_age_s~1374 resume-press-1
- qsave 2026-11-13 05:40:56 UTC epoch=1794548427: wrote=yes part3_audio_age_s~1443 resume-press-1
- qsave 2026-11-13 05:42:04 UTC epoch=1794548496: wrote=yes part3_audio_age_s~1510 resume-press-1
- qsave 2026-11-13 05:43:30 UTC epoch=1794548564: wrote=yes part3_audio_age_s~1597 resume-press-2
- qsave 2026-11-13 05:44:44 UTC epoch=1794548651: wrote=yes part3_audio_age_s~1671 resume-press-1
- qsave 2026-11-13 05:46:11 UTC epoch=1794548724: wrote=yes part3_audio_age_s~1757 resume-press-1
- health #3 2026-11-13 05:46:25 UTC epoch=1794548785: audio_bytes=679285720 audio_s~1768 video_bytes=69468160 underruns_total=1641 load=[0.93, 3.29, 3.07] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 05:47:21 UTC epoch=1794548796: wrote=no part3_audio_age_s~1828 resume-press-1
- qsave 2026-11-13 05:48:44 UTC epoch=1794548881: wrote=yes part3_audio_age_s~1911 resume-press-1
- qsave 2026-11-13 05:50:29 UTC epoch=1794548964: wrote=no part3_audio_age_s~2015 resume-press-3
- qsave 2026-11-13 05:51:49 UTC epoch=1794549069: wrote=yes part3_audio_age_s~2096 resume-press-1
- qsave 2026-11-13 05:53:22 UTC epoch=1794549149: wrote=no part3_audio_age_s~2188 resume-press-2
- qsave 2026-11-13 05:54:39 UTC epoch=1794549242: wrote=yes part3_audio_age_s~2265 resume-press-2
- qsave 2026-11-13 05:55:55 UTC epoch=1794549319: wrote=yes part3_audio_age_s~2341 resume-press-2
- health #4 2026-11-13 05:56:09 UTC epoch=1794549369: audio_bytes=903661104 audio_s~2353 video_bytes=92274688 underruns_total=2789 load=[0.34, 4.01, 4.13] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 05:57:30 UTC epoch=1794549398: wrote=yes part3_audio_age_s~2437 resume-press-3
- qsave 2026-11-13 05:57:32 UTC epoch=1794549395: wrote=yes part3_audio_age_s~2439 resume-press-3
- qsave 2026-11-13 05:58:51 UTC epoch=1794549491: wrote=yes part3_audio_age_s~2518 resume-press-2
- qsave 2026-11-13 06:00:08 UTC epoch=1794549571: wrote=yes part3_audio_age_s~2595 resume-press-2
- qsave 2026-11-13 06:01:28 UTC epoch=1794549648: wrote=yes part3_audio_age_s~2675 resume-press-2
- qsave 2026-11-13 06:02:48 UTC epoch=1794549728: wrote=yes part3_audio_age_s~2755 resume-press-2
- qsave 2026-11-13 06:03:51 UTC epoch=1794549808: wrote=yes part3_audio_age_s~2817 resume-press-1
- qsave 2026-11-13 06:05:21 UTC epoch=1794549871: wrote=no part3_audio_age_s~2907 resume-press-2
- health #5 2026-11-13 06:06:11 UTC epoch=1794549971: audio_bytes=1134884664 audio_s~2955 video_bytes=116654080 underruns_total=4047 load=[8.19, 5.92, 5.62] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 06:06:44 UTC epoch=1794549961: wrote=yes part3_audio_age_s~2990 resume-press-3
- qsave 2026-11-13 06:12:24 UTC epoch=1794550304: wrote=no part3_audio_age_s~3331 resume-press-1
- qsave 2026-11-13 06:13:43 UTC epoch=1794550384: wrote=no part3_audio_age_s~3410 resume-press-1
- qsave 2026-11-13 06:15:04 UTC epoch=1794550463: wrote=yes part3_audio_age_s~3490 resume-press-1
- qsave 2026-11-13 06:16:41 UTC epoch=1794550544: wrote=yes part3_audio_age_s~3588 resume-press-2
- qsave 2026-11-13 06:17:59 UTC epoch=1794550641: wrote=yes part3_audio_age_s~3666 resume-press-2
- qsave 2026-11-13 06:19:06 UTC epoch=1794550719: wrote=yes part3_audio_age_s~3732 resume-press-1
- qsave 2026-11-13 06:20:22 UTC epoch=1794550786: wrote=yes part3_audio_age_s~3809 resume-press-1
- health #6 2026-11-13 06:21:16 UTC epoch=1794550876: audio_bytes=1482570488 audio_s~3860 video_bytes=154140672 underruns_total=5420 load=[0.99, 3.50, 4.78] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 06:21:34 UTC epoch=1794550862: wrote=yes part3_audio_age_s~3881 resume-press-1
- qsave 2026-11-13 06:21:48 UTC epoch=1794550885: wrote=no part3_audio_age_s~3895 
- qsave 2026-11-13 06:22:58 UTC epoch=1794550948: wrote=yes part3_audio_age_s~3964 resume-press-1
- qsave 2026-11-13 06:24:04 UTC epoch=1794551018: wrote=no part3_audio_age_s~4030 
- qsave 2026-11-13 06:25:27 UTC epoch=1794551084: wrote=no part3_audio_age_s~4114 resume-press-1
- qsave 2026-11-13 06:26:43 UTC epoch=1794551167: wrote=yes part3_audio_age_s~4190 resume-press-1
- qsave 2026-11-13 06:28:04 UTC epoch=1794551243: wrote=yes part3_audio_age_s~4270 resume-press-1
- qsave 2026-11-13 06:29:12 UTC epoch=1794551324: wrote=yes part3_audio_age_s~4339 resume-press-1
- qsave 2026-11-13 06:30:44 UTC epoch=1794551392: wrote=no part3_audio_age_s~4431 resume-press-2
- health #7 2026-11-13 06:30:57 UTC epoch=1794551457: audio_bytes=1705864216 audio_s~4442 video_bytes=179044352 underruns_total=6258 load=[7.93, 4.92, 5.02] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- INCIDENT 06:30-06:32 UTC (part 8): a manual save attempt under the
  perf-line contention window misfired — the park press landed, the
  resume press was eaten, and two parked F11 presses did not write
  (save witness stale since 06:28:53). Game sat parked ~2 min at a
  stable line (footage holds a dialogue pause; no content lost). AUTO
  restored with a verified press at 06:32:09 (B=67). Cause: input
  presses eaten under load — same contention window reported to parent.
- qsave 2026-11-13 06:33:05 UTC epoch=1794551539: wrote=yes part3_audio_age_s~4571 resume-press-1
- qsave 2026-11-13 06:34:29 UTC epoch=1794551625: wrote=no part3_audio_age_s~4656 resume-press-1
- qsave 2026-11-13 06:35:47 UTC epoch=1794551709: wrote=yes part3_audio_age_s~4734 resume-press-1
- qsave 2026-11-13 06:37:26 UTC epoch=1794551787: wrote=no part3_audio_age_s~4833 resume-press-3
- qsave 2026-11-13 06:38:43 UTC epoch=1794551886: wrote=no part3_audio_age_s~4910 resume-press-1
- qsave 2026-11-13 06:40:02 UTC epoch=1794551963: wrote=no part3_audio_age_s~4989 resume-press-1
- qsave 2026-11-13 06:41:18 UTC epoch=1794552042: wrote=yes part3_audio_age_s~5065 resume-press-1
- health #8 2026-11-13 06:41:50 UTC epoch=1794552110: audio_bytes=1956707664 audio_s~5095 video_bytes=204472320 underruns_total=7066 load=[5.77, 4.77, 4.94] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 06:42:26 UTC epoch=1794552116: wrote=no part3_audio_age_s~5132 
- qsave 2026-11-13 06:42:28 UTC epoch=1794552118: wrote=no part3_audio_age_s~5135 
- qsave 2026-11-13 06:44:03 UTC epoch=1794552186: wrote=yes part3_audio_age_s~5229 resume-press-3
- qsave 2026-11-13 06:45:38 UTC epoch=1794552283: wrote=no part3_audio_age_s~5325 resume-press-3
- qsave 2026-11-13 06:46:55 UTC epoch=1794552378: wrote=no part3_audio_age_s~5402 resume-press-1
- qsave 2026-11-13 06:48:13 UTC epoch=1794552455: wrote=no part3_audio_age_s~5480 resume-press-1
- qsave 2026-11-13 06:49:19 UTC epoch=1794552533: wrote=yes part3_audio_age_s~5546 resume-press-1
- qsave 2026-11-13 06:50:51 UTC epoch=1794552599: wrote=no part3_audio_age_s~5638 resume-press-2
- health #9 2026-11-13 06:51:28 UTC epoch=1794552688: audio_bytes=2178526304 audio_s~5673 video_bytes=229113856 underruns_total=7601 load=[1.93, 3.35, 3.97] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 06:52:00 UTC epoch=1794552691: wrote=yes part3_audio_age_s~5706 resume-press-1
- qsave 2026-11-13 06:52:03 UTC epoch=1794552699: wrote=yes part3_audio_age_s~5710 
- qsave 2026-11-13 06:53:19 UTC epoch=1794552763: wrote=yes part3_audio_age_s~5786 resume-press-1
- qsave 2026-11-13 06:54:46 UTC epoch=1794552839: wrote=yes part3_audio_age_s~5873 resume-press-1
- qsave 2026-11-13 06:56:08 UTC epoch=1794552926: wrote=yes part3_audio_age_s~5955 resume-press-1
- qsave 2026-11-13 06:57:45 UTC epoch=1794553008: wrote=no part3_audio_age_s~6052 resume-press-3
- qsave 2026-11-13 06:58:59 UTC epoch=1794553105: wrote=yes part3_audio_age_s~6126 resume-press-1
- qsave 2026-11-13 07:00:17 UTC epoch=1794553179: wrote=no part3_audio_age_s~6203 resume-press-1
- health #10 2026-11-13 07:01:12 UTC epoch=1794553272: audio_bytes=2402388016 audio_s~6256 video_bytes=253493248 underruns_total=8435 load=[1.07, 3.54, 3.90] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- NOTE 07:01 UTC: win32-perf's full game instance exited, but the line
  continues with probe runs (probe_present.exe ~28% CPU + its own
  wineserver/explorer) — contention is now bursty rather than
  continuous. Underrun deltas remain elevated (loop68 window +834);
  the whole part-8 span from ~05:46 UTC is flagged contention-affected
  for the final gate, worst 05:56-06:41.
- qsave 2026-11-13 07:01:37 UTC epoch=1794553257: wrote=yes part3_audio_age_s~6283 resume-press-1
- qsave 2026-11-13 07:01:54 UTC epoch=1794553286: wrote=no part3_audio_age_s~6301 
- qsave 2026-11-13 07:03:27 UTC epoch=1794553354: wrote=yes part3_audio_age_s~6394 resume-press-3
- qsave 2026-11-13 07:04:47 UTC epoch=1794553447: wrote=no part3_audio_age_s~6474 resume-press-1
- qsave 2026-11-13 07:06:05 UTC epoch=1794553527: wrote=no part3_audio_age_s~6552 resume-press-1
- qsave 2026-11-13 07:07:25 UTC epoch=1794553606: wrote=no part3_audio_age_s~6632 resume-press-1
- qsave 2026-11-13 07:08:56 UTC epoch=1794553685: wrote=no part3_audio_age_s~6722 resume-press-3
- qsave 2026-11-13 07:10:15 UTC epoch=1794553776: wrote=no part3_audio_age_s~6802 resume-press-3
- health #11 2026-11-13 07:10:58 UTC epoch=1794553858: audio_bytes=2627974896 audio_s~6843 video_bytes=277610496 underruns_total=8898 load=[1.50, 2.74, 3.42] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 07:11:17 UTC epoch=1794553855: wrote=no part3_audio_age_s~6864 

## GAME CRASH — part 8 ended (07:11 UTC)
- KiriKiri/TVP bitmap-allocation failure dialog (1280x960, 4915240 B)
  appeared in the Ch.2-1 cafe scene; modal — it ate quick-save/AUTO
  input from ~07:03 to 07:11. Dismissed 07:11:32 UTC; the engine then
  exited. Xvfb/PA/capture infrastructure unaffected. Captures stopped
  by PID; part 8 audio survived in full (6920.123 s). Recovery #8
  (game relaunch only) -> part 9 from the 07:02:48 quick save.

## Part 9 (resume after game crash #1)
- resumed from data_quick_01 (07:02:48 UTC) via START -> F12 (focused, second press); position = Ch.2-1 club room (evening), just before the cafe transition that crashed part 8.
- underrun count at part9 start: 8969
- part9 audio_start_epoch=1794554115.8374188 (2026-11-13 07:15:15 UTC)
- part9 video_start_epoch=1794554115.8398235 (2026-11-13 07:15:15 UTC)
- part9 video_minus_audio_offset_s=0.002

### Part 9 — FINAL (VM restart #8)
- files: continuous-video.part9.mkv / continuous-audio.part9.raw
- video_duration_s=N/A (unfinalized header), audio_s=1175.775
- frontier: Chapter 2-1, cafe — Wakaba waitress scene (the part-8
  bitmap-crash transition PASSED cleanly on this pass); newest quick
  save 07:33:47 UTC, 64 s before the cut.
- audio_start_epoch=1794554115.837418703, video_start_epoch=1794554115.839823517
- qsave 2026-11-13 07:16:32 UTC epoch=1794554150: wrote=yes part3_audio_age_s~76 resume-press-1
- qsave 2026-11-13 07:17:41 UTC epoch=1794554232: wrote=yes part3_audio_age_s~145 resume-press-1
- qsave 2026-11-13 07:18:57 UTC epoch=1794554301: wrote=yes part3_audio_age_s~221 resume-press-1
- qsave 2026-11-13 07:20:18 UTC epoch=1794554378: wrote=no part3_audio_age_s~302 resume-press-1
- qsave 2026-11-13 07:21:34 UTC epoch=1794554458: wrote=yes part3_audio_age_s~378 resume-press-1
- qsave 2026-11-13 07:22:50 UTC epoch=1794554534: wrote=yes part3_audio_age_s~454 resume-press-1
- qsave 2026-11-13 07:24:12 UTC epoch=1794554610: wrote=yes part3_audio_age_s~535 resume-press-1
- health #1 2026-11-13 07:25:22 UTC epoch=1794554722: audio_bytes=232101128 audio_s~604 video_bytes=25690112 underruns_total=9351 load=[1.60, 2.75, 3.03] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 07:25:30 UTC epoch=1794554692: wrote=yes part3_audio_age_s~614 resume-press-1
- qsave 2026-11-13 07:26:25 UTC epoch=1794554730: wrote=no part3_audio_age_s~668 resume-press-3
- qsave 2026-11-13 07:27:40 UTC epoch=1794554825: wrote=yes part3_audio_age_s~744 resume-press-1
- qsave 2026-11-13 07:28:59 UTC epoch=1794554900: wrote=no part3_audio_age_s~822 resume-press-1
- qsave 2026-11-13 07:30:21 UTC epoch=1794554979: wrote=no part3_audio_age_s~905 resume-press-1
- qsave 2026-11-13 07:31:40 UTC epoch=1794555061: wrote=yes part3_audio_age_s~984 resume-press-2
- qsave 2026-11-13 07:32:47 UTC epoch=1794555140: wrote=yes part3_audio_age_s~1051 resume-press-1
- qsave 2026-11-13 07:34:07 UTC epoch=1794555207: wrote=yes part3_audio_age_s~1131 resume-press-1

## VM RESTART #8 — part 9 ended (07:34 UTC)
- Eighth restart, ~07:34:5x UTC, only ~20 min into part 9. SURVIVED:
  continuous-audio.part9.raw (last write 07:34:51) + video mkv.
  Newest quick save 07:33:47. Story frontier: Ch.2-1 cafe.
- Net story: ~793 min (~13.2 h). Recovery #9 -> part 10.

## Part 10 (resume after VM restart #8)
- resumed from data_quick_01 (07:33:47 UTC) via START -> F12 (focused, second press); position = Ch.2-1 cafe, Nanao + Nene.
- underrun count at part10 start: 57
- part10 audio_start_epoch=1794555494.181932 (2026-11-13 07:38:14 UTC)
- part10 video_start_epoch=1794555494.2420595 (2026-11-13 07:38:14 UTC)
- part10 video_minus_audio_offset_s=0.060

### Part 10 — FINAL (GAME CRASH #2 — engine bitmap-alloc failure)
- files: continuous-video.part10.mkv / continuous-audio.part10.raw
- video_duration_s=N/A (unfinalized header), audio_s=5296.308
- frontier: Chapter 2-1, home — Taichi scene. At ~09:04-09:05 the
  engine raised the modal bitmap dialog again, this time
  TVPAllocBitmapBits(size=33115672 (2508x3301)) — a large portrait/CG
  allocation failing after ~88 min of continuous session (same
  failure family as part 8's crash, at 1280x960 after ~115 min —
  consistent with long-session 32-bit address-space fragmentation).
  Dismissed 09:06; the engine exited on dismissal, as before.
  Newest quick save 09:03:48 UTC — part 11 resumes ~1 min back.
- audio_start_epoch=1794555494.181932006, video_start_epoch=1794555494.242059467
- qsave 2026-11-13 07:39:40 UTC epoch=1794555534: wrote=no part3_audio_age_s~85 resume-press-1
- qsave 2026-11-13 07:41:00 UTC epoch=1794555620: wrote=yes part3_audio_age_s~165 resume-press-1
- qsave 2026-11-13 07:42:25 UTC epoch=1794555700: wrote=yes part3_audio_age_s~251 resume-press-1
- qsave 2026-11-13 07:43:50 UTC epoch=1794555785: wrote=yes part3_audio_age_s~335 resume-press-1
- qsave 2026-11-13 07:45:23 UTC epoch=1794555870: wrote=no part3_audio_age_s~429 resume-press-2
- qsave 2026-11-13 07:46:44 UTC epoch=1794555963: wrote=yes part3_audio_age_s~509 resume-press-2
- qsave 2026-11-13 07:48:03 UTC epoch=1794556044: wrote=yes part3_audio_age_s~589 resume-press-2
- health #1 2026-11-13 07:48:27 UTC epoch=1794556107: audio_bytes=234347152 audio_s~610 video_bytes=23330816 underruns_total=1035 load=[5.63, 5.94, 3.37] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 07:49:34 UTC epoch=1794556120: wrote=yes part3_audio_age_s~680 resume-press-3
- qsave 2026-11-13 07:49:34 UTC epoch=1794556123: wrote=yes part3_audio_age_s~680 resume-press-3
- qsave 2026-11-13 07:50:48 UTC epoch=1794556214: wrote=yes part3_audio_age_s~754 resume-press-1
- qsave 2026-11-13 07:52:08 UTC epoch=1794556288: wrote=no part3_audio_age_s~833 resume-press-1
- qsave 2026-11-13 07:53:25 UTC epoch=1794556368: wrote=yes part3_audio_age_s~911 resume-press-1
- qsave 2026-11-13 07:54:42 UTC epoch=1794556445: wrote=yes part3_audio_age_s~987 resume-press-1
- qsave 2026-11-13 07:55:52 UTC epoch=1794556522: wrote=yes part3_audio_age_s~1057 resume-press-1
- qsave 2026-11-13 07:57:14 UTC epoch=1794556592: wrote=yes part3_audio_age_s~1139 resume-press-1
- health #2 2026-11-13 07:58:12 UTC epoch=1794556692: audio_bytes=459256896 audio_s~1195 video_bytes=46661632 underruns_total=1607 load=[1.75, 3.95, 3.56] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 07:58:28 UTC epoch=1794556674: wrote=yes part3_audio_age_s~1213 resume-press-1
- qsave 2026-11-13 07:58:44 UTC epoch=1794556701: wrote=no part3_audio_age_s~1229 
- qsave 2026-11-13 08:00:23 UTC epoch=1794556764: wrote=yes part3_audio_age_s~1329 resume-press-3
- qsave 2026-11-13 08:01:39 UTC epoch=1794556863: wrote=yes part3_audio_age_s~1405 resume-press-1
- qsave 2026-11-13 08:03:15 UTC epoch=1794556939: wrote=yes part3_audio_age_s~1501 resume-press-3
- qsave 2026-11-13 08:04:38 UTC epoch=1794557035: wrote=yes part3_audio_age_s~1583 resume-press-1
- qsave 2026-11-13 08:05:55 UTC epoch=1794557118: wrote=yes part3_audio_age_s~1660 resume-press-1
- qsave 2026-11-13 08:07:08 UTC epoch=1794557195: wrote=yes part3_audio_age_s~1734 resume-press-1
- health #3 2026-11-13 08:07:53 UTC epoch=1794557273: audio_bytes=682359400 audio_s~1776 video_bytes=67633152 underruns_total=2445 load=[0.43, 3.05, 3.54] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 08:08:48 UTC epoch=1794557268: wrote=yes part3_audio_age_s~1834 resume-press-3
- qsave 2026-11-13 08:08:48 UTC epoch=1794557282: wrote=yes part3_audio_age_s~1834 resume-press-3
- qsave 2026-11-13 08:10:02 UTC epoch=1794557368: wrote=yes part3_audio_age_s~1908 resume-press-1
- qsave 2026-11-13 08:11:23 UTC epoch=1794557442: wrote=yes part3_audio_age_s~1989 resume-press-1
- qsave 2026-11-13 08:12:31 UTC epoch=1794557523: wrote=yes part3_audio_age_s~2056 resume-press-1
- qsave 2026-11-13 08:13:51 UTC epoch=1794557591: wrote=no part3_audio_age_s~2136 resume-press-1
- qsave 2026-11-13 08:15:02 UTC epoch=1794557671: wrote=yes part3_audio_age_s~2207 resume-press-1
- qsave 2026-11-13 08:16:14 UTC epoch=1794557742: wrote=yes part3_audio_age_s~2279 resume-press-1
- qsave 2026-11-13 08:17:24 UTC epoch=1794557814: wrote=yes part3_audio_age_s~2349 resume-press-1
- health #4 2026-11-13 08:17:33 UTC epoch=1794557853: audio_bytes=905327400 audio_s~2357 video_bytes=92274688 underruns_total=3127 load=[3.55, 2.68, 3.34] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 08:18:19 UTC epoch=1794557858: wrote=yes part3_audio_age_s~2405 resume-press-1
- qsave 2026-11-13 08:19:31 UTC epoch=1794557939: wrote=yes part3_audio_age_s~2477 resume-press-1
- qsave 2026-11-13 08:20:52 UTC epoch=1794558011: wrote=no part3_audio_age_s~2557 resume-press-1
- qsave 2026-11-13 08:22:08 UTC epoch=1794558092: wrote=yes part3_audio_age_s~2633 resume-press-1
- qsave 2026-11-13 08:23:23 UTC epoch=1794558168: wrote=yes part3_audio_age_s~2708 resume-press-1
- qsave 2026-11-13 08:24:42 UTC epoch=1794558243: wrote=no part3_audio_age_s~2787 resume-press-1
- qsave 2026-11-13 08:25:58 UTC epoch=1794558322: wrote=yes part3_audio_age_s~2863 resume-press-1
- qsave 2026-11-13 08:27:04 UTC epoch=1794558398: wrote=yes part3_audio_age_s~2929 resume-press-1
- health #5 2026-11-13 08:27:10 UTC epoch=1794558430: audio_bytes=1126698880 audio_s~2934 video_bytes=117702656 underruns_total=3491 load=[3.67, 2.84, 3.24] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 08:27:56 UTC epoch=1794558437: wrote=no part3_audio_age_s~2981 resume-press-1
- qsave 2026-11-13 08:29:00 UTC epoch=1794558516: wrote=no part3_audio_age_s~3045 
- qsave 2026-11-13 08:30:18 UTC epoch=1794558580: wrote=no part3_audio_age_s~3123 resume-press-1
- qsave 2026-11-13 08:31:34 UTC epoch=1794558658: wrote=yes part3_audio_age_s~3199 resume-press-1
- qsave 2026-11-13 08:32:42 UTC epoch=1794558734: wrote=yes part3_audio_age_s~3267 resume-press-1
- qsave 2026-11-13 08:33:59 UTC epoch=1794558802: wrote=yes part3_audio_age_s~3344 resume-press-1
- qsave 2026-11-13 08:35:23 UTC epoch=1794558879: wrote=no part3_audio_age_s~3428 resume-press-1
- qsave 2026-11-13 08:36:33 UTC epoch=1794558963: wrote=yes part3_audio_age_s~3498 resume-press-1
- health #6 2026-11-13 08:36:51 UTC epoch=1794559011: audio_bytes=1348871216 audio_s~3512 video_bytes=143130624 underruns_total=4013 load=[6.81, 4.46, 3.70] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 08:37:39 UTC epoch=1794559020: wrote=yes part3_audio_age_s~3565 resume-press-1
- qsave 2026-11-13 08:38:57 UTC epoch=1794559099: wrote=no part3_audio_age_s~3643 resume-press-1
- qsave 2026-11-13 08:40:13 UTC epoch=1794559177: wrote=no part3_audio_age_s~3719 resume-press-1
- qsave 2026-11-13 08:41:29 UTC epoch=1794559253: wrote=no part3_audio_age_s~3794 resume-press-1
- qsave 2026-11-13 08:42:47 UTC epoch=1794559329: wrote=yes part3_audio_age_s~3872 resume-press-1
- qsave 2026-11-13 08:43:54 UTC epoch=1794559407: wrote=yes part3_audio_age_s~3939 resume-press-1
- qsave 2026-11-13 08:45:09 UTC epoch=1794559474: wrote=yes part3_audio_age_s~4015 resume-press-1
- qsave 2026-11-13 08:46:27 UTC epoch=1794559549: wrote=no part3_audio_age_s~4092 resume-press-1
- health #7 2026-11-13 08:46:31 UTC epoch=1794559591: audio_bytes=1572846376 audio_s~4095 video_bytes=165937152 underruns_total=4336 load=[4.40, 4.05, 3.60] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 08:47:13 UTC epoch=1794559598: wrote=yes part3_audio_age_s~4138 resume-press-1
- qsave 2026-11-13 08:48:19 UTC epoch=1794559673: wrote=yes part3_audio_age_s~4205 resume-press-1
- qsave 2026-11-13 08:49:38 UTC epoch=1794559739: wrote=yes part3_audio_age_s~4283 resume-press-1
- qsave 2026-11-13 08:50:55 UTC epoch=1794559818: wrote=no part3_audio_age_s~4360 resume-press-1
- qsave 2026-11-13 08:52:02 UTC epoch=1794559895: wrote=yes part3_audio_age_s~4427 resume-press-1
- qsave 2026-11-13 08:53:09 UTC epoch=1794559962: wrote=yes part3_audio_age_s~4495 resume-press-1
- qsave 2026-11-13 08:54:27 UTC epoch=1794560029: wrote=no part3_audio_age_s~4572 resume-press-1
- qsave 2026-11-13 08:55:34 UTC epoch=1794560107: wrote=yes part3_audio_age_s~4640 resume-press-1
- health #8 2026-11-13 08:56:10 UTC epoch=1794560170: audio_bytes=1794717216 audio_s~4673 video_bytes=189530112 underruns_total=4626 load=[1.48, 3.04, 3.24] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 08:56:54 UTC epoch=1794560187: wrote=yes part3_audio_age_s~4719 resume-press-1
- qsave 2026-11-13 08:58:03 UTC epoch=1794560254: wrote=yes part3_audio_age_s~4788 resume-press-1
- qsave 2026-11-13 08:59:12 UTC epoch=1794560323: wrote=yes part3_audio_age_s~4858 resume-press-1
- qsave 2026-11-13 09:00:30 UTC epoch=1794560392: wrote=yes part3_audio_age_s~4935 resume-press-1
- qsave 2026-11-13 09:01:40 UTC epoch=1794560470: wrote=yes part3_audio_age_s~5005 resume-press-1
- qsave 2026-11-13 09:02:48 UTC epoch=1794560540: wrote=yes part3_audio_age_s~5073 resume-press-1
- qsave 2026-11-13 09:04:08 UTC epoch=1794560608: wrote=yes part3_audio_age_s~5153 resume-press-1
- qsave 2026-11-13 09:05:11 UTC epoch=1794560688: wrote=no part3_audio_age_s~5216 
- health #9 2026-11-13 09:05:57 UTC epoch=1794560757: audio_bytes=2020652248 audio_s~5262 video_bytes=213123072 underruns_total=4736 load=[3.08, 3.95, 3.72] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]

## GAME CRASH #2 — part 10 ended (09:06 UTC)
- Same TVPAllocBitmapBits modal-dialog failure (2508x3301) in the
  Ch.2-1 home scene; dismissed 09:06 UTC, engine exited. Captures
  stopped by PID; part 10 audio survived in full (5296.308 s).
  Recovery #10 (game relaunch only) -> part 11 from the 09:03:48 save.
- Net story: ~793 + 88.3 - ~1 overlap = ~880 min (~14.7 h).

## VM RESTART #9 — during recovery #10 (09:07 UTC)
- The VM restarted ~09:07:4x UTC while the post-crash game relaunch
  was booting. Part 10 was already finalized and its captures stopped,
  so nothing was lost. Recovery #11 (full stack) -> part 11 from the
  same 09:03:48 quick save.

## Part 11 (resume after game crash #2 + VM restart #9)
- resumed from data_quick_01 (09:03:48 UTC) via START -> F12 (focused, first press); position = Ch.2-1 night street, Nene — just before the home scene whose portrait allocation crashed part 10.
- underrun count at part11 start: 4
- part11 audio_start_epoch=1794561014.9745228 (2026-11-13 09:10:14 UTC)
- part11 video_start_epoch=1794561014.9777558 (2026-11-13 09:10:14 UTC)
- part11 video_minus_audio_offset_s=0.003

### Part 11 — FINAL (VM restart #10)
- files: continuous-video.part11.mkv / continuous-audio.part11.raw
- video_duration_s=N/A (unfinalized header), audio_s=6911.227
- frontier: Chapter 2-2, club room — Meguru consultation planning
  (Nene + Meguru). Newest quick save 11:04:43 UTC, 43 s before the
  cut. NOTE: an exec-result delivery during the restart claimed
  "audio ~7107 s / health shot 12" — spurious; disk truth is
  2,653,911,176 bytes = 6911.227 s and health shots end at #11.
- audio_start_epoch=1794561014.974522819, video_start_epoch=1794561014.977755891
- qsave 2026-11-13 09:12:29 UTC epoch=1794561122: wrote=yes part3_audio_age_s~134 resume-press-1
- qsave 2026-11-13 09:13:37 UTC epoch=1794561190: wrote=yes part3_audio_age_s~202 resume-press-1
- qsave 2026-11-13 09:14:54 UTC epoch=1794561257: wrote=yes part3_audio_age_s~279 resume-press-1
- qsave 2026-11-13 09:16:03 UTC epoch=1794561334: wrote=yes part3_audio_age_s~348 resume-press-1
- qsave 2026-11-13 09:17:19 UTC epoch=1794561403: wrote=yes part3_audio_age_s~424 resume-press-1
- qsave 2026-11-13 09:18:37 UTC epoch=1794561479: wrote=no part3_audio_age_s~502 resume-press-1
- qsave 2026-11-13 09:19:59 UTC epoch=1794561557: wrote=yes part3_audio_age_s~583 resume-press-1
- qsave 2026-11-13 09:21:25 UTC epoch=1794561639: wrote=yes part3_audio_age_s~669 resume-press-1
- health #1 2026-11-13 09:21:34 UTC epoch=1794561694: audio_bytes=260141648 audio_s~677 video_bytes=21757952 underruns_total=322 load=[0.47, 1.71, 1.28] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 09:22:08 UTC epoch=1794561702: wrote=no part3_audio_age_s~713 
- qsave 2026-11-13 09:23:29 UTC epoch=1794561768: wrote=no part3_audio_age_s~794 resume-press-1
- qsave 2026-11-13 09:25:00 UTC epoch=1794561850: wrote=yes part3_audio_age_s~885 resume-press-3
- qsave 2026-11-13 09:26:26 UTC epoch=1794561940: wrote=no part3_audio_age_s~971 resume-press-1
- qsave 2026-11-13 09:27:34 UTC epoch=1794562026: wrote=yes part3_audio_age_s~1039 resume-press-1
- qsave 2026-11-13 09:28:47 UTC epoch=1794562095: wrote=yes part3_audio_age_s~1112 resume-press-1
- qsave 2026-11-13 09:29:59 UTC epoch=1794562167: wrote=yes part3_audio_age_s~1183 resume-press-1
- health #2 2026-11-13 09:31:13 UTC epoch=1794562273: audio_bytes=482716808 audio_s~1257 video_bytes=43778048 underruns_total=1100 load=[6.61, 3.83, 2.79] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 09:31:18 UTC epoch=1794562239: wrote=yes part3_audio_age_s~1263 resume-press-1
- milestone 09:31 UTC: CHAPTER 2-2 reached (classroom) — Ch.2-1
  complete; the home-scene portrait allocation that crashed part 10
  passed cleanly on part 11's fresh process (~21 min in).
- qsave 2026-11-13 09:31:56 UTC epoch=1794562280: wrote=yes part3_audio_age_s~1301 resume-press-1
- qsave 2026-11-13 09:33:06 UTC epoch=1794562356: wrote=yes part3_audio_age_s~1371 resume-press-1
- qsave 2026-11-13 09:34:26 UTC epoch=1794562426: wrote=no part3_audio_age_s~1451 resume-press-1
- qsave 2026-11-13 09:35:44 UTC epoch=1794562506: wrote=yes part3_audio_age_s~1529 resume-press-1
- qsave 2026-11-13 09:37:04 UTC epoch=1794562584: wrote=yes part3_audio_age_s~1608 resume-press-1
- qsave 2026-11-13 09:38:12 UTC epoch=1794562664: wrote=yes part3_audio_age_s~1677 resume-press-1
- qsave 2026-11-13 09:39:19 UTC epoch=1794562732: wrote=yes part3_audio_age_s~1744 resume-press-1
- qsave 2026-11-13 09:40:26 UTC epoch=1794562799: wrote=yes part3_audio_age_s~1811 resume-press-1
- health #3 2026-11-13 09:40:51 UTC epoch=1794562851: audio_bytes=704715472 audio_s~1835 video_bytes=66322432 underruns_total=1406 load=[4.24, 3.62, 3.20] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 09:41:30 UTC epoch=1794562863: wrote=yes part3_audio_age_s~1874 resume-press-1
- qsave 2026-11-13 09:42:38 UTC epoch=1794562930: wrote=yes part3_audio_age_s~1943 resume-press-1
- qsave 2026-11-13 09:43:57 UTC epoch=1794562998: wrote=yes part3_audio_age_s~2022 resume-press-1
- qsave 2026-11-13 09:45:17 UTC epoch=1794563077: wrote=no part3_audio_age_s~2102 resume-press-1
- qsave 2026-11-13 09:46:40 UTC epoch=1794563157: wrote=yes part3_audio_age_s~2184 resume-press-1
- qsave 2026-11-13 09:47:49 UTC epoch=1794563240: wrote=yes part3_audio_age_s~2254 resume-press-1
- qsave 2026-11-13 09:49:03 UTC epoch=1794563309: wrote=yes part3_audio_age_s~2328 resume-press-1
- qsave 2026-11-13 09:50:15 UTC epoch=1794563383: wrote=yes part3_audio_age_s~2399 resume-press-1
- health #4 2026-11-13 09:50:34 UTC epoch=1794563434: audio_bytes=928396016 audio_s~2417 video_bytes=90701824 underruns_total=1846 load=[7.48, 5.64, 4.07] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 09:51:12 UTC epoch=1794563442: wrote=yes part3_audio_age_s~2457 resume-press-1
- qsave 2026-11-13 09:52:23 UTC epoch=1794563512: wrote=yes part3_audio_age_s~2528 resume-press-1
- qsave 2026-11-13 09:53:43 UTC epoch=1794563583: wrote=no part3_audio_age_s~2607 resume-press-1
- qsave 2026-11-13 09:55:05 UTC epoch=1794563663: wrote=yes part3_audio_age_s~2690 resume-press-1
- qsave 2026-11-13 09:56:26 UTC epoch=1794563745: wrote=no part3_audio_age_s~2771 resume-press-1
- qsave 2026-11-13 09:57:47 UTC epoch=1794563826: wrote=yes part3_audio_age_s~2852 resume-press-1
- qsave 2026-11-13 09:59:12 UTC epoch=1794563908: wrote=yes part3_audio_age_s~2936 resume-press-1
- health #5 2026-11-13 10:00:15 UTC epoch=1794564015: audio_bytes=1150810448 audio_s~2996 video_bytes=122159104 underruns_total=2446 load=[3.55, 4.95, 4.27] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:00:38 UTC epoch=1794563992: wrote=yes part3_audio_age_s~3023 resume-press-1
- qsave 2026-11-13 10:00:42 UTC epoch=1794564022: wrote=yes part3_audio_age_s~3027 
- qsave 2026-11-13 10:02:04 UTC epoch=1794564082: wrote=yes part3_audio_age_s~3109 resume-press-1
- qsave 2026-11-13 10:03:27 UTC epoch=1794564164: wrote=no part3_audio_age_s~3192 resume-press-1
- qsave 2026-11-13 10:04:49 UTC epoch=1794564247: wrote=yes part3_audio_age_s~3274 resume-press-1
- qsave 2026-11-13 10:06:00 UTC epoch=1794564329: wrote=yes part3_audio_age_s~3345 resume-press-1
- qsave 2026-11-13 10:07:19 UTC epoch=1794564400: wrote=yes part3_audio_age_s~3424 resume-press-1
- qsave 2026-11-13 10:08:55 UTC epoch=1794564479: wrote=yes part3_audio_age_s~3520 resume-press-3
- health #6 2026-11-13 10:09:54 UTC epoch=1794564594: audio_bytes=1373599200 audio_s~3577 video_bytes=142606336 underruns_total=3322 load=[2.01, 4.67, 4.53] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:10:35 UTC epoch=1794564575: wrote=no part3_audio_age_s~3620 resume-press-3
- qsave 2026-11-13 10:10:55 UTC epoch=1794564610: wrote=no part3_audio_age_s~3640 resume-press-2
- qsave 2026-11-13 10:12:16 UTC epoch=1794564695: wrote=no part3_audio_age_s~3721 resume-press-1
- qsave 2026-11-13 10:13:37 UTC epoch=1794564776: wrote=yes part3_audio_age_s~3802 resume-press-1
- qsave 2026-11-13 10:14:58 UTC epoch=1794564858: wrote=no part3_audio_age_s~3882 resume-press-1
- qsave 2026-11-13 10:16:19 UTC epoch=1794564938: wrote=yes part3_audio_age_s~3964 resume-press-1
- qsave 2026-11-13 10:17:29 UTC epoch=1794565019: wrote=yes part3_audio_age_s~4034 resume-press-1
- qsave 2026-11-13 10:18:46 UTC epoch=1794565089: wrote=no part3_audio_age_s~4111 resume-press-1
- health #7 2026-11-13 10:19:41 UTC epoch=1794565181: audio_bytes=1599382912 audio_s~4165 video_bytes=168820736 underruns_total=4102 load=[0.27, 2.97, 4.07] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:20:06 UTC epoch=1794565166: wrote=no part3_audio_age_s~4191 resume-press-1
- qsave 2026-11-13 10:20:56 UTC epoch=1794565226: wrote=yes part3_audio_age_s~4241 resume-press-1
- qsave 2026-11-13 10:22:13 UTC epoch=1794565296: wrote=no part3_audio_age_s~4317 resume-press-1
- qsave 2026-11-13 10:23:32 UTC epoch=1794565373: wrote=no part3_audio_age_s~4397 resume-press-1
- qsave 2026-11-13 10:24:52 UTC epoch=1794565452: wrote=yes part3_audio_age_s~4477 resume-press-1
- qsave 2026-11-13 10:26:01 UTC epoch=1794565532: wrote=yes part3_audio_age_s~4546 resume-press-1
- qsave 2026-11-13 10:27:14 UTC epoch=1794565601: wrote=yes part3_audio_age_s~4619 resume-press-1
- qsave 2026-11-13 10:28:28 UTC epoch=1794565674: wrote=yes part3_audio_age_s~4692 resume-press-1
- qsave 2026-11-13 10:29:44 UTC epoch=1794565748: wrote=yes part3_audio_age_s~4769 resume-press-1
- health #8 2026-11-13 10:30:00 UTC epoch=1794565800: audio_bytes=1836051800 audio_s~4781 video_bytes=202637312 underruns_total=4700 load=[8.61, 4.56, 4.37] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:30:55 UTC epoch=1794565811: wrote=yes part3_audio_age_s~4840 resume-press-1
- qsave 2026-11-13 10:32:07 UTC epoch=1794565895: wrote=yes part3_audio_age_s~4911 resume-press-1
- qsave 2026-11-13 10:33:28 UTC epoch=1794565967: wrote=no part3_audio_age_s~4993 resume-press-1
- qsave 2026-11-13 10:34:49 UTC epoch=1794566048: wrote=no part3_audio_age_s~5074 resume-press-1
- qsave 2026-11-13 10:36:12 UTC epoch=1794566129: wrote=no part3_audio_age_s~5157 resume-press-1
- qsave 2026-11-13 10:37:24 UTC epoch=1794566212: wrote=yes part3_audio_age_s~5229 resume-press-1
- qsave 2026-11-13 10:38:35 UTC epoch=1794566284: wrote=yes part3_audio_age_s~5300 resume-press-1
- health #9 2026-11-13 10:39:44 UTC epoch=1794566384: audio_bytes=2060794696 audio_s~5366 video_bytes=233832448 underruns_total=5344 load=[7.75, 5.39, 4.66] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:40:14 UTC epoch=1794566355: wrote=yes part3_audio_age_s~5399 resume-press-3
- qsave 2026-11-13 10:40:21 UTC epoch=1794566392: wrote=yes part3_audio_age_s~5406 
- qsave 2026-11-13 10:41:44 UTC epoch=1794566462: wrote=yes part3_audio_age_s~5489 resume-press-1
- qsave 2026-11-13 10:43:04 UTC epoch=1794566544: wrote=yes part3_audio_age_s~5569 resume-press-1
- qsave 2026-11-13 10:44:26 UTC epoch=1794566624: wrote=yes part3_audio_age_s~5650 resume-press-1
- qsave 2026-11-13 10:45:34 UTC epoch=1794566706: wrote=yes part3_audio_age_s~5719 resume-press-1
- qsave 2026-11-13 10:46:56 UTC epoch=1794566774: wrote=yes part3_audio_age_s~5801 resume-press-1
- qsave 2026-11-13 10:48:07 UTC epoch=1794566856: wrote=yes part3_audio_age_s~5872 resume-press-1
- health #10 2026-11-13 10:49:24 UTC epoch=1794566964: audio_bytes=2283976960 audio_s~5947 video_bytes=268959744 underruns_total=6146 load=[7.06, 6.32, 5.23] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:49:29 UTC epoch=1794566928: wrote=no part3_audio_age_s~5954 resume-press-1
- qsave 2026-11-13 10:50:07 UTC epoch=1794566972: wrote=yes part3_audio_age_s~5991 resume-press-1
- qsave 2026-11-13 10:51:16 UTC epoch=1794567047: wrote=yes part3_audio_age_s~6061 resume-press-1
- qsave 2026-11-13 10:52:35 UTC epoch=1794567116: wrote=no part3_audio_age_s~6140 resume-press-1
- qsave 2026-11-13 10:53:50 UTC epoch=1794567195: wrote=yes part3_audio_age_s~6215 resume-press-1
- qsave 2026-11-13 10:55:18 UTC epoch=1794567271: wrote=yes part3_audio_age_s~6303 resume-press-1
- qsave 2026-11-13 10:56:40 UTC epoch=1794567358: wrote=yes part3_audio_age_s~6385 resume-press-1
- qsave 2026-11-13 10:58:01 UTC epoch=1794567440: wrote=yes part3_audio_age_s~6466 resume-press-1
- health #11 2026-11-13 10:59:04 UTC epoch=1794567544: audio_bytes=2506389752 audio_s~6527 video_bytes=293076992 underruns_total=6916 load=[2.01, 4.96, 4.99] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 10:59:29 UTC epoch=1794567522: wrote=no part3_audio_age_s~6553 resume-press-1
- qsave 2026-11-13 10:59:42 UTC epoch=1794567554: wrote=no part3_audio_age_s~6567 
- qsave 2026-11-13 11:01:03 UTC epoch=1794567622: wrote=no part3_audio_age_s~6648 resume-press-1
- qsave 2026-11-13 11:02:17 UTC epoch=1794567703: wrote=yes part3_audio_age_s~6722 resume-press-1
- qsave 2026-11-13 11:03:41 UTC epoch=1794567777: wrote=yes part3_audio_age_s~6806 resume-press-1
- qsave 2026-11-13 11:05:04 UTC epoch=1794567861: wrote=yes part3_audio_age_s~6889 resume-press-1

## VM RESTART #10 — part 11 ended (11:05 UTC)
- Tenth restart, ~11:04:5x UTC. SURVIVED: continuous-audio.part11.raw
  (last write 11:05:26) + video mkv. Newest quick save 11:04:43.
  Frontier: Ch.2-2 club room. Net story ~994 min (~16.6 h).
  Recovery #12 -> part 12.

## Part 12 (resume after VM restart #10)
- resumed from data_quick_01 (11:04:43 UTC) via START -> F12 (focused, first press); position = Ch.2-2 club room, Meguru.
- underrun count at part12 start: 22
- part12 audio_start_epoch=1794568134.409007 (2026-11-13 11:08:54 UTC)
- part12 video_start_epoch=1794568134.4131637 (2026-11-13 11:08:54 UTC)
- part12 video_minus_audio_offset_s=0.004

### Part 12 — FINAL (stopped by KK's order, clean SIGINT finalize)
- files: continuous-video.part12.mkv / continuous-audio.part12.raw
- video_duration_s=4076.350 (ffprobe, header finalized — h264
  1280x720 @20fps), audio_s=4076.127 (A/V agree within 0.22 s)
- frontier: Chapter 2-2, school hallway — Hideaki + Wakaba.
  Newest quick save 12:13:35 UTC.
- audio_start_epoch=1794568134.409007129, video_start_epoch=1794568134.413163729
- qsave 2026-11-13 11:10:29 UTC epoch=1794568201: wrote=yes part3_audio_age_s~94 resume-press-1
- qsave 2026-11-13 11:11:41 UTC epoch=1794568269: wrote=yes part3_audio_age_s~166 resume-press-1
- qsave 2026-11-13 11:12:50 UTC epoch=1794568341: wrote=yes part3_audio_age_s~235 resume-press-1
- qsave 2026-11-13 11:14:02 UTC epoch=1794568410: wrote=yes part3_audio_age_s~307 resume-press-1
- qsave 2026-11-13 11:15:16 UTC epoch=1794568482: wrote=yes part3_audio_age_s~381 resume-press-1
- qsave 2026-11-13 11:16:37 UTC epoch=1794568556: wrote=yes part3_audio_age_s~462 resume-press-1
- qsave 2026-11-13 11:17:49 UTC epoch=1794568637: wrote=yes part3_audio_age_s~534 resume-press-1
- qsave 2026-11-13 11:18:58 UTC epoch=1794568709: wrote=yes part3_audio_age_s~603 resume-press-1
- health #1 2026-11-13 11:19:32 UTC epoch=1794568772: audio_bytes=244386824 audio_s~636 video_bytes=30932992 underruns_total=239 load=[1.34, 2.53, 1.58] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 11:20:09 UTC epoch=1794568779: wrote=yes part3_audio_age_s~674 resume-press-1
- qsave 2026-11-13 11:21:19 UTC epoch=1794568849: wrote=yes part3_audio_age_s~744 resume-press-1
- qsave 2026-11-13 11:22:28 UTC epoch=1794568919: wrote=yes part3_audio_age_s~813 resume-press-1
- qsave 2026-11-13 11:23:38 UTC epoch=1794568988: wrote=yes part3_audio_age_s~883 resume-press-1
- qsave 2026-11-13 11:24:47 UTC epoch=1794569058: wrote=yes part3_audio_age_s~952 resume-press-1
- qsave 2026-11-13 11:25:58 UTC epoch=1794569127: wrote=yes part3_audio_age_s~1023 resume-press-1
- qsave 2026-11-13 11:27:17 UTC epoch=1794569198: wrote=no part3_audio_age_s~1102 resume-press-1
- qsave 2026-11-13 11:28:37 UTC epoch=1794569277: wrote=no part3_audio_age_s~1182 resume-press-1
- health #2 2026-11-13 11:29:11 UTC epoch=1794569351: audio_bytes=466402744 audio_s~1214 video_bytes=64749568 underruns_total=413 load=[1.56, 2.63, 2.10] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 11:29:45 UTC epoch=1794569360: wrote=no part3_audio_age_s~1250 
- qsave 2026-11-13 11:31:02 UTC epoch=1794569425: wrote=no part3_audio_age_s~1327 resume-press-1
- qsave 2026-11-13 11:32:21 UTC epoch=1794569502: wrote=yes part3_audio_age_s~1405 resume-press-1
- qsave 2026-11-13 11:33:30 UTC epoch=1794569581: wrote=yes part3_audio_age_s~1476 resume-press-1
- qsave 2026-11-13 11:34:44 UTC epoch=1794569650: wrote=yes part3_audio_age_s~1549 resume-press-1
- qsave 2026-11-13 11:35:57 UTC epoch=1794569724: wrote=yes part3_audio_age_s~1622 resume-press-1
- qsave 2026-11-13 11:37:08 UTC epoch=1794569797: wrote=yes part3_audio_age_s~1693 resume-press-1
- qsave 2026-11-13 11:38:26 UTC epoch=1794569868: wrote=no part3_audio_age_s~1771 resume-press-1
- health #3 2026-11-13 11:38:52 UTC epoch=1794569932: audio_bytes=689427912 audio_s~1795 video_bytes=93847552 underruns_total=681 load=[0.29, 2.10, 2.35] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 11:39:45 UTC epoch=1794569946: wrote=yes part3_audio_age_s~1850 resume-press-1
- qsave 2026-11-13 11:41:01 UTC epoch=1794570025: wrote=yes part3_audio_age_s~1926 resume-press-1
- qsave 2026-11-13 11:42:18 UTC epoch=1794570101: wrote=no part3_audio_age_s~2003 resume-press-1
- qsave 2026-11-13 11:43:33 UTC epoch=1794570178: wrote=yes part3_audio_age_s~2078 resume-press-1
- qsave 2026-11-13 11:44:53 UTC epoch=1794570253: wrote=no part3_audio_age_s~2158 resume-press-1
- qsave 2026-11-13 11:46:10 UTC epoch=1794570333: wrote=yes part3_audio_age_s~2235 resume-press-1
- qsave 2026-11-13 11:47:26 UTC epoch=1794570410: wrote=yes part3_audio_age_s~2311 resume-press-1
- health #4 2026-11-13 11:48:39 UTC epoch=1794570519: audio_bytes=914720320 audio_s~2382 video_bytes=121110528 underruns_total=956 load=[6.03, 3.43, 2.96] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 11:48:48 UTC epoch=1794570486: wrote=no part3_audio_age_s~2393 resume-press-1
- qsave 2026-11-13 11:49:26 UTC epoch=1794570528: wrote=yes part3_audio_age_s~2431 resume-press-1
- qsave 2026-11-13 11:50:34 UTC epoch=1794570606: wrote=yes part3_audio_age_s~2499 resume-press-1
- qsave 2026-11-13 11:51:51 UTC epoch=1794570674: wrote=no part3_audio_age_s~2576 resume-press-1
- qsave 2026-11-13 11:53:10 UTC epoch=1794570751: wrote=yes part3_audio_age_s~2655 resume-press-1
- qsave 2026-11-13 11:54:36 UTC epoch=1794570830: wrote=no part3_audio_age_s~2741 resume-press-1
- qsave 2026-11-13 11:55:58 UTC epoch=1794570916: wrote=yes part3_audio_age_s~2823 resume-press-1
- qsave 2026-11-13 11:57:11 UTC epoch=1794570998: wrote=yes part3_audio_age_s~2896 resume-press-1
- health #5 2026-11-13 11:58:21 UTC epoch=1794571101: audio_bytes=1138098368 audio_s~2963 video_bytes=144703488 underruns_total=1526 load=[10.44, 6.04, 4.21] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 11:58:47 UTC epoch=1794571071: wrote=no part3_audio_age_s~2992 resume-press-3
- qsave 2026-11-13 11:58:50 UTC epoch=1794571107: wrote=no part3_audio_age_s~2995 
- qsave 2026-11-13 12:00:27 UTC epoch=1794571170: wrote=no part3_audio_age_s~3092 resume-press-2
- qsave 2026-11-13 12:01:56 UTC epoch=1794571267: wrote=yes part3_audio_age_s~3181 resume-press-2
- qsave 2026-11-13 12:03:28 UTC epoch=1794571356: wrote=yes part3_audio_age_s~3273 resume-press-2
- qsave 2026-11-13 12:04:44 UTC epoch=1794571448: wrote=yes part3_audio_age_s~3349 resume-press-1
- qsave 2026-11-13 12:05:58 UTC epoch=1794571524: wrote=no part3_audio_age_s~3423 resume-press-1
- qsave 2026-11-13 12:07:14 UTC epoch=1794571598: wrote=yes part3_audio_age_s~3499 resume-press-1
- health #6 2026-11-13 12:07:59 UTC epoch=1794571679: audio_bytes=1360356528 audio_s~3542 video_bytes=167510016 underruns_total=2284 load=[4.91, 4.46, 3.99] quiet=[started_epoch=1794499060 restore_due_epoch=1794787594 jobs=vn-arcade-dev-loop bluesky-continuous-posting agentic-feature-tour extended_note=KK decision 2026-11-13 09:05 JST: quiet extended until the Sanoba recording completes; restore manually via quiet.sh stop; restore_due_epoch is a 72h backstop only ]
- qsave 2026-11-13 12:08:19 UTC epoch=1794571674: wrote=no part3_audio_age_s~3564 
- qsave 2026-11-13 12:08:49 UTC epoch=1794571695: wrote=yes part3_audio_age_s~3594 resume-press-1
- qsave 2026-11-13 12:10:16 UTC epoch=1794571769: wrote=no part3_audio_age_s~3681 resume-press-1
- qsave 2026-11-13 12:11:30 UTC epoch=1794571856: wrote=yes part3_audio_age_s~3755 resume-press-1
- qsave 2026-11-13 12:12:43 UTC epoch=1794571930: wrote=yes part3_audio_age_s~3828 resume-press-1
- qsave 2026-11-13 12:14:15 UTC epoch=1794572003: wrote=yes part3_audio_age_s~3920 resume-press-3

## RECORDING LINE STOPPED BY KK'S ORDER — FINAL ENTRY (2026-11-13 21:14 JST)
- Orderly stop executed 12:15-12:17 UTC: save loop halted, AUTO
  parked on a stable dialogue frame (verified OFF, B=137), final
  F11 attempted twice — the game was healthy and parked but did not
  write; not forced. Newest quick save stands at 12:13:35 UTC
  (loop99's last write, ~3 min before the stop).
- Captures stopped with SIGINT: part 12's MKV finalized cleanly
  (ffprobe: h264 1280x720 @20fps, duration 4076.350 s, 186,217,648
  bytes); audio raw 1,565,232,712 bytes = 4076.127 s.
- Part 12 epochs: audio_start 1794568134.409 / video_start
  1794568134.413 (offset +0.004 s); stop initiated 1794572211.101;
  captures down 1794572219.214.
- Game + supervisor (pid 2911 lineage) stopped; Xvfb :113 and the
  line's PulseAudio left idle. No other line's processes touched.
- STORY FRONTIER AT STOP: Chapter 2-2, school hallway (Hideaki +
  Wakaba). Trial ending NOT reached.
- SERIES TOTALS: 12 parts, gross recorded audio 65,126.748 s
  (1085.4 min / ~18.1 h); net story ~17.8 h after ~19 min of
  resume overlaps (estimate). Chapters completed: 1-1..1-6, 2-1;
  final position mid-2-2. No choice screens encountered.
- Quiet protocol: LEFT ACTIVE per instructions — quiet.sh stop was
  NOT run; restoration is KK's separate decision.
- Correction/observation (12:17 UTC, post-stop): this line did NOT
  run quiet.sh stop and did NOT restore any job. However, at the
  post-stop check, quiet.state was ABSENT, quiet.sh status reported
  "inactive", and cron state showed all three jobs (vn-arcade-dev-
  loop, bluesky-continuous-posting, agentic-feature-tour) ENABLED —
  i.e. the restoration had already been effected outside this line
  at some point before the check (timing unknown to this line,
  consistent with the decision being handled on the main side).
  Nothing remains paused.
