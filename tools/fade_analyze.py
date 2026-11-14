#!/usr/bin/env python3
"""fade_analyze.py VIDEO [OUT.json] -- motion/fade delivery analysis.

Decodes the video at its NATIVE frame rate (no fps resampling) at
160x90 grayscale and computes, per frame step:
  mad[i]        mean abs diff vs previous frame (v2 eps=0.05 = distinct)
  bright[i]     frame mean brightness
A frame step with mad > EPS is a DISTINCT new frame delivered in that
slot (at 20 fps capture, one slot = 50 ms -- KK's unit).

Fade windows: maximal runs of distinct steps, merging runs separated
by <= MERGE_GAP non-distinct steps, keeping windows with >= MIN_DISTINCT
distinct steps. For each window: start/end (s), wall duration, distinct
frames delivered, stalled slots inside the window, longest internal
stall. A perfectly smooth fade of duration D at 20 fps would deliver
~D*20 distinct frames with 0 stalled slots; a stalled pipeline delivers
few distinct frames separated by duplicate (stalled) slots.
"""
import json, subprocess, sys
import numpy as np

W, H = 160, 90
EPS = 0.05
MERGE_GAP = 2
MIN_DISTINCT = 3


def main():
    video = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    # probe fps + frame count
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=r_frame_rate,avg_frame_rate,nb_frames",
                         "-of", "json", video], capture_output=True, text=True)
    st = json.loads(pr.stdout)["streams"][0]
    def rate(s):
        a, b = s.split("/")
        return float(a) / float(b) if float(b) else 0.0
    fps = rate(st.get("avg_frame_rate") or st["r_frame_rate"])
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video,
                          "-vf", f"scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         stdout=subprocess.PIPE)
    frames = []
    while True:
        buf = p.stdout.read(W * H)
        if len(buf) < W * H:
            break
        frames.append(np.frombuffer(buf, dtype=np.uint8).astype(np.float32))
    p.wait()
    n = len(frames)
    mad = [0.0] * n
    bright = [float(f.mean()) for f in frames]
    for i in range(1, n):
        mad[i] = float(np.abs(frames[i] - frames[i - 1]).mean())
    distinct = [1 if m > EPS else 0 for m in mad]

    # fade windows
    windows = []
    i = 1
    while i < n:
        if distinct[i]:
            start = i
            last_distinct = i
            j = i
            while j + 1 < n:
                if distinct[j + 1]:
                    last_distinct = j + 1
                    j += 1
                elif j + 1 - last_distinct <= MERGE_GAP and any(distinct[j + 2:j + 2 + MERGE_GAP + 1]):
                    j += 1
                else:
                    break
            dcount = sum(distinct[start:last_distinct + 1])
            if dcount >= MIN_DISTINCT:
                # longest internal stall within window
                stall = cur = 0
                for k in range(start, last_distinct + 1):
                    cur = cur + 1 if not distinct[k] else 0
                    stall = max(stall, cur)
                windows.append({
                    "start_s": round(start / fps, 2),
                    "end_s": round((last_distinct + 1) / fps, 2),
                    "duration_s": round((last_distinct + 1 - start) / fps, 2),
                    "distinct_frames": int(dcount),
                    "slots": int(last_distinct + 1 - start),
                    "stalled_slots": int((last_distinct + 1 - start) - dcount),
                    "longest_internal_stall_slots": int(stall),
                    "bright_start": round(bright[start - 1], 1) if start > 0 else None,
                    "bright_end": round(bright[last_distinct], 1),
                    "mad_max": round(max(mad[start:last_distinct + 1]), 3),
                })
            i = last_distinct + 1
        else:
            i += 1

    per_sec = []
    full = int(n // fps)
    for s in range(full):
        seg = distinct[int(s * fps):int((s + 1) * fps)]
        per_sec.append(int(sum(seg)))
    res = {
        "video": video, "fps": round(fps, 3), "frames": n,
        "duration_s": round(n / fps, 2),
        "distinct_total": int(sum(distinct)),
        "per_second_distinct": per_sec,
        "windows": windows,
        "mad_series": [round(m, 4) for m in mad],
        "bright_series": [round(b, 1) for b in bright],
    }
    print(json.dumps({k: res[k] for k in
                      ("video", "fps", "frames", "duration_s", "distinct_total", "windows")},
                     indent=1))
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=1)
        print("wrote", out)


if __name__ == "__main__":
    main()
