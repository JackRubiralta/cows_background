#!/usr/bin/env python3
"""Find the most seamless loop in a video.

Every frame is shrunk to a 48x27 greyscale thumbnail (small enough to ignore
film grain) and compared with every other frame. A loop that plays frames
START..END-1 and then jumps back to START is invisible when frame END looks
like frame START, and the frames around them look alike too, so the motion
carries on across the jump. The best such pair wins; among pairs that are
nearly as good, the longest loop wins.

Prints one line: START END FPS RATIO
  START, END  half-open frame range of the loop, counted from the start of
              the file
  RATIO       seam jump divided by the video's typical frame-to-frame change:
              about 1 or less is invisible, 2 is a small hiccup, 3+ is a cut
"""

import argparse
import json
import math
import subprocess
import sys

import numpy as np

W, H = 48, 27
WINDOW = 2          # compare frames END+k with START+k for k in -WINDOW..WINDOW
BLOCK = 512         # rows per block, keeps memory flat on long videos
NEAR_BEST = 1.03    # pairs within 3% of the best seam count as equally good


def probe_fps(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=avg_frame_rate,r_frame_rate", "-of", "json", path],
        check=True, capture_output=True, text=True).stdout
    stream = json.loads(out)["streams"][0]
    for key in ("avg_frame_rate", "r_frame_rate"):
        num, _, den = stream.get(key, "0/0").partition("/")
        if float(den or 0) > 0 and float(num) > 0:
            return float(num) / float(den)
    sys.exit("find-loop: could not read the frame rate")


def thumbnails(path, start, end, fps):
    cmd = ["ffmpeg", "-v", "error"]
    if start > 0:
        # Half a frame early, so the frame at exactly START is included.
        cmd += ["-ss", f"{max(start - 0.5 / fps, 0):.6f}"]
    cmd += ["-i", path]
    if end is not None:
        cmd += ["-t", f"{end - start:.6f}"]
    cmd += ["-an", "-vf", f"scale={W}:{H}:flags=area,format=gray",
            "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, W * H).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--start", type=float, default=0.0, help="ignore everything before this (seconds)")
    ap.add_argument("--end", type=float, default=None, help="ignore everything after this (seconds)")
    ap.add_argument("--min-loop", type=float, default=10.0, help="shortest loop allowed (seconds)")
    args = ap.parse_args()

    fps = probe_fps(args.video)
    v = thumbnails(args.video, args.start, args.end, fps)
    n = len(v)
    min_gap = max(int(round(args.min_loop * fps)), 2 * WINDOW + 2)
    if n < min_gap + 2 * WINDOW + 1:
        sys.exit(f"find-loop: only {n} frames, too short for a {args.min_loop:g}s loop")

    # Long videos are compared on every step-th frame; the winner is then
    # refined frame by frame.
    step = max(1, math.ceil(n / 12000))
    best = search(v, step, min_gap, 0, n, 0, n)
    if step > 1:
        _, i, j = best
        best = search(v, 1, min_gap, i - 2 * step, i + 2 * step + 1, j - 2 * step, j + 2 * step + 1)
    score, end, start = best

    steps = np.sqrt(((v[1:] - v[:-1]) ** 2).mean(1))
    normal = float(np.median(steps)) or 1.0
    offset = int(round(args.start * fps))
    print(start + offset, end + offset, f"{fps:.6f}", f"{score / normal:.2f}")


def search(v, step, min_gap, i0, i1, j0, j1):
    """Best (score, i, j) with i - j >= min_gap; frame i is replaced by frame j."""
    n = len(v)
    idx = np.arange(WINDOW, n - WINDOW, step)
    rows = idx[(idx >= i0) & (idx < i1)]
    cols = idx[(idx >= j0) & (idx < j1)]
    sq = (v ** 2).sum(1)
    found = []
    for b in range(0, len(rows), BLOCK):
        r = rows[b:b + BLOCK]
        acc = np.zeros((len(r), len(cols)), np.float32)
        for k in range(-WINDOW, WINDOW + 1):
            a, c = v[r + k], v[cols + k]
            d = sq[r + k][:, None] + sq[cols + k][None, :] - 2 * a @ c.T
            acc += np.sqrt(np.maximum(d, 0) / v.shape[1])
        acc /= 2 * WINDOW + 1
        acc[(r[:, None] - cols[None, :]) < min_gap] = np.inf
        flat = np.argsort(acc, axis=None)[:64]
        for f in flat:
            ri, ci = np.unravel_index(f, acc.shape)
            if np.isfinite(acc[ri, ci]):
                found.append((float(acc[ri, ci]), int(r[ri]), int(cols[ci])))
    if not found:
        sys.exit("find-loop: no loop long enough; try a smaller --min-loop")
    top = min(s for s, _, _ in found)
    good = [f for f in found if f[0] <= top * NEAR_BEST]
    return max(good, key=lambda f: (f[1] - f[2], -f[0]))


if __name__ == "__main__":
    main()
