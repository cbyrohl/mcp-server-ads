#!/usr/bin/env python3
"""Trim idle frames from a GIF.

Detects sequences of near-identical frames (e.g. blinking cursor, no real
content change) and collapses them to a short pause, keeping all "action"
frames at their original speed.

Usage:
    uvx --with Pillow --with numpy python demos/trim_idle.py demos/demo.gif demos/demo_trimmed.gif

Options (positional):
    input_gif       Input GIF path
    output_gif      Output GIF path
    --threshold     Mean pixel diff below which frames are "idle" (default: 1.5)
    --max-idle-ms   Maximum total duration for an idle stretch in ms (default: 500)
"""

import argparse
import sys

import numpy as np
from PIL import Image


def load_frames(path):
    """Load all frames from a GIF with their durations."""
    img = Image.open(path)
    frames = []
    try:
        while True:
            frame = img.convert("RGB")
            duration = img.info.get("duration", 100)
            frames.append((frame.copy(), duration))
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames


def frame_diff(a, b):
    """Mean absolute pixel difference between two frames."""
    arr_a = np.asarray(a, dtype=np.float32)
    arr_b = np.asarray(b, dtype=np.float32)
    return np.mean(np.abs(arr_a - arr_b))


def trim_idle(frames, threshold=1.5, max_idle_ms=500):
    """Collapse runs of near-identical frames to max_idle_ms."""
    result = []
    idle_run = []

    for i, (frame, duration) in enumerate(frames):
        if i == 0:
            result.append((frame, duration))
            continue

        diff = frame_diff(frames[i - 1][0], frame)

        if diff < threshold:
            idle_run.append((frame, duration))
        else:
            # Flush idle run: keep first and last frame with reduced total duration
            if idle_run:
                total_idle = sum(d for _, d in idle_run)
                capped = min(total_idle, max_idle_ms)
                # Keep last idle frame with the capped duration
                result.append((idle_run[-1][0], capped))
                idle_run = []
            result.append((frame, duration))

    # Flush any trailing idle run
    if idle_run:
        total_idle = sum(d for _, d in idle_run)
        capped = min(total_idle, max_idle_ms)
        result.append((idle_run[-1][0], capped))

    return result


def save_gif(frames, path):
    """Save frames as an animated GIF."""
    if not frames:
        print("No frames to save.", file=sys.stderr)
        sys.exit(1)

    images = [f for f, _ in frames]
    durations = [d for _, d in frames]

    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Trim idle frames from a GIF")
    parser.add_argument("input_gif", help="Input GIF path")
    parser.add_argument("output_gif", help="Output GIF path")
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.5,
        help="Mean pixel diff below which frames are idle (default: 1.5)",
    )
    parser.add_argument(
        "--max-idle-ms",
        type=int,
        default=500,
        help="Max total duration for an idle stretch in ms (default: 500)",
    )
    args = parser.parse_args()

    print(f"Loading {args.input_gif}...")
    frames = load_frames(args.input_gif)
    print(f"  {len(frames)} frames loaded")

    original_duration = sum(d for _, d in frames)
    print(f"  Original duration: {original_duration / 1000:.1f}s")

    print(f"Trimming idle frames (threshold={args.threshold}, max_idle={args.max_idle_ms}ms)...")
    trimmed = trim_idle(frames, threshold=args.threshold, max_idle_ms=args.max_idle_ms)
    trimmed_duration = sum(d for _, d in trimmed)
    print(f"  {len(frames)} -> {len(trimmed)} frames")
    print(f"  Duration: {original_duration / 1000:.1f}s -> {trimmed_duration / 1000:.1f}s")

    print(f"Saving {args.output_gif}...")
    save_gif(trimmed, args.output_gif)
    print("Done.")


if __name__ == "__main__":
    main()
