"""Tests for the hookboard aggregator."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hookboard import (  # noqa: E402
    load_entries, main, parse_duration, parse_report, render_markdown, summarise,
)

# Mirrors what scripts/report.py actually emits.
REPORT_TEMPLATE = """---
source: {source}
title: {title}
duration: {duration}
watched_at: 2026-09-15T10:00:00+02:00
intent: hook study
hero_frames: [frame_0000.jpg]
transcript_source: captions
---

# {title}

## TL;DR

- something

## Hook microscope (0-10s)

{hook_block}

## Editorial profile

- Shots: {shots}
- Cuts/min: {cuts}
- Mean shot length: {mean}s
- Median shot length: {median}s
- Talking-head ratio: n/a (opencv not installed)

## Transcript

_No transcript available._
"""

HOOK_RAN = "- Frames: 20 at 2 fps\n- Word-level transcript (5 words):"
HOOK_SKIPPED = "_Skipped: video <30s._"


def write_short(root: Path, slug: str, *, duration="00:28", shots=9,
                cuts=19.3, hook_block=HOOK_SKIPPED, coding=None,
                title=None) -> Path:
    d = root / slug
    d.mkdir(parents=True)
    (d / "report.md").write_text(
        REPORT_TEMPLATE.format(
            source=f"https://youtu.be/{slug}", title=title or f"Short {slug}",
            duration=duration, shots=shots, cuts=cuts, mean=3.1, median=2.8,
            hook_block=hook_block,
        ),
        encoding="utf-8",
    )
    if coding is not None:
        (d / "coding.json").write_text(json.dumps(coding), encoding="utf-8")
    return d


class TestParseDuration(unittest.TestCase):

    def test_mm_ss(self):
        self.assertEqual(parse_duration("00:28"), 28)
        self.assertEqual(parse_duration("02:15"), 135)

    def test_hh_mm_ss(self):
        self.assertEqual(parse_duration("01:02:15"), 3735)

    def test_unparseable(self):
        self.assertIsNone(parse_duration("banana"))
        self.assertIsNone(parse_duration(""))


class TestParseReport(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hookboard-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_extracts_frontmatter_and_pacing(self):
        d = write_short(self.tmp, "abc", duration="00:31", shots=12, cuts=23.2)
        got = parse_report((d / "report.md").read_text())
        self.assertEqual(got["title"], "Short abc")
        self.assertEqual(got["source"], "https://youtu.be/abc")
        self.assertEqual(got["duration_seconds"], 31)
        self.assertEqual(got["shot_count"], 12)
        self.assertEqual(got["cuts_per_minute"], 23.2)
        self.assertEqual(got["mean_shot_length"], 3.1)
        self.assertEqual(got["transcript_source"], "captions")

    def test_detects_skipped_hook_microscope(self):
        d = write_short(self.tmp, "abc", hook_block=HOOK_SKIPPED)
        got = parse_report((d / "report.md").read_text())
        self.assertIs(got["hook_ran"], False)
        self.assertEqual(got["hook_skip_reason"], "video <30s")

    def test_detects_hook_microscope_that_ran(self):
        d = write_short(self.tmp, "abc", hook_block=HOOK_RAN)
        got = parse_report((d / "report.md").read_text())
        self.assertIs(got["hook_ran"], True)
        self.assertIsNone(got["hook_skip_reason"])

    def test_missing_pacing_block_degrades_to_none(self):
        got = parse_report("---\ntitle: Bare\nduration: 00:20\n---\n\n# Bare\n")
        self.assertEqual(got["title"], "Bare")
        self.assertIsNone(got["cuts_per_minute"])
        self.assertIsNone(got["hook_ran"])


class TestLoadEntries(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hookboard-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_merges_coding_json(self):
        write_short(self.tmp, "a", coding={
            "channel": "Chan", "views": 900000, "hook_type": "contrarian"})
        entries = load_entries(self.tmp)
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0]["coded"])
        self.assertEqual(entries[0]["hook_type"], "contrarian")
        self.assertEqual(entries[0]["views"], 900000)

    def test_uncoded_short_still_loads(self):
        write_short(self.tmp, "a")
        entries = load_entries(self.tmp)
        self.assertFalse(entries[0]["coded"])
        self.assertEqual(entries[0]["duration_seconds"], 28)

    def test_directory_without_report_is_skipped(self):
        write_short(self.tmp, "a")
        (self.tmp / "scratch").mkdir()
        self.assertEqual(len(load_entries(self.tmp)), 1)

    def test_invalid_coding_json_fails_loudly(self):
        d = write_short(self.tmp, "a")
        (d / "coding.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            load_entries(self.tmp)

    def test_non_object_coding_json_fails_loudly(self):
        d = write_short(self.tmp, "a")
        (d / "coding.json").write_text("[1, 2]", encoding="utf-8")
        with self.assertRaises(SystemExit):
            load_entries(self.tmp)


class TestSummarise(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hookboard-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _board(self, specs):
        for slug, kwargs in specs:
            write_short(self.tmp, slug, **kwargs)
        entries = load_entries(self.tmp)
        return entries, summarise(entries)

    def test_counts_and_medians(self):
        _, s = self._board([
            ("a", {"duration": "00:20", "cuts": 10.0}),
            ("b", {"duration": "00:30", "cuts": 20.0}),
            ("c", {"duration": "00:40", "cuts": 30.0}),
        ])
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["median_duration_seconds"], 30)
        self.assertEqual(s["median_cuts_per_minute"], 20.0)
        # 20s and 30s are inside the 15-35s band; 40s is not.
        self.assertEqual(s["duration_in_target_band"], 2)

    def test_hook_type_distribution(self):
        _, s = self._board([
            ("a", {"coding": {"hook_type": "number"}}),
            ("b", {"coding": {"hook_type": "number"}}),
            ("c", {"coding": {"hook_type": "question"}}),
        ])
        self.assertEqual(s["hook_types"], {"number": 2, "question": 1})
        self.assertEqual(s["coded"], 3)

    def test_unrecognised_hook_type_is_flagged_not_dropped(self):
        _, s = self._board([("a", {"coding": {"hook_type": "vibes"}})])
        self.assertEqual(s["hook_types"], {"vibes (unrecognised)": 1})

    def test_performance_split_needs_four_coded_views(self):
        _, s = self._board([
            ("a", {"coding": {"views": 100}}),
            ("b", {"coding": {"views": 200}}),
            ("c", {"coding": {"views": 300}}),
        ])
        self.assertFalse(s["performance_split"]["compared"])

    def test_performance_split_compares_top_and_rest(self):
        _, s = self._board([
            ("a", {"cuts": 40.0, "coding": {"views": 4000}}),
            ("b", {"cuts": 38.0, "coding": {"views": 3000}}),
            ("c", {"cuts": 10.0, "coding": {"views": 200}}),
            ("d", {"cuts": 12.0, "coding": {"views": 100}}),
        ])
        split = s["performance_split"]
        self.assertTrue(split["compared"])
        self.assertEqual(split["top_n"], 2)
        self.assertEqual(split["rest_n"], 2)
        self.assertEqual(split["top_median_cuts_per_minute"], 39.0)
        self.assertEqual(split["rest_median_cuts_per_minute"], 11.0)

    def test_counts_skipped_hook_microscopes(self):
        _, s = self._board([
            ("a", {"hook_block": HOOK_SKIPPED}),
            ("b", {"hook_block": HOOK_SKIPPED}),
            ("c", {"hook_block": HOOK_RAN}),
        ])
        self.assertEqual(s["hook_microscope_skipped"], 2)
        self.assertEqual(s["hook_skip_reasons"], {"video <30s": 2})

    def test_empty_metrics_do_not_crash(self):
        s = summarise([])
        self.assertEqual(s["total"], 0)
        self.assertIsNone(s["median_duration_seconds"])


class TestRender(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hookboard-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_markdown_contains_rows_and_sections(self):
        write_short(self.tmp, "a", title="Why This Play Worked", coding={
            "channel": "Chan", "views": 1_800_000, "hook_type": "contrarian",
            "first_words": "Everyone got this wrong.", "material_tier": "C",
            "text_density": "high", "ending": "loop"})
        entries = load_entries(self.tmp)
        md = render_markdown(entries, summarise(entries))
        self.assertIn("Why This Play Worked", md)
        self.assertIn("1.8M", md)
        self.assertIn("contrarian", md)
        self.assertIn("## Patterns", md)
        self.assertIn("Caveat", md)  # hook microscope was skipped

    def test_pipe_in_first_words_is_escaped(self):
        write_short(self.tmp, "a", coding={"first_words": "a | b"})
        entries = load_entries(self.tmp)
        md = render_markdown(entries, summarise(entries))
        self.assertIn("a \\| b", md)

    def test_uncoded_board_renders_with_placeholders(self):
        write_short(self.tmp, "a")
        entries = load_entries(self.tmp)
        md = render_markdown(entries, summarise(entries))
        self.assertIn("|", md)
        self.assertIn("Not enough coded", md)


class TestMain(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hookboard-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_output_file(self):
        write_short(self.tmp, "a", coding={"hook_type": "number"})
        out = self.tmp / "board.md"
        self.assertEqual(main([str(self.tmp), "-o", str(out)]), 0)
        self.assertIn("Hookboard", out.read_text())

    def test_json_mode_is_valid_json(self):
        write_short(self.tmp, "a", coding={"hook_type": "number"})
        out = self.tmp / "board.json"
        self.assertEqual(main([str(self.tmp), "--json", "-o", str(out)]), 0)
        payload = json.loads(out.read_text())
        self.assertEqual(payload["summary"]["total"], 1)

    def test_missing_directory_returns_2(self):
        self.assertEqual(main([str(self.tmp / "nope")]), 2)

    def test_empty_directory_returns_1(self):
        self.assertEqual(main([str(self.tmp)]), 1)


if __name__ == "__main__":
    unittest.main()
