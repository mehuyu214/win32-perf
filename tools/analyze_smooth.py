#!/usr/bin/env python3
"""analyze_smooth.py VIDEO [OUT.json] -- KK-score + magnitude companion.

KK's picture-hash score saturates when sub-perceptual dither flips the
160x90 hash every frame (measured 2026-11-13: consecutive-frame max
diff 2/255 across the whole frame). This companion reports, per second:
  kk_pts      - KK hash points (score_frames.py definition)
  meaningful  - frames whose mean-abs-diff at 160x90 gray exceeds
                MEANINGFUL (default 0.05 gray levels)
and global stats: inter-change gap distribution for meaningful frames
(max/p95 gap in frames), max run of hash-unchanged frames.
"""
import json, subprocess, sys
import numpy as np

W, H, FPS = 160, 90, 20
MEANINGFUL = 0.05

def main():
    video = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf",
                          f"fps={FPS},scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         stdout=subprocess.PIPE)
    prev = None
    mg = []  # per-frame 0/1 (thresholded MAD; NO hash scoring -- v1 retired)
    while True:
        buf = p.stdout.read(W * H)
        if len(buf) < W * H:
            break
        f = np.frombuffer(buf, dtype=np.uint8).astype(np.int16)
        if prev is not None:
            mg.append(1 if np.abs(f - prev).mean() > MEANINGFUL else 0)
        prev = f
    mg = np.array(mg)
    nsec = len(mg) // FPS
    mg_s = [int(mg[i*FPS:(i+1)*FPS].sum()) for i in range(nsec)]
    idx = np.nonzero(mg)[0]
    gaps = np.diff(idx) if len(idx) > 1 else np.array([len(mg)])
    # longest run without meaningful change (frames)
    maxrun = cur = 0
    for v in mg:
        cur = cur + 1 if v == 0 else 0
        maxrun = max(maxrun, cur)
    res = {
        "video": video, "frames": int(len(mg) + 1),
        "meaningful_mean_per_s": round(float(np.mean(mg_s)), 2),
        "meaningful_seconds_zero": int(sum(1 for x in mg_s if x == 0)),
        "meaningful_total_frames": int(mg.sum()),
        "meaningful_gap_max_frames": int(gaps.max()) if len(gaps) else None,
        "meaningful_gap_p95_frames": float(np.percentile(gaps, 95)) if len(gaps) else None,
        "longest_no_meaningful_change_s": round(maxrun / FPS, 2),
        "meaningful_per_second": mg_s,
    }
    print(json.dumps({k: v for k, v in res.items() if 'per_second' not in k}, indent=1))
    if out:
        json.dump(res, open(out, "w"), indent=1)
        print("wrote", out)

if __name__ == "__main__":
    main()
