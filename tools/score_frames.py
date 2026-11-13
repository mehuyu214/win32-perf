#!/usr/bin/env python3
"""score_frames.py VIDEO [OUT_PREFIX] [THRESHOLD] -- KK's picture-change score.

v2 (2026-11-13, measurement-integrity fix): v1 scored a frame as changed
when its exact MD5 hash of the 160x90 grayscale frame differed from the
previous frame. That saturated on sub-perceptual dither: consecutive
frames differing by <=2/255 over the whole screen flipped the hash every
frame, so an essentially static screen scored 19.3 pts/s (cap-base2) --
the same failure mode as the literal-hash method rejected in Phase 1.1
(settled title 19.92 pts/s). v2 counts a frame as changed only when the
mean absolute difference of the 160x90 grayscale frames exceeds
THRESHOLD (default 0.05 gray levels on the 0-255 scale).

Calibration (2026-11-13, /tmp/calib.py):
  settled title, cap-op-virgl.mkv 200-260s (near-static ref):
      max per-frame diff 0.0037, p99 0.0016  -> any eps >= 0.01 scores 0
  cap-env-story60:  event band 0.13-0.79;  frac>0.05 = 0.021
  cap-base2-story60: event band 0.13-0.77; frac>0.05 = 0.028
  (low dither/drift band tops out ~0.012; event band starts ~0.13 --
  the valley is wide, eps=0.05 sits in it with 4x margin over static)
Output: <prefix>.json (summary + per-second series + per-frame MAD series
head for audit), <prefix>.csv (second, points), <prefix>.png (graph).
Ideal (KK): 10 pts/s.
"""
import json, subprocess, sys, os
import numpy as np

THRESHOLD = 0.05

def main():
    video = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(video)[0] + "-scores"
    thresh = float(sys.argv[3]) if len(sys.argv) > 3 else THRESHOLD
    W, H, FPS = 160, 90, 20
    cmd = ["ffmpeg", "-v", "error", "-i", video, "-vf",
           f"fps={FPS},scale={W}:{H},format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    framesz = W * H
    prev = None
    changed = []  # 1 per changed frame, in order
    mad = []      # mean abs diff per frame (audit)
    total = 0
    while True:
        buf = p.stdout.read(framesz)
        if len(buf) < framesz:
            break
        total += 1
        f = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
        if prev is not None:
            d = float(np.abs(f - prev).mean())
            mad.append(round(d, 4))
            changed.append(1 if d > thresh else 0)
        prev = f
    p.wait()
    if p.returncode != 0:
        print("ffmpeg failed", file=sys.stderr); return 1
    nsec = (total + FPS - 1) // FPS
    per_sec = [int(sum(changed[i*FPS:(i+1)*FPS])) for i in range(nsec)]
    mean = float(np.mean(per_sec)) if per_sec else 0.0
    summary = {
        "video": video, "fps": FPS, "downscale": [W, H], "frames": total,
        "duration_s": total / FPS, "method": "thresholded-mad-v2",
        "threshold": thresh,
        "mean_pts_per_s": round(mean, 3),
        "median_pts_per_s": round(float(np.median(per_sec)), 3) if per_sec else 0.0,
        "seconds_ge_10": int(sum(1 for v in per_sec if v >= 10)),
        "seconds_zero": int(sum(1 for v in per_sec if v == 0)),
        "seconds_total": nsec,
        "per_second": per_sec,
        "mad_first_120": mad[:120],
        "mad_max": max(mad) if mad else 0.0,
        "mad_median": round(float(np.median(mad)), 4) if mad else 0.0,
    }
    with open(prefix + ".json", "w") as f:
        json.dump(summary, f, indent=1)
    with open(prefix + ".csv", "w") as f:
        f.write("second,points\n")
        for i, v in enumerate(per_sec):
            f.write(f"{i},{v}\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.bar(range(nsec), per_sec, width=1.0)
    ax.axhline(10, color="red", linestyle="--", linewidth=1, label="ideal 10 pts/s")
    ax.set_xlabel("second"); ax.set_ylabel("changed frames (pts/s)")
    ax.set_title(f"picture-change score v2 (eps={thresh}): {os.path.basename(video)}  mean={mean:.2f} pts/s")
    ax.set_ylim(0, max(12, max(per_sec) + 2) if per_sec else 12)
    ax.legend()
    fig.tight_layout(); fig.savefig(prefix + ".png", dpi=100)
    print(json.dumps({k: summary[k] for k in
                      ("frames", "duration_s", "method", "threshold",
                       "mean_pts_per_s", "median_pts_per_s",
                       "seconds_ge_10", "seconds_zero", "seconds_total")}, indent=1))
    print("wrote", prefix + ".json/.csv/.png")
    return 0

if __name__ == "__main__":
    sys.exit(main())
