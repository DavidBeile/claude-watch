# Changelog

All notable changes to `/watch` are documented here.

## [Unreleased]

### Added
- `scripts/youtube.py` — read-only YouTube Data + Analytics client for your own channel, pure stdlib. Subcommands: `auth` (OAuth installed-app loopback flow), `videos`, `retention`, `channel`, `traffic`. The point of it is `retention`: it returns the audience-retention curve plus a summary naming the steepest drop-off (in seconds, not just ratios) and the worst `relativeRetentionPerformance` point — the metric that separates "viewers leave here" from "viewers leave here faster than they do on comparable videos". Scopes are `yt-analytics.readonly` and `youtube.readonly` only; it cannot upload, edit or delete. Credentials live in `~/.config/watch/.env`, the refresh token in `~/.config/watch/youtube-token.json` at mode 0600. Inert unless `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` are set.
- 20 tests in `scripts/tests/test_youtube.py` covering duration parsing, Analytics row shaping, retention summarisation and token-freshness logic.

### Fixed
- Hook microscope no longer skips videos under 30 seconds. It previously returned `skipped_reason: "video <30s"` for anything shorter, which meant YouTube Shorts — whose sweet spot is 15-35s — never got a hook analysis at all, exactly where the hook matters most. Short videos now get the word-level Whisper transcript (the half that carries the analysis) while skipping only the 2 fps frame re-pass, since the main pass already samples a short video densely; `analyse_hook()` reuses the main pass's frames inside the hook window instead. The report says which of the two it was. With no Whisper key set there is genuinely nothing to gain on a short video, and the report states that rather than implying a missing feature.

### Changed
- `analyse_hook()` takes `main_pass_frames` and returns `frames_source` (`"dense-repass"` or `"main-pass"`). The audio slice is now clamped to the video's end, so a 6-second clip no longer asks ffmpeg for 10 seconds of audio.
- `watch.py` reports a specific hook skip reason (`--no-hook-microscope` or `focused mode`) instead of one string naming all three possible causes.
- 12 tests added in `scripts/tests/test_hook.py`.

## [0.2.0] — 2026-05-25

Based on [bradautomates/claude-video](https://github.com/bradautomates/claude-video) v0.1.3 by Bradley Bonanno (MIT). Its pipeline (yt-dlp + ffmpeg + Whisper) is preserved; everything below is additive.

### Added
- Scene-change frame extraction in `scripts/frames.py` — `extract_scene_change()` + `select_hero_frames()` using ffmpeg's `select=gt(scene,...)` filter. One frame per detected shot instead of uniform every-N-seconds sampling. Keeps token cost flat on long videos. Uniform sampling still available as a fallback for static/screen-recorded sources.
- 0-10s hook microscope in `scripts/hook.py` — 2 fps frames + word-level Whisper transcript on the opening 10 seconds, so the report can tell you what's on screen *as each word lands*.
- Editorial pacing metrics in `scripts/pacing.py` — shot count, cuts/min, mean + median shot length.
- Structured `report.md` emitter in `scripts/report.py` — fixed-schema ingest-ready report with `<!-- pending Claude fill: ... -->` markers for narrative sections (TL;DR, key moments, hook breakdown, editorial profile, quotable moments, entities, concepts).
- Word-level timestamps in `scripts/whisper.py` (Groq + OpenAI backends extended).
- New CLI flags in `scripts/watch.py`: `--intent`, `--no-scene-change`, `--no-hook-microscope`.
- Step 4.4 (stage to Obsidian vault) + Step 4.5 (ingest gate) in `SKILL.md` — optional auto-save to your Obsidian vault. Path resolved via `$WATCH_VAULT_DIR` or auto-detected from `~/Second brain/`, `~/Documents/Obsidian/`, `~/Obsidian/`. Skips cleanly when no vault is detected.
- 7 unit tests under `scripts/tests/` (stdlib `unittest`, no pytest dependency).

### Changed
- `SKILL.md` is now a v2 contract — describes the structured report, the marker-fill step, and the vault config. Backwards-compatible with /watch invocations that don't care about ingest.
- README documents the added features and the `$WATCH_VAULT_DIR` configuration.

## [0.1.3] — 2026-05-09

### Fixed
- Windows: `video.info.json` is read as UTF-8 (#4). Previously `Path.read_text()` defaulted to cp1252 on Windows and crashed on yt-dlp's UTF-8 output, silently dropping Title/Uploader from the report. Same fix applied to `.env` reads/writes in `whisper.py` and `setup.py`.
- `download.py` now logs info.json parse failures to stderr instead of swallowing them.

### Security
- Hardened subprocess argv against option injection (#2): inserted `--` before the URL in the yt-dlp argv, and tightened `is_url` to reject `-`-prefixed sources and require a non-empty netloc. Resolved video/audio paths to absolute via `Path.resolve()` before passing to `ffmpeg`/`ffprobe`, so a relative path starting with `-` can't be misinterpreted as a flag.

## [0.1.2] — 2026-04-24

### Fixed
- Windows console crash: removed the emoji from the long-video warning in `watch.py`; cp1252 consoles couldn't encode it.
- `setup.py` now prints `winget` / `pip` install commands on Windows instead of "unsupported platform" — matches what the README already promised.

### Changed
- `SKILL.md` notes that on Windows the scripts must be invoked with `python`, not `python3` (the latter is the Microsoft Store stub on Windows).

## [0.1.1] — 2026-04-24

### Fixed
- Added `commands/watch.md` shim so `/watch` is callable when installed as a Claude Code plugin. Without it, the plugin loaded but the skill wasn't exposed as a slash command.
- `scripts/build-skill.sh` now strips `commands/` from the claude.ai `.skill` bundle alongside `hooks/` and `.claude-plugin/`.

## [0.1.0] — 2026-04-24

Initial marketplace release.

### Added
- `/watch <url-or-path> [question]` slash command.
- yt-dlp download with native caption extraction (manual + auto-subs).
- ffmpeg frame extraction with auto-scaled fps (≤2 fps, ≤100 frames, duration-aware budget).
- `--start` / `--end` focused mode with denser frame budget and transcript range filtering.
- Whisper fallback (Groq preferred, OpenAI secondary) for videos without captions.
- `setup.py` preflight: silent `--check`, structured `--json`, and installer that auto-runs `brew install` on macOS.
- Session-start hook that prints a one-line status on first run / partial config.
- `.skill` bundle packaging for claude.ai upload via `scripts/build-skill.sh`.
