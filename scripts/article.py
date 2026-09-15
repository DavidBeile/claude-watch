#!/usr/bin/env python3
"""Write a structured, ingest-shaped report.md for a fetched web article.

The text counterpart to `report.py`. Where a video report is anchored on
timestamps (frames, transcript segments, pacing), an article report is
anchored on structure: the heading outline, word count, and the links the
page points at.

The division of labour is identical to the video path: this script fills
everything that can be computed, and emits `<!-- pending Claude fill: <hint> -->`
markers for the narrative sections Claude writes before ingest. The section
names match `report.py` on purpose — TL;DR, Entities, Concepts — so the same
Obsidian Ingest op consumes a watched video and a read article without
special-casing either.

Fetching is NOT this script's job. The Scrapling MCP server retrieves the
page; this script only shapes what came back.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

from report import _pending

WORDS_PER_MINUTE = 200


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _reading_time(words: int) -> str:
    if words == 0:
        return "0 min"
    return f"{max(1, round(words / WORDS_PER_MINUTE))} min"


def _yaml_scalar(value: str | None) -> str:
    """Quote a frontmatter value only when it would otherwise break the YAML.

    Deliberately narrow: a bare URL stays unquoted so that `source:` reads the
    same here as it does in a video report from `report.py`. A colon only
    forces quoting when followed by whitespace, which is what actually ends
    the key in YAML — `https://x` is safe, `Title: subtitle` is not.
    """
    if not value:
        return "(unknown)"
    raw = str(value)
    flat = " ".join(raw.split())
    needs_quotes = (
        flat != raw  # contained newlines or runs of whitespace
        or ": " in flat
        or flat.endswith(":")
        or " #" in flat
        or flat[0] in "-?:,[]{}#&*!|>'\"%@`"
    )
    if needs_quotes:
        return '"' + flat.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return flat


def _outline(headings: list[dict]) -> list[str]:
    """Render headings as an indented outline, one line per heading."""
    lines: list[str] = []
    for h in headings:
        level = max(1, min(6, int(h.get("level", 2))))
        text = " ".join(str(h.get("text", "")).split())
        if not text:
            continue
        lines.append(f"{'  ' * (level - 1)}- {text}")
    return lines


def write_article_report(
    out_path: Path,
    source: str,
    title: str,
    intent: str,
    text: str,
    author: str | None = None,
    site: str | None = None,
    published: str | None = None,
    headings: list[dict] | None = None,
    links: list[dict] | None = None,
    fetch_mode: str = "http",
    selector: str | None = None,
    http_status: int | None = None,
    truncated: bool = False,
    fetched_at: _dt.datetime | None = None,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fetched_at = fetched_at or _dt.datetime.now().astimezone()
    headings = headings or []
    links = links or []

    words = _word_count(text)
    lines: list[str] = []

    lines.append("---")
    lines.append(f"source: {_yaml_scalar(source)}")
    lines.append(f"title: {_yaml_scalar(title)}")
    lines.append(f"author: {_yaml_scalar(author)}")
    lines.append(f"site: {_yaml_scalar(site)}")
    lines.append(f"published: {_yaml_scalar(published)}")
    lines.append(f"fetched_at: {fetched_at.isoformat()}")
    lines.append(f"intent: {intent or '(none)'}")
    lines.append(f"word_count: {words}")
    lines.append(f"reading_time: {_reading_time(words)}")
    lines.append(f"fetch_mode: {fetch_mode}")
    lines.append(f"selector: {_yaml_scalar(selector)}")
    lines.append(f"http_status: {http_status if http_status is not None else '(unknown)'}")
    lines.append(f"truncated: {'true' if truncated else 'false'}")
    lines.append("---")
    lines.append("")

    lines.append(f"# {title}")
    lines.append("")

    if truncated:
        lines.append(
            "> **Incomplete fetch.** The extracted text was cut short — the sections "
            "below describe only what came back. Re-fetch before ingesting if the "
            "article matters."
        )
        lines.append("")

    lines.append("## TL;DR")
    lines.append("")
    lines.append(_pending(
        f"3-5 bullets through the lens of: '{intent or 'general summary'}'"
    ))
    lines.append("")

    lines.append("## Key points")
    lines.append("")
    lines.append(_pending(
        "5-10 bullets in `- **<claim>** — <supporting detail>` format. "
        "Anchor each to a section heading from the outline below when the "
        "article is long enough to have one."
    ))
    lines.append("")

    lines.append("## Notable quotes")
    lines.append("")
    lines.append(_pending(
        "Top 3-5 verbatim lines worth citing, each followed by the heading it "
        "sits under. Quote exactly — do not paraphrase into quotation marks."
    ))
    lines.append("")

    lines.append("## Structure")
    lines.append("")
    lines.append(f"- Words: {words}")
    lines.append(f"- Reading time: {_reading_time(words)}")
    lines.append(f"- Headings: {len(headings)}")
    lines.append(f"- Outbound links: {len(links)}")
    lines.append(f"- Fetch mode: {fetch_mode}")
    lines.append("")
    outline = _outline(headings)
    if outline:
        lines.append("### Outline")
        lines.append("")
        lines.extend(outline)
        lines.append("")
    else:
        lines.append("_No headings — a flat page, a paywall stub, or a narrow selector._")
        lines.append("")
    lines.append(_pending(
        "One-line shape fingerprint: e.g. 'Listicle, 7 numbered sections, "
        "heavy on product links.' Inferred from the outline plus the text."
    ))
    lines.append("")

    lines.append("## Entities mentioned")
    lines.append("")
    lines.append("- People: " + _pending("comma-separated, [[wikilink]]-ready"))
    lines.append("- Companies: " + _pending("comma-separated"))
    lines.append("- Tools / products: " + _pending("comma-separated"))
    lines.append("- Places: " + _pending("comma-separated, or omit if none"))
    lines.append("")

    lines.append("## Concepts surfaced")
    lines.append("")
    lines.append(_pending(
        "List of concept: one-line gist. Frameworks, mental models, named "
        "patterns. These map to wiki/concepts/ pages."
    ))
    lines.append("")

    lines.append("## Full text")
    lines.append("")
    if text.strip():
        lines.append(f"_Fetched {fetched_at.date().isoformat()} from {source}._")
        lines.append("")
        lines.append("```")
        lines.extend(text.strip().splitlines())
        lines.append("```")
    else:
        lines.append("_No text extracted._")
    lines.append("")

    lines.append("## Links")
    lines.append("")
    if links:
        lines.append(f"_Total: {len(links)}._")
        lines.append("")
        for link in links:
            href = str(link.get("href", "")).strip()
            if not href:
                continue
            label = " ".join(str(link.get("text", "")).split()) or href
            lines.append(f"- [{label}]({href})")
    else:
        lines.append("_None extracted._")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: article.py <kwargs.json> [<out.md>]", file=sys.stderr)
        raise SystemExit(2)
    payload = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("report.md")
    write_article_report(out_path=out, **payload)
    print(str(out.resolve()))
