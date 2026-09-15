#!/usr/bin/env python3
"""hookboard — aggregate many /watch reports into one competitive pattern board.

`/watch` analyses one video at a time. A competitive analysis needs the
*pattern across* 15-20 videos: which hook types recur, whether the fast-cut
shorts actually outperform, how much of the field leans on broadcast footage.
This script is that missing layer.

Input is a directory of per-short subdirectories, each holding:

    <dir>/<slug>/report.md      written by /watch (required)
    <dir>/<slug>/coding.json    analyst-filled judgement calls (optional)

`report.md` supplies the deterministic numbers (duration, shot count,
cuts/min, whether the hook microscope ran). `coding.json` supplies what only
a viewer can decide — hook type, material tier, ending style — plus the
performance figure that makes the rest interpretable:

    {
      "channel":       "Example NFL Channel",
      "views":         1830000,
      "hook_type":     "contrarian",   // see HOOK_TYPES
      "first_words":   "Everyone got this play wrong.",
      "material_tier": "C",            // A green / B licensed / C transformative
      "text_density":  "high",         // none | low | medium | high
      "ending":        "loop",         // loop | cliffhanger | hard_cut | cta
      "notes":         "freeform"
    }

Unknown coding fields are preserved but ignored. Missing files degrade to
"?" rather than failing — a half-coded board is still useful.

Usage:
    python3 hookboard.py <dir>                 # markdown board to stdout
    python3 hookboard.py <dir> --json          # machine-readable
    python3 hookboard.py <dir> -o board.md     # write to file
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

HOOK_TYPES = ("question", "number", "contrarian", "conflict", "visual", "other")
MATERIAL_TIERS = ("A", "B", "C", "D")

# "Shorts land between 15 and 35 seconds" — the band the playbook targets.
TARGET_DURATION = (15.0, 35.0)

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_DURATION_RE = re.compile(r"^(?:(\d+):)?(\d+):(\d+)$")


def parse_duration(text: str) -> float | None:
    """'02:15' or '01:02:15' -> seconds. None when unparseable."""
    m = _DURATION_RE.match(text.strip())
    if not m:
        return None
    hours, minutes, seconds = m.groups()
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds)


def parse_report(report_md: str) -> dict:
    """Pull the deterministic fields out of a /watch report.md."""
    out: dict = {
        "title": None, "source": None, "duration_seconds": None,
        "shot_count": None, "cuts_per_minute": None,
        "mean_shot_length": None, "median_shot_length": None,
        "hook_ran": None, "hook_skip_reason": None,
        "transcript_source": None,
    }

    fm = _FRONTMATTER_RE.match(report_md)
    if fm:
        for line in fm.group(1).splitlines():
            key, sep, value = line.partition(":")
            if not sep:
                continue
            key, value = key.strip(), value.strip()
            if key == "title":
                out["title"] = value
            elif key == "source":
                out["source"] = value
            elif key == "transcript_source":
                out["transcript_source"] = value
            elif key == "duration":
                out["duration_seconds"] = parse_duration(value)

    # Editorial profile block, emitted by scripts/report.py.
    for key, pattern in (
        ("shot_count", r"^- Shots:\s*([\d.]+)"),
        ("cuts_per_minute", r"^- Cuts/min:\s*([\d.]+)"),
        ("mean_shot_length", r"^- Mean shot length:\s*([\d.]+)s"),
        ("median_shot_length", r"^- Median shot length:\s*([\d.]+)s"),
    ):
        m = re.search(pattern, report_md, re.MULTILINE)
        if m:
            value = float(m.group(1))
            out[key] = int(value) if key == "shot_count" else value

    # Hook microscope: "_Skipped: <reason>._" or a "- Frames: N at 2 fps" line.
    hook_section = _section(report_md, "Hook microscope")
    if hook_section is not None:
        skipped = re.search(r"_Skipped:\s*(.+?)\._", hook_section)
        if skipped:
            out["hook_ran"] = False
            out["hook_skip_reason"] = skipped.group(1).strip()
        elif re.search(r"^- Frames:", hook_section, re.MULTILINE):
            out["hook_ran"] = True

    return out


def _section(markdown: str, heading_starts_with: str) -> str | None:
    """Return the body of the first '## <heading...>' section, or None."""
    pattern = re.compile(
        r"^##\s+" + re.escape(heading_starts_with) + r".*?$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(markdown)
    return m.group(1) if m else None


def load_entries(root: Path) -> list[dict]:
    """Read every <root>/<slug>/report.md, merged with its coding.json."""
    entries: list[dict] = []
    for sub in sorted(p for p in root.iterdir() if p.is_dir()):
        report_path = sub / "report.md"
        if not report_path.is_file():
            continue
        entry = {"slug": sub.name}
        entry.update(parse_report(report_path.read_text(encoding="utf-8")))

        coding_path = sub / "coding.json"
        if coding_path.is_file():
            try:
                coding = json.loads(coding_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{coding_path}: invalid JSON — {exc}") from exc
            if not isinstance(coding, dict):
                raise SystemExit(f"{coding_path}: expected a JSON object")
            entry.update(coding)
            entry["coded"] = True
        else:
            entry["coded"] = False
        entries.append(entry)
    return entries


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 1) if values else None


def summarise(entries: list[dict]) -> dict:
    """Roll the per-video rows up into the patterns worth acting on."""
    coded = [e for e in entries if e.get("coded")]
    durations = [e["duration_seconds"] for e in entries
                 if e.get("duration_seconds") is not None]
    cuts = [e["cuts_per_minute"] for e in entries
            if e.get("cuts_per_minute") is not None]

    def distribution(field: str, universe: tuple[str, ...] | None = None) -> dict:
        counts: dict[str, int] = {}
        for e in coded:
            value = e.get(field)
            if value is None:
                continue
            counts[str(value)] = counts.get(str(value), 0) + 1
        if universe:
            unknown = sorted(k for k in counts if k not in universe)
            for key in unknown:
                counts[f"{key} (unrecognised)"] = counts.pop(key)
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    # Split on the median view count so "what do the winners do differently"
    # is answerable rather than guessed at.
    with_views = [e for e in coded if isinstance(e.get("views"), (int, float))]
    top: list[dict] = []
    rest: list[dict] = []
    if len(with_views) >= 4:
        cutoff = statistics.median(e["views"] for e in with_views)
        top = [e for e in with_views if e["views"] >= cutoff]
        rest = [e for e in with_views if e["views"] < cutoff]

    def tier_stat(group: list[dict], field: str) -> float | None:
        return _median([e[field] for e in group if e.get(field) is not None])

    in_band = [d for d in durations
               if TARGET_DURATION[0] <= d <= TARGET_DURATION[1]]

    return {
        "total": len(entries),
        "coded": len(coded),
        "median_duration_seconds": _median(durations),
        "duration_in_target_band": len(in_band),
        "duration_sample": len(durations),
        "median_cuts_per_minute": _median(cuts),
        "hook_types": distribution("hook_type", HOOK_TYPES),
        "material_tiers": distribution("material_tier", MATERIAL_TIERS),
        "endings": distribution("ending"),
        "text_density": distribution("text_density"),
        "hook_microscope_skipped": sum(
            1 for e in entries if e.get("hook_ran") is False),
        "hook_skip_reasons": distribution_of_reasons(entries),
        "performance_split": {
            "compared": bool(top and rest),
            "top_n": len(top),
            "rest_n": len(rest),
            "top_median_cuts_per_minute": tier_stat(top, "cuts_per_minute"),
            "rest_median_cuts_per_minute": tier_stat(rest, "cuts_per_minute"),
            "top_median_duration_seconds": tier_stat(top, "duration_seconds"),
            "rest_median_duration_seconds": tier_stat(rest, "duration_seconds"),
            "top_hook_types": _counts([e.get("hook_type") for e in top]),
            "rest_hook_types": _counts([e.get("hook_type") for e in rest]),
        },
    }


def _counts(values: list) -> dict:
    counts: dict[str, int] = {}
    for v in values:
        if v is None:
            continue
        counts[str(v)] = counts.get(str(v), 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def distribution_of_reasons(entries: list[dict]) -> dict:
    return _counts([e.get("hook_skip_reason") for e in entries])


def _cell(value, suffix: str = "") -> str:
    if value is None:
        return "?"
    if isinstance(value, float):
        return f"{value:g}{suffix}"
    return f"{value}{suffix}"


def _views(value) -> str:
    if not isinstance(value, (int, float)):
        return "?"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return str(int(value))


def render_markdown(entries: list[dict], summary: dict) -> str:
    lines: list[str] = ["# Hookboard", ""]
    lines.append(
        f"{summary['total']} shorts analysed, {summary['coded']} fully coded."
    )
    lines.append("")

    lines.append("## Per short")
    lines.append("")
    lines.append("| Short | Channel | Views | Dur | Hook | First words | "
                 "Cuts/min | Tier | Text | Ending |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for e in sorted(entries,
                    key=lambda x: (-(x.get("views") or 0), x["slug"])):
        first = str(e.get("first_words") or "?").replace("|", "\\|")
        if len(first) > 42:
            first = first[:39] + "..."
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            e.get("title") or e["slug"],
            e.get("channel", "?"),
            _views(e.get("views")),
            _cell(e.get("duration_seconds"), "s"),
            e.get("hook_type", "?"),
            first,
            _cell(e.get("cuts_per_minute")),
            e.get("material_tier", "?"),
            e.get("text_density", "?"),
            e.get("ending", "?"),
        ))
    lines.append("")

    lines.append("## Patterns")
    lines.append("")
    lines.append(f"- Median duration: "
                 f"{_cell(summary['median_duration_seconds'], 's')} "
                 f"({summary['duration_in_target_band']}/"
                 f"{summary['duration_sample']} inside the "
                 f"{TARGET_DURATION[0]:g}-{TARGET_DURATION[1]:g}s band)")
    lines.append(f"- Median cuts/min: "
                 f"{_cell(summary['median_cuts_per_minute'])}")
    for label, key in (("Hook types", "hook_types"),
                       ("Material tiers", "material_tiers"),
                       ("Endings", "endings"),
                       ("Text density", "text_density")):
        dist = summary[key]
        rendered = ", ".join(f"{k} ×{v}" for k, v in dist.items()) or "—"
        lines.append(f"- {label}: {rendered}")
    lines.append("")

    split = summary["performance_split"]
    lines.append("## Above vs. below median views")
    lines.append("")
    if not split["compared"]:
        lines.append(
            "_Not enough coded `views` to split (need 4+). Add view counts to "
            "`coding.json` — this is the section that turns the board from a "
            "description into a decision._"
        )
    else:
        lines.append(f"Top {split['top_n']} vs. bottom {split['rest_n']}:")
        lines.append("")
        lines.append("| Metric | Top | Rest |")
        lines.append("|---|---|---|")
        lines.append("| Median cuts/min | {} | {} |".format(
            _cell(split["top_median_cuts_per_minute"]),
            _cell(split["rest_median_cuts_per_minute"])))
        lines.append("| Median duration | {} | {} |".format(
            _cell(split["top_median_duration_seconds"], "s"),
            _cell(split["rest_median_duration_seconds"], "s")))
        lines.append("| Hook types | {} | {} |".format(
            ", ".join(f"{k} ×{v}" for k, v in split["top_hook_types"].items())
            or "—",
            ", ".join(f"{k} ×{v}" for k, v in split["rest_hook_types"].items())
            or "—"))
    lines.append("")

    skipped = summary["hook_microscope_skipped"]
    if skipped:
        reasons = ", ".join(
            f"{k} ×{v}" for k, v in summary["hook_skip_reasons"].items())
        lines.append("## Caveat")
        lines.append("")
        lines.append(
            f"The hook microscope was skipped on {skipped}/{summary['total']} "
            f"shorts ({reasons}). Those rows have no word-level transcript, so "
            f"their `first_words` came from the regular pass and are less "
            f"precise."
        )
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate /watch reports into a competitive pattern board.")
    parser.add_argument("directory", type=Path,
                        help="directory of per-short subdirectories")
    parser.add_argument("--json", action="store_true",
                        help="emit JSON instead of markdown")
    parser.add_argument("-o", "--out", type=Path,
                        help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"error: not a directory: {args.directory}", file=sys.stderr)
        return 2

    entries = load_entries(args.directory)
    if not entries:
        print(f"error: no <slug>/report.md found under {args.directory}",
              file=sys.stderr)
        return 1

    summary = summarise(entries)
    output = (json.dumps({"entries": entries, "summary": summary}, indent=2)
              if args.json else render_markdown(entries, summary))

    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
