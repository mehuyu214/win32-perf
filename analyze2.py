#!/usr/bin/env python3
"""Magnitude-weighted frame-change analysis.

Per consecutive-frame pair, computes mean absolute luma difference
(via tblend=difference + signalstats YAVG on a 480x270 downscale) and
counts changes/s above several magnitude thresholds, plus the longest
gap between changes above 0.1 (a clearly visible content update).
Usage: analyze2.py FILE START DUR LABEL
Appends JSON to results_change.jsonl next to this script.
"""
import json, os, re, subprocess, sys

THRESH = [0.005, 0.02, 0.1, 0.5, 2.0]

def main():
    path, start, dur, label = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    fps = 20.0
    vf = ("scale=480:270,tblend=all_mode=difference,signalstats,"
          "metadata=print:key=lavfi.signalstats.YAVG")
    cmd = ["ffmpeg", "-nostdin", "-threads", "1", "-v", "info",
           "-ss", str(start), "-i", path, "-t", str(dur),
           "-map", "0:v:0", "-vf", vf, "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    vals = [float(m) for m in re.findall(r"lavfi\.signalstats\.YAVG=([\d.]+)", out.stderr)]
    if not vals:
        print(f"{label}: NO DATA rc={out.returncode} err={out.stderr[-300:]}")
        return
    wall = len(vals) / fps
    counts = {t: sum(1 for v in vals if v >= t) for t in THRESH}
    # longest run of consecutive pairs below 0.1 (i.e. visual freeze), in seconds
    longest = cur = 0
    for v in vals:
        if v < 0.1:
            cur += 1; longest = max(longest, cur)
        else:
            cur = 0
    rec = dict(label=label, file=os.path.basename(path), start=start, dur=dur,
               pairs=len(vals),
               counts={str(t): counts[t] for t in THRESH},
               per_s={str(t): round(counts[t]/wall, 3) for t in THRESH},
               mean_yavg=round(sum(vals)/len(vals), 4),
               longest_freeze_s=round(longest/fps, 2))
    print(json.dumps(rec, ensure_ascii=False))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_change.jsonl"), "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
