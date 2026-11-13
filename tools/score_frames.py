#!/usr/bin/env python3
"""score_frames.py VIDEO [OUT_PREFIX] -- KK's picture-change score.

Splits VIDEO at 20 fps; each frame is downscaled to 160x90 grayscale and
hashed; a frame scores 1 point if its picture-hash differs from the
previous frame's. Output: <prefix>.json (summary + per-second series),
<prefix>.csv (second, points), <prefix>.png (points-per-second graph).
Ideal (KK): 10 pts/s.
"""
import hashlib, json, subprocess, sys, os
import numpy as np

def main():
    video = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(video)[0] + "-scores"
    W, H, FPS = 160, 90, 20
    cmd = ["ffmpeg", "-v", "error", "-i", video, "-vf",
           f"fps={FPS},scale={W}:{H},format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    framesz = W * H
    prev = None
    changed = []  # 1 per changed frame, in order
    total = 0
    while True:
        buf = p.stdout.read(framesz)
        if len(buf) < framesz:
            break
        total += 1
        h = hashlib.md5(buf).hexdigest()
        changed.append(1 if (prev is not None and h != prev) else 0)
        prev = h
    p.wait()
    if p.returncode != 0:
        print("ffmpeg failed", file=sys.stderr); return 1
    # per-second aggregation: FPS frames per second
    nsec = (total + FPS - 1) // FPS
    per_sec = [int(sum(changed[i*FPS:(i+1)*FPS])) for i in range(nsec)]
    mean = float(np.mean(per_sec)) if per_sec else 0.0
    summary = {
        "video": video, "fps": FPS, "downscale": [W, H], "frames": total,
        "duration_s": total / FPS, "mean_pts_per_s": round(mean, 3),
        "median_pts_per_s": round(float(np.median(per_sec)), 3) if per_sec else 0.0,
        "seconds_ge_10": int(sum(1 for v in per_sec if v >= 10)),
        "seconds_total": nsec,
        "per_second": per_sec,
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
    ax.set_title(f"picture-change score: {os.path.basename(video)}  mean={mean:.2f} pts/s")
    ax.set_ylim(0, max(12, max(per_sec) + 2) if per_sec else 12)
    ax.legend()
    fig.tight_layout(); fig.savefig(prefix + ".png", dpi=100)
    print(json.dumps({k: summary[k] for k in
                      ("frames", "duration_s", "mean_pts_per_s", "median_pts_per_s",
                       "seconds_ge_10", "seconds_total")}, indent=1))
    print("wrote", prefix + ".json/.csv/.png")
    return 0

if __name__ == "__main__":
    sys.exit(main())
