#!/usr/bin/env python3
"""Sample every thread of a qemu process via /proc at 10 Hz for DUR s.

Per snapshot per tid: state, wchan, utime+stime (ticks). Output CSV:
t,tid,state,wchan,ticks. Summary JSON: per-tid CPU delta, dominant
wchan share, % of samples in R state. No ptrace needed.
Usage: tsample.py PID DUR OUT.csv
"""
import json, os, sys, time, collections

def main():
    pid, dur, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    taskdir = f"/proc/{pid}/task"
    rows = []
    t0 = time.monotonic()
    while time.monotonic() - t0 < dur:
        t = time.monotonic() - t0
        try:
            tids = os.listdir(taskdir)
        except FileNotFoundError:
            break
        for tid in tids:
            try:
                with open(f"{taskdir}/{tid}/stat", "rb") as f:
                    parts = f.read().rsplit(b")", 1)[1].split()
                state = parts[0].decode()
                ticks = int(parts[11]) + int(parts[12])  # utime+stime after comm
                try:
                    with open(f"{taskdir}/{tid}/wchan") as f:
                        wchan = f.read().strip() or "-"
                except OSError:
                    wchan = "?"
                rows.append((round(t, 2), tid, state, wchan, ticks))
            except (FileNotFoundError, ProcessLookupError, IndexError):
                continue
        dt = 0.1 - (time.monotonic() - t0) % 0.1
        time.sleep(max(0.005, dt))
    with open(outp, "w") as f:
        f.write("t,tid,state,wchan,ticks\n")
        for r in rows:
            f.write(",".join(map(str, r)) + "\n")
    # summary
    byt = collections.defaultdict(list)
    for t, tid, state, wchan, ticks in rows:
        byt[tid].append((t, state, wchan, ticks))
    summ = {}
    for tid, lst in byt.items():
        cpu = lst[-1][3] - lst[0][3]
        wch = collections.Counter(w for _, _, w, _ in lst)
        rstates = sum(1 for _, s, _, _ in lst if s == "R")
        summ[tid] = dict(samples=len(lst), cpu_ticks=cpu,
                         r_pct=round(100 * rstates / len(lst), 1),
                         top_wchan=wch.most_common(3))
    print(json.dumps(summ, indent=0))
    return 0

if __name__ == "__main__":
    sys.exit(main())
