"""Tests for article report.md emission."""
import datetime as dt
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from article import write_article_report  # noqa: E402

SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog.\n\nSecond paragraph here."


class TestArticleReport(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="watch-article-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, **overrides):
        kwargs = dict(
            out_path=self.tmp / "report.md",
            source="https://example.com/post",
            title="A Test Article",
            intent="studying pricing tactics",
            text=SAMPLE_TEXT,
            author="Jane Doe",
            site="example.com",
            published="2026-01-15",
            headings=[
                {"level": 1, "text": "A Test Article"},
                {"level": 2, "text": "Background"},
                {"level": 3, "text": "Prior work"},
            ],
            links=[{"href": "https://example.com/pricing", "text": "Pricing"}],
            fetch_mode="http",
            http_status=200,
            fetched_at=dt.datetime(2026, 9, 15, 12, 0, tzinfo=dt.timezone.utc),
        )
        kwargs.update(overrides)
        return write_article_report(**kwargs).read_text()

    def test_writes_all_required_sections(self):
        body = self._write()
        for section in (
            "## TL;DR",
            "## Key points",
            "## Notable quotes",
            "## Structure",
            "## Entities mentioned",
            "## Concepts surfaced",
            "## Full text",
            "## Links",
        ):
            self.assertIn(section, body)

    def test_frontmatter_carries_provenance(self):
        body = self._write()
        head = body.split("---")[1]
        self.assertIn("source: https://example.com/post", head)
        self.assertIn("author: Jane Doe", head)
        self.assertIn("http_status: 200", head)
        self.assertIn("fetch_mode: http", head)
        self.assertIn("truncated: false", head)
        self.assertIn("intent: studying pricing tactics", head)

    def test_word_count_and_reading_time(self):
        body = self._write()
        # SAMPLE_TEXT has 12 words; under one minute rounds up to 1.
        self.assertIn("word_count: 12", body)
        self.assertIn("reading_time: 1 min", body)
        self.assertIn("- Words: 12", body)

    def test_reading_time_scales_with_length(self):
        body = self._write(text=" ".join(["word"] * 1000))
        self.assertIn("word_count: 1000", body)
        self.assertIn("reading_time: 5 min", body)

    def test_outline_indents_by_heading_level(self):
        body = self._write()
        self.assertIn("- A Test Article", body)
        self.assertIn("  - Background", body)
        self.assertIn("    - Prior work", body)

    def test_pending_markers_left_for_claude(self):
        body = self._write()
        # Narrative sections must stay unfilled so Claude has a job list.
        self.assertGreaterEqual(body.count("<!-- pending Claude fill:"), 7)
        self.assertIn("studying pricing tactics", body)

    def test_empty_headings_explains_itself(self):
        body = self._write(headings=[])
        self.assertIn("_No headings", body)
        self.assertIn("- Headings: 0", body)

    def test_blank_headings_are_skipped(self):
        body = self._write(headings=[{"level": 2, "text": "   "}])
        self.assertIn("_No headings", body)

    def test_empty_text_is_stated_not_faked(self):
        body = self._write(text="")
        self.assertIn("_No text extracted._", body)
        self.assertIn("word_count: 0", body)
        self.assertIn("reading_time: 0 min", body)

    def test_truncated_fetch_raises_a_banner(self):
        body = self._write(truncated=True)
        self.assertIn("truncated: true", body)
        self.assertIn("Incomplete fetch", body)

    def test_title_with_colon_is_quoted(self):
        body = self._write(title="Scrapling: a field guide")
        self.assertIn('title: "Scrapling: a field guide"', body)

    def test_whitespace_only_metadata_does_not_crash(self):
        # `not value` doesn't catch "   ", so the quoting rule has to survive
        # a value that flattens to the empty string.
        body = self._write(author="   ", title="Fine")
        self.assertIn('author: ""', body)

    def test_missing_metadata_degrades_visibly(self):
        body = self._write(author=None, published=None, site=None)
        self.assertIn("author: (unknown)", body)
        self.assertIn("published: (unknown)", body)

    def test_links_are_rendered(self):
        body = self._write()
        self.assertIn("[Pricing](https://example.com/pricing)", body)
        self.assertIn("- Outbound links: 1", body)

    def test_link_without_text_falls_back_to_href(self):
        body = self._write(links=[{"href": "https://example.com/x", "text": ""}])
        self.assertIn("[https://example.com/x](https://example.com/x)", body)

    def test_link_without_href_is_dropped(self):
        body = self._write(links=[{"href": "", "text": "dead"}])
        self.assertIn("_Total: 1._", body)
        self.assertNotIn("dead", body.split("## Links")[1])


if __name__ == "__main__":
    unittest.main()
