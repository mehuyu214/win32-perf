#!/usr/bin/env python3
"""Unique-frame analysis of a recorded master.

Decodes a window with ffmpeg framemd5 (full-res, exact pixel hashes) and
reports: frames/s delivered, unique frames/s, run-length distribution of
consecutive identical frames. Usage:
  analyze_frames.py FILE START_SEC DUR_SEC LABEL
Prints one summary block; also appends a JSON line to results_frames.jsonl
in this script's directory.
"""
import json, os, subprocess, sys, collections

def main():
    path, start, dur, label = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    fps = 20.0
    cmd = ["ffmpeg", "-nostdin", "-threads", "1", "-v", "error",
           "-ss", str(start), "-i", path, "-t", str(dur),
           "-map", "0:v:0", "-f", "framemd5", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    hashes = []
    for line in out.stdout.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 6:
            hashes.append(parts[5])
    n = len(hashes)
    if n == 0:
        print(f"{label}: NO FRAMES (ffmpeg rc={out.returncode}) stderr={out.stderr[:300]}")
        return
    # run lengths
    runs = []
    cur = 1
    for a, b in zip(hashes, hashes[1:]):
        if a == b:
            cur += 1
        else:
            runs.append(cur); cur = 1
    runs.append(cur)
    uniq_transitions = len(runs)  # number of distinct segments
    uniq_hashes = len(set(hashes))
    wall = n / fps
    # per-second unique transitions
    per_sec = collections.Counter()
    idx = 0
    pos = 0  # frame index of run start
    for r in runs:
        per_sec[int(pos / fps)] += 1
        pos += r
    secs = sorted(per_sec)
    ups = [per_sec[s] for s in range(int(wall))]
    runs_sorted = sorted(runs)
    median_run = runs_sorted[len(runs_sorted)//2] / fps
    p90_run = runs_sorted[int(len(runs_sorted)*0.9)] / fps
    max_run = runs_sorted[-1] / fps
    rec = dict(label=label, file=os.path.basename(path), start=start, dur=dur,
               frames=n, wall_s=round(wall,2), segments=uniq_transitions,
               unique_hashes=uniq_hashes,
               unique_per_s=round(uniq_transitions/wall, 3),
               median_run_s=round(median_run,2), p90_run_s=round(p90_run,2),
               max_run_s=round(max_run,2),
               per_sec_changes=ups)
    print(json.dumps(rec, ensure_ascii=False))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_frames.jsonl"), "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
