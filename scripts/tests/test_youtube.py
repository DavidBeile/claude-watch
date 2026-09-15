"""Tests for the YouTube analytics client's pure logic.

The OAuth and HTTP paths need a real Google project and are exercised by
`youtube.py auth` on a real machine; everything testable without a network
lives here.
"""
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from youtube import (  # noqa: E402
    parse_iso8601_duration, rows_to_dicts, summarise_retention, token_is_fresh,
)


class TestParseDuration(unittest.TestCase):

    def test_common_shapes(self):
        self.assertEqual(parse_iso8601_duration("PT28S"), 28.0)
        self.assertEqual(parse_iso8601_duration("PT1M5S"), 65.0)
        self.assertEqual(parse_iso8601_duration("PT1H2M3S"), 3723.0)
        self.assertEqual(parse_iso8601_duration("PT12M"), 720.0)

    def test_fractional_seconds(self):
        self.assertEqual(parse_iso8601_duration("PT1M5.5S"), 65.5)

    def test_days(self):
        self.assertEqual(parse_iso8601_duration("P1DT1H"), 90000.0)

    def test_rejects_garbage(self):
        for value in ("", "banana", "1M5S", "P"):
            with self.subTest(value=value):
                self.assertIsNone(parse_iso8601_duration(value))


class TestRowsToDicts(unittest.TestCase):

    def test_zips_headers_and_rows(self):
        payload = {
            "columnHeaders": [{"name": "day"}, {"name": "views"}],
            "rows": [["2026-09-01", 120], ["2026-09-02", 340]],
        }
        self.assertEqual(rows_to_dicts(payload),
                         [{"day": "2026-09-01", "views": 120},
                          {"day": "2026-09-02", "views": 340}])

    def test_empty_payloads(self):
        self.assertEqual(rows_to_dicts({}), [])
        self.assertEqual(rows_to_dicts({"columnHeaders": [{"name": "day"}],
                                        "rows": None}), [])


def curve(points):
    """points: [(elapsed_ratio, watch_ratio, relative_or_None), ...]"""
    return [{"elapsedVideoTimeRatio": e,
             "audienceWatchRatio": w,
             "relativeRetentionPerformance": r}
            for e, w, r in points]


class TestSummariseRetention(unittest.TestCase):

    def test_empty_curve(self):
        self.assertEqual(summarise_retention([]), {"samples": 0})

    def test_reports_checkpoints(self):
        s = summarise_retention(curve([
            (0.0, 1.0, 0.6), (0.25, 0.8, 0.6),
            (0.5, 0.6, 0.5), (0.75, 0.4, 0.4), (1.0, 0.3, 0.4),
        ]))
        self.assertEqual(s["samples"], 5)
        self.assertEqual(s["watch_ratio_at_25pct"], 0.8)
        self.assertEqual(s["watch_ratio_at_50pct"], 0.6)
        self.assertEqual(s["watch_ratio_at_75pct"], 0.4)

    def test_finds_steepest_drop(self):
        s = summarise_retention(curve([
            (0.0, 1.0, 0.6), (0.1, 0.95, 0.6),
            (0.2, 0.5, 0.3),   # the cliff
            (0.3, 0.48, 0.3),
        ]))
        drop = s["steepest_drop"]
        self.assertAlmostEqual(drop["drop"], 0.45)
        self.assertEqual(drop["from_ratio"], 0.1)
        self.assertEqual(drop["to_ratio"], 0.2)

    def test_steepest_drop_maps_to_seconds(self):
        s = summarise_retention(curve([
            (0.0, 1.0, 0.6), (0.1, 0.9, 0.6), (0.2, 0.4, 0.3),
        ]), duration_seconds=30.0)
        self.assertEqual(s["steepest_drop"]["from_seconds"], 3.0)
        self.assertEqual(s["steepest_drop"]["to_seconds"], 6.0)

    def test_flags_below_average_relative_performance(self):
        s = summarise_retention(curve([
            (0.0, 1.0, 0.7), (0.5, 0.6, 0.31), (1.0, 0.4, 0.55),
        ]), duration_seconds=40.0)
        worst = s["worst_relative_performance"]
        self.assertEqual(worst["value"], 0.31)
        self.assertEqual(worst["at_ratio"], 0.5)
        self.assertEqual(worst["at_seconds"], 20.0)
        self.assertTrue(worst["below_average"])

    def test_above_average_is_not_flagged(self):
        s = summarise_retention(curve([
            (0.0, 1.0, 0.8), (0.5, 0.7, 0.62), (1.0, 0.5, 0.7),
        ]))
        self.assertFalse(s["worst_relative_performance"]["below_average"])

    def test_handles_missing_relative_metric(self):
        rows = [{"elapsedVideoTimeRatio": e, "audienceWatchRatio": w}
                for e, w in ((0.0, 1.0), (0.5, 0.6))]
        s = summarise_retention(rows)
        self.assertIsNone(s["worst_relative_performance"])
        self.assertIsNotNone(s["steepest_drop"])

    def test_unsorted_input_is_sorted(self):
        s = summarise_retention(curve([
            (1.0, 0.3, 0.4), (0.0, 1.0, 0.6), (0.5, 0.6, 0.5),
        ]))
        self.assertEqual(s["watch_ratio_at_50pct"], 0.6)

    def test_rows_without_elapsed_ratio_are_dropped(self):
        rows = curve([(0.0, 1.0, 0.6)]) + [{"audienceWatchRatio": 0.2}]
        self.assertEqual(summarise_retention(rows)["samples"], 1)

    def test_monotonic_curve_has_no_negative_steepest(self):
        s = summarise_retention(curve([(0.0, 1.0, 0.6), (0.5, 1.0, 0.6)]))
        self.assertEqual(s["steepest_drop"]["drop"], 0.0)


class TestTokenFreshness(unittest.TestCase):

    def test_fresh_token(self):
        self.assertTrue(token_is_fresh(
            {"access_token": "x", "expires_at": 1000.0}, now=500.0))

    def test_expired_token(self):
        self.assertFalse(token_is_fresh(
            {"access_token": "x", "expires_at": 1000.0}, now=1001.0))

    def test_token_inside_refresh_margin_is_stale(self):
        # 30s of life left — refresh rather than risk a mid-call expiry.
        self.assertFalse(token_is_fresh(
            {"access_token": "x", "expires_at": 1000.0}, now=970.0))

    def test_missing_fields(self):
        self.assertFalse(token_is_fresh({}))
        self.assertFalse(token_is_fresh({"access_token": "x"}))
        self.assertFalse(token_is_fresh({"expires_at": 9e9}))


if __name__ == "__main__":
    unittest.main()
