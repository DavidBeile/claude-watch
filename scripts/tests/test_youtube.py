"""Tests for the YouTube analytics client's pure logic.

Scope note: the HTTP layer was verified manually against the live Google
endpoints — request construction, form encoding, and the 401/403 error paths
all behave. What remains unverified, and cannot be covered here, is the OAuth
consent flow (needs a browser and real credentials) and parsing of real
response payloads (needs a valid token). Everything testable without a network
lives below.
"""
import argparse
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

import youtube  # noqa: E402
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


class TestWriteTokenPermissions(unittest.TestCase):
    """Regression: the refresh token must never exist world-readable.

    The old code wrote via write_text() (created under the process umask) and
    only then chmod'ed to 600, leaving a window in which any local user could
    read it — and no protection at all if the chmod failed.
    """

    def _run_in_tmp(self, token):
        tmpdir = Path(tempfile.mkdtemp())
        target = tmpdir / "youtube-token.json"
        with mock.patch.object(youtube, "CONFIG_DIR", tmpdir), \
             mock.patch.object(youtube, "TOKEN_FILE", target):
            youtube._write_token(token)
        return target

    def test_token_file_is_owner_only(self):
        old_umask = os.umask(0o022)          # the permissive default
        try:
            target = self._run_in_tmp({"refresh_token": "secret"})
        finally:
            os.umask(old_umask)
        mode = stat.S_IMODE(target.stat().st_mode)
        self.assertEqual(mode, 0o600, f"token file is {oct(mode)}, want 0o600")

    def test_token_roundtrips(self):
        target = self._run_in_tmp({"refresh_token": "secret", "expires_at": 1})
        self.assertEqual(json.loads(target.read_text())["refresh_token"], "secret")

    def test_rewrite_tightens_a_loose_existing_file(self):
        tmpdir = Path(tempfile.mkdtemp())
        target = tmpdir / "youtube-token.json"
        target.write_text("{}", encoding="utf-8")
        target.chmod(0o644)                  # e.g. written by an older version
        with mock.patch.object(youtube, "CONFIG_DIR", tmpdir), \
             mock.patch.object(youtube, "TOKEN_FILE", target):
            youtube._write_token({"refresh_token": "secret"})
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_creates_the_file_with_0600_from_the_outset(self):
        """The real defect was the transient window, not the final mode.

        Checking st_mode afterwards passes even on the broken version, because
        its chmod eventually lands. What matters is that the file is *created*
        with 0600 — so assert on the creation mode itself.
        """
        tmpdir = Path(tempfile.mkdtemp())
        target = tmpdir / "youtube-token.json"
        seen = []
        real_open = os.open

        def spy(path, flags, mode=0o777):
            seen.append((flags, mode))
            return real_open(path, flags, mode)

        with mock.patch.object(youtube, "CONFIG_DIR", tmpdir), \
             mock.patch.object(youtube, "TOKEN_FILE", target), \
             mock.patch.object(youtube.os, "open", spy):
            youtube._write_token({"refresh_token": "secret"})

        self.assertTrue(seen, "token file was not created through os.open with an "
                              "explicit mode — it is exposed under the umask first")
        flags, mode = seen[-1]
        self.assertEqual(stat.S_IMODE(mode), 0o600)
        self.assertTrue(flags & os.O_EXCL, "must not write into a pre-existing file")

    def test_fails_closed_when_secure_create_is_impossible(self):
        tmpdir = Path(tempfile.mkdtemp())
        target = tmpdir / "youtube-token.json"
        with mock.patch.object(youtube, "CONFIG_DIR", tmpdir), \
             mock.patch.object(youtube, "TOKEN_FILE", target), \
             mock.patch.object(youtube.os, "open", side_effect=OSError("nope")):
            with self.assertRaises(SystemExit):
                youtube._write_token({"refresh_token": "secret"})
        self.assertFalse(target.exists(), "no token must be left behind")


class _FakeServer:
    """Stands in for HTTPServer: each handle_request() replays one scripted hit."""

    def __init__(self, script):
        self.script = list(script)
        self.timeout = None
        self.timeouts_seen = []

    def handle_request(self):
        self.timeouts_seen.append(self.timeout)
        if self.script:
            self.script.pop(0)()


class TestWaitForCallback(unittest.TestCase):
    """Regression: the loopback wait must be bounded and must ignore noise."""

    def setUp(self):
        youtube._CallbackHandler.reset()
        self.addCleanup(youtube._CallbackHandler.reset)

    def _hit(self, **kw):
        def apply():
            for key, value in kw.items():
                setattr(youtube._CallbackHandler, key, value)
        return apply

    def test_returns_on_matching_state(self):
        server = _FakeServer([self._hit(code="abc", state="s1")])
        youtube._wait_for_callback(server, "s1", timeout=5)

    def test_ignores_unrelated_requests_then_succeeds(self):
        # A browser fetching /favicon.ico must not end the wait.
        server = _FakeServer([lambda: None, lambda: None,
                              self._hit(code="abc", state="s1")])
        youtube._wait_for_callback(server, "s1", timeout=5)
        self.assertEqual(len(server.timeouts_seen), 3)

    def test_times_out_instead_of_hanging(self):
        server = _FakeServer([])          # nothing ever arrives
        with self.assertRaises(SystemExit) as ctx:
            youtube._wait_for_callback(server, "s1", timeout=0.05)
        self.assertIn("Timed out", str(ctx.exception))

    def test_user_denial_aborts(self):
        server = _FakeServer([self._hit(error="access_denied")])
        with self.assertRaises(SystemExit) as ctx:
            youtube._wait_for_callback(server, "s1", timeout=5)
        self.assertIn("denied", str(ctx.exception))

    def test_state_mismatch_aborts(self):
        server = _FakeServer([self._hit(code="abc", state="wrong")])
        with self.assertRaises(SystemExit) as ctx:
            youtube._wait_for_callback(server, "s1", timeout=5)
        self.assertIn("state mismatch", str(ctx.exception))

    def test_never_blocks_past_the_deadline(self):
        server = _FakeServer([])
        with self.assertRaises(SystemExit):
            youtube._wait_for_callback(server, "s1", timeout=0.05)
        self.assertTrue(all(t <= 1.0 for t in server.timeouts_seen),
                        "handle_request() must never be left unbounded")


class TestVideosShortFormPagination(unittest.TestCase):
    """Regression: --limit counts videos RETURNED, not uploads inspected.

    Channel shape below: every page holds one short and four long uploads, so
    the old 'take args.limit uploads, then filter' order returned 1 row for
    --limit 3 while qualifying shorts sat on the next page.
    """

    PAGES = 4
    PER_PAGE = 5

    def _api_get(self, url, params, access):
        if url.endswith("/channels"):
            return {"items": [{"contentDetails":
                    {"relatedPlaylists": {"uploads": "UU_fake"}}}]}
        if url.endswith("/playlistItems"):
            page = int(params.get("pageToken") or 0)
            items = [{"contentDetails": {"videoId": f"v{page}_{i}"}}
                     for i in range(self.PER_PAGE)]
            out = {"items": items}
            if page + 1 < self.PAGES:
                out["nextPageToken"] = str(page + 1)
            return out
        if url.endswith("/videos"):
            items = []
            for n, vid in enumerate(params["id"].split(",")):
                short = vid.endswith("_0")        # one short per page
                items.append({
                    "id": vid,
                    "snippet": {"title": vid, "publishedAt": "2026-01-01T00:00:00Z"},
                    "contentDetails": {"duration": "PT30S" if short else "PT12M"},
                    "statistics": {"viewCount": str(100 - n)},
                })
            return {"items": items}
        raise AssertionError(f"unexpected call: {url}")

    def _run(self, limit, short_form):
        args = argparse.Namespace(limit=limit, short_form=short_form)
        printed = []
        with mock.patch.object(youtube, "ensure_access_token", return_value="t"), \
             mock.patch.object(youtube, "api_get", side_effect=self._api_get), \
             mock.patch("builtins.print", lambda *a, **k: printed.append(a[0])):
            youtube.cmd_videos(args)
        return json.loads(printed[-1])

    def test_short_form_keeps_paginating_until_limit_is_met(self):
        rows = self._run(limit=3, short_form=True)
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r["duration_seconds"] <= youtube.SHORT_FORM_MAX_SECONDS
                            for r in rows))

    def test_stops_when_playlist_is_exhausted(self):
        # Only 4 shorts exist in total; asking for 10 must not loop forever.
        rows = self._run(limit=10, short_form=True)
        self.assertEqual(len(rows), self.PAGES)

    def test_never_returns_more_than_limit(self):
        rows = self._run(limit=2, short_form=True)
        self.assertEqual(len(rows), 2)

    def test_unfiltered_mode_is_unchanged(self):
        rows = self._run(limit=3, short_form=False)
        self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
