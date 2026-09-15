#!/usr/bin/env python3
"""Hook microscope: dense frames + word-level transcript over [0, 10s].

The first 10 seconds is where every retention curve gets decided. Treating
them like any other 10 seconds wastes the highest-leverage analysis budget.
This module re-runs frame extraction at 2 fps over the hook range and asks
Whisper for word-level timestamps so the reporter can align each frame to
the exact word being spoken.

Short videos (< 30s) get the word-level transcript but skip the frame
re-pass. The main pass already samples them densely enough that a 2 fps
re-extract would mostly duplicate frames — but the word timestamps are the
half that actually carries the analysis, and they are independent of frame
density. Shorts live at 15-35s, so gating the whole microscope on duration
withheld the microscope precisely where hooks matter most.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from frames import extract  # noqa: E402
from whisper import load_api_key, transcribe_audio  # noqa: E402


HOOK_DURATION_SECONDS = 10.0
HOOK_FPS = 2.0

# Below this, the main pass is already dense over the hook window and the
# 2 fps re-pass would only duplicate frames. Word timestamps still run.
FRAME_REPASS_MIN_DURATION = 30.0


def analyse_hook(
    video_path: str,
    out_dir: Path,
    backend: str | None = None,
    api_key: str | None = None,
    full_video_duration: float = 0.0,
    main_pass_frames: list[dict] | None = None,
) -> dict:
    """Run hook microscope.

    Args:
        full_video_duration: total duration; 0 means unknown (treated as long).
        main_pass_frames: frames from the caller's main extraction pass. Short
            videos reuse the ones inside the hook window instead of paying for
            a near-duplicate re-extract.

    Returns {frames, words, segments, ran, frames_source}.
    """
    # Never ask ffmpeg or Whisper for audio past the end of the video.
    hook_end = HOOK_DURATION_SECONDS
    if full_video_duration > 0:
        hook_end = min(HOOK_DURATION_SECONDS, full_video_duration)

    short = 0 < full_video_duration < FRAME_REPASS_MIN_DURATION

    if backend is None or api_key is None:
        backend, api_key = load_api_key()

    if short and not (backend and api_key):
        # Nothing left to add: no re-pass worth running, no transcript to get.
        return {"frames": [], "words": [], "segments": [], "ran": False,
                "frames_source": None,
                "skipped_reason": (
                    f"video <{FRAME_REPASS_MIN_DURATION:g}s and no Whisper key "
                    "— main-pass frames already cover the hook window"
                )}

    out_dir.mkdir(parents=True, exist_ok=True)
    if short:
        hook_frames = _frames_in_window(main_pass_frames, hook_end)
        frames_source = "main-pass"
    else:
        hook_frames_dir = out_dir / "hook_frames"
        hook_frames = extract(
            video_path, hook_frames_dir,
            fps=HOOK_FPS, resolution=512, max_frames=25,
            start_seconds=0.0, end_seconds=hook_end,
        )
        frames_source = "dense-repass"

    words: list[dict] = []
    segments: list[dict] = []

    if backend and api_key:
        try:
            if shutil.which("ffmpeg") is None:
                raise SystemExit("ffmpeg required for hook microscope")
            hook_audio = out_dir / "hook_audio.mp3"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(Path(video_path).resolve()),
                "-vn", "-acodec", "libmp3lame", "-ar", "16000",
                "-ac", "1", "-b:a", "64k",
                "-t", str(hook_end),
                str(hook_audio.resolve()),
            ], check=True, capture_output=True)
            segments, _, words = transcribe_audio(
                hook_audio, backend=backend, api_key=api_key,
                word_timestamps=True,
            )
        except SystemExit as exc:
            print(f"[hook] whisper failed: {exc}", file=sys.stderr)
        except subprocess.CalledProcessError as exc:
            print(f"[hook] ffmpeg slice failed: {exc.stderr}", file=sys.stderr)

    return {
        "frames": hook_frames,
        "words": words,
        "segments": segments,
        "ran": True,
        "frames_source": frames_source,
    }


def _frames_in_window(frames: list[dict] | None, end_seconds: float) -> list[dict]:
    """Main-pass frames falling inside [0, end_seconds]."""
    if not frames:
        return []
    return [f for f in frames
            if f.get("timestamp_seconds") is not None
            and f["timestamp_seconds"] <= end_seconds]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: hook.py <video-path> <out-dir>", file=sys.stderr)
        raise SystemExit(2)
    result = analyse_hook(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps(result, indent=2, default=str))
