#!/usr/bin/env python3
"""YouTube Data + Analytics client for your own channel.

Gives Claude the numbers it needs to write the *next* script: which videos
held attention, and — the part that actually matters — where they stopped
holding it. `relativeRetentionPerformance` compares each moment against other
YouTube videos of similar length, so it separates "viewers drop here" (normal
on short-form) from "viewers drop here faster than they should" (a finding).

Read-only by design. The scopes below cannot upload, edit or delete anything;
widening them is a deliberate later step, not a config tweak.

Pure stdlib — no `pip install google-api-python-client` needed.

Setup (once):
    1. console.cloud.google.com -> new project
    2. Enable "YouTube Data API v3" and "YouTube Analytics API"
    3. OAuth consent screen -> External -> Testing, add yourself as test user
    4. Credentials -> OAuth client ID -> Desktop app
    5. Put the id/secret in ~/.config/watch/.env:
           YOUTUBE_CLIENT_ID=...apps.googleusercontent.com
           YOUTUBE_CLIENT_SECRET=...
    6. python3 scripts/youtube.py auth

Usage:
    python3 scripts/youtube.py auth
    python3 scripts/youtube.py videos --limit 25 --short-form
    python3 scripts/youtube.py retention <video-id>
    python3 scripts/youtube.py channel --days 90
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import secrets
import ssl
import sys
import time
import urllib.error
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

CONFIG_DIR = Path.home() / ".config" / "watch"
CONFIG_FILE = CONFIG_DIR / ".env"
TOKEN_FILE = CONFIG_DIR / "youtube-token.json"

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
DATA_API = "https://www.googleapis.com/youtube/v3"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"

# Read-only. yt-analytics.readonly carries retention; youtube.readonly lists
# the channel's own uploads. Deliberately NOT youtube.force-ssl, which would
# also grant delete.
SCOPES = (
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
)

# YouTube's audience retention report rejects maxResults above this.
RETENTION_MAX_RESULTS = 200

# Shorts run to three minutes since the 2024 change; used as the --short-form
# cutoff, not as a claim about what YouTube labels a Short.
SHORT_FORM_MAX_SECONDS = 180

# Upper bound on the loopback wait during `auth`. Long enough for a real consent
# click including a password prompt, short enough that a broken redirect fails
# with a message instead of hanging the terminal.
OAUTH_CALLBACK_TIMEOUT = 180.0

USER_AGENT = "watch-skill/1.0 (+claude-code; python-urllib)"

_ISO_DURATION_RE = re.compile(
    r"^P(?:(?P<days>\d+)D)?"
    r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$"
)


# --------------------------------------------------------------------------
# Pure helpers (no I/O — these are what the tests cover)
# --------------------------------------------------------------------------

def parse_iso8601_duration(value: str) -> float | None:
    """'PT1M5S' -> 65.0. None when unparseable."""
    if not value:
        return None
    m = _ISO_DURATION_RE.match(value.strip())
    if not m:
        return None
    parts = m.groupdict()
    if not any(parts.values()):
        return None
    return (int(parts["days"] or 0) * 86400
            + int(parts["hours"] or 0) * 3600
            + int(parts["minutes"] or 0) * 60
            + float(parts["seconds"] or 0))


def rows_to_dicts(payload: dict) -> list[dict]:
    """Analytics returns columnHeaders + rows; zip them into dicts."""
    headers = [h.get("name") for h in payload.get("columnHeaders", [])]
    return [dict(zip(headers, row)) for row in payload.get("rows", []) or []]


def summarise_retention(rows: list[dict], duration_seconds: float | None = None) -> dict:
    """Turn a retention curve into the few numbers worth acting on.

    Returns the ratio still watching at 25/50/75%, the steepest drop between
    two samples, and — when available — the worst `relativeRetentionPerformance`
    point, which is the one that says "worse than comparable videos" rather
    than merely "people left here".
    """
    curve = sorted(
        (r for r in rows if r.get("elapsedVideoTimeRatio") is not None),
        key=lambda r: r["elapsedVideoTimeRatio"],
    )
    if not curve:
        return {"samples": 0}

    def at(target: float) -> float | None:
        best = min(curve, key=lambda r: abs(r["elapsedVideoTimeRatio"] - target))
        return best.get("audienceWatchRatio")

    steepest = None
    for prev, cur in zip(curve, curve[1:]):
        a, b = prev.get("audienceWatchRatio"), cur.get("audienceWatchRatio")
        if a is None or b is None:
            continue
        drop = a - b
        if steepest is None or drop > steepest["drop"]:
            steepest = {
                "drop": round(drop, 4),
                "from_ratio": prev["elapsedVideoTimeRatio"],
                "to_ratio": cur["elapsedVideoTimeRatio"],
            }
    if steepest and duration_seconds:
        steepest["from_seconds"] = round(
            steepest["from_ratio"] * duration_seconds, 1)
        steepest["to_seconds"] = round(
            steepest["to_ratio"] * duration_seconds, 1)

    relative = [r for r in curve
                if isinstance(r.get("relativeRetentionPerformance"), (int, float))]
    worst_relative = None
    if relative:
        worst = min(relative, key=lambda r: r["relativeRetentionPerformance"])
        worst_relative = {
            "value": round(worst["relativeRetentionPerformance"], 4),
            "at_ratio": worst["elapsedVideoTimeRatio"],
            "below_average": worst["relativeRetentionPerformance"] < 0.5,
        }
        if duration_seconds:
            worst_relative["at_seconds"] = round(
                worst["elapsedVideoTimeRatio"] * duration_seconds, 1)

    return {
        "samples": len(curve),
        "watch_ratio_at_25pct": at(0.25),
        "watch_ratio_at_50pct": at(0.50),
        "watch_ratio_at_75pct": at(0.75),
        "steepest_drop": steepest,
        "worst_relative_performance": worst_relative,
    }


def token_is_fresh(token: dict, now: float | None = None) -> bool:
    """True when the cached access token still has >60s of life."""
    expires_at = token.get("expires_at")
    if not token.get("access_token") or not isinstance(expires_at, (int, float)):
        return False
    now = now if now is not None else _dt.datetime.now().timestamp()
    return expires_at - now > 60


# --------------------------------------------------------------------------
# Config + token storage
# --------------------------------------------------------------------------

def _env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value and value.strip():
        return value.strip()
    if not CONFIG_FILE.exists():
        return None
    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, raw = line.partition("=")
        if key.strip() == name:
            return raw.strip().strip('"').strip("'") or None
    return None


def load_client_credentials() -> tuple[str, str]:
    client_id = _env_value("YOUTUBE_CLIENT_ID")
    client_secret = _env_value("YOUTUBE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit(
            "YouTube OAuth credentials missing.\n"
            f"  Add to {CONFIG_FILE}:\n"
            "    YOUTUBE_CLIENT_ID=...apps.googleusercontent.com\n"
            "    YOUTUBE_CLIENT_SECRET=...\n"
            "  Create them at console.cloud.google.com -> Credentials ->\n"
            "  OAuth client ID -> Desktop app. See this file's docstring."
        )
    return client_id, client_secret


def _write_token(token: dict) -> None:
    """Persist the refresh token, readable only by the owner.

    write_text() + chmod() is not good enough: the file is created under the
    process umask (0644 on a default 022) and stays world-readable until the
    chmod lands — and if the chmod fails the credential keeps whatever mode it
    had. We therefore create a fresh file with 0600 from the outset and swap it
    in atomically, so the token is never observable by other local users.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = TOKEN_FILE.with_name(f"{TOKEN_FILE.name}.{os.getpid()}.tmp")
    try:
        fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except OSError as exc:
        # Fail closed — writing the token insecurely is worse than not at all.
        raise SystemExit(
            f"[youtube] cannot create {tmp} with mode 600: {exc}"
        ) from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(token, indent=2))
        os.replace(tmp, TOKEN_FILE)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def _read_token() -> dict:
    if not TOKEN_FILE.exists():
        return {}
    try:
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[youtube] {TOKEN_FILE} is corrupt; re-run `auth`", file=sys.stderr)
        return {}


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def _post_form(url: str, fields: dict) -> dict:
    body = urllib.parse.urlencode(fields).encode()
    request = Request(url, data=body, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    })
    try:
        with urlopen(request, timeout=60, context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"OAuth request failed ({exc.code}): "
            f"{exc.read().decode('utf-8', errors='replace')[:400]}") from exc


def api_get(url: str, params: dict, access_token: str) -> dict:
    full = f"{url}?{urllib.parse.urlencode(params)}"
    request = Request(full, headers={
        "Authorization": f"Bearer {access_token}",
        "User-Agent": USER_AGENT,
    })
    try:
        with urlopen(request, timeout=60, context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        if exc.code == 403:
            raise SystemExit(
                f"YouTube API refused the request (403): {detail}\n"
                "  Common causes: the API is not enabled in the Cloud project, "
                "or the token lacks the needed scope (re-run `auth`)."
            ) from exc
        raise SystemExit(f"YouTube API error ({exc.code}): {detail}") from exc


# --------------------------------------------------------------------------
# OAuth (installed-app loopback flow)
# --------------------------------------------------------------------------

class _CallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    state: str | None = None
    error: str | None = None

    @classmethod
    def reset(cls) -> None:
        cls.code = cls.state = cls.error = None

    def do_GET(self):  # noqa: N802 (stdlib naming)
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = (query.get("code") or [None])[0]
        state = (query.get("state") or [None])[0]
        error = (query.get("error") or [None])[0]
        # Browsers also request /favicon.ico on this port, and a user may reload
        # the tab. Only record requests that actually carry OAuth parameters —
        # otherwise a stray GET would wipe a callback we already captured.
        if code or error:
            _CallbackHandler.code = code
            _CallbackHandler.state = state
            _CallbackHandler.error = error
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><p>Waiting for the OAuth callback.</p></body></html>")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        message = ("Authorisation failed — check the terminal."
                   if _CallbackHandler.error else
                   "Authorised. You can close this tab and return to the terminal.")
        self.wfile.write(f"<html><body><p>{message}</p></body></html>".encode())

    def log_message(self, *args):  # silence the default stderr access log
        pass


def _wait_for_callback(server: HTTPServer, expected_state: str,
                       timeout: float = OAUTH_CALLBACK_TIMEOUT) -> None:
    """Serve loopback requests until the OAuth callback lands or time runs out.

    A bare handle_request() blocks forever when the browser never reaches the
    listener, the user closes the consent tab, or Google simply never redirects
    — the first-run flow then hangs with no way out but killing the process.
    """
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SystemExit(
                f"Timed out after {timeout:.0f}s waiting for the OAuth callback.\n"
                "  Re-run `auth`. If the browser cannot reach 127.0.0.1, open the\n"
                "  printed URL manually in a browser on this machine."
            )
        server.timeout = min(1.0, remaining)
        server.handle_request()          # returns on timeout too, thanks to server.timeout
        if _CallbackHandler.error:
            raise SystemExit(f"Authorisation denied: {_CallbackHandler.error}")
        if _CallbackHandler.code:
            if _CallbackHandler.state != expected_state:
                raise SystemExit("OAuth state mismatch — aborting.")
            return
        # anything else was a stray request; keep waiting until the deadline


def run_auth_flow() -> dict:
    client_id, client_secret = load_client_credentials()
    state = secrets.token_urlsafe(24)
    _CallbackHandler.reset()   # class state survives across runs in one process

    server = HTTPServer(("127.0.0.1", 0), _CallbackHandler)
    redirect_uri = f"http://127.0.0.1:{server.server_port}"

    auth_url = f"{AUTH_ENDPOINT}?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",   # we need a refresh token
        "prompt": "consent",        # force one, even on re-auth
        "state": state,
    })

    print("[youtube] opening browser for consent…", file=sys.stderr)
    print(f"[youtube] if nothing opens, visit:\n{auth_url}\n", file=sys.stderr)
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    try:
        _wait_for_callback(server, state)
    finally:
        server.server_close()

    payload = _post_form(TOKEN_ENDPOINT, {
        "code": _CallbackHandler.code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })
    if "refresh_token" not in payload:
        raise SystemExit(
            "Google returned no refresh token. Revoke the app at "
            "myaccount.google.com/permissions and run `auth` again.")

    token = {
        "access_token": payload["access_token"],
        "refresh_token": payload["refresh_token"],
        "expires_at": _dt.datetime.now().timestamp() + payload.get("expires_in", 3600),
    }
    _write_token(token)
    return token


def ensure_access_token() -> str:
    token = _read_token()
    if not token.get("refresh_token"):
        raise SystemExit("Not authorised yet. Run: python3 scripts/youtube.py auth")
    if token_is_fresh(token):
        return token["access_token"]

    client_id, client_secret = load_client_credentials()
    payload = _post_form(TOKEN_ENDPOINT, {
        "refresh_token": token["refresh_token"],
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    })
    token["access_token"] = payload["access_token"]
    token["expires_at"] = (_dt.datetime.now().timestamp()
                           + payload.get("expires_in", 3600))
    _write_token(token)
    return token["access_token"]


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def _today() -> _dt.date:
    return _dt.date.today()


def cmd_auth(_args) -> int:
    run_auth_flow()
    print(f"[youtube] authorised; token cached at {TOKEN_FILE}")
    print("[youtube] read-only scopes: " + ", ".join(
        s.rsplit("/", 1)[-1] for s in SCOPES))
    return 0


def cmd_videos(args) -> int:
    access = ensure_access_token()
    channels = api_get(f"{DATA_API}/channels",
                       {"part": "contentDetails,snippet", "mine": "true"}, access)
    items = channels.get("items") or []
    if not items:
        raise SystemExit("No channel found for this account.")
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # --limit counts videos we RETURN, not uploads we inspect. With
    # --short-form on a mixed-format channel the old code stopped after
    # args.limit uploads and only then dropped the long ones, so the caller
    # silently got fewer rows than asked for — sometimes none — while
    # qualifying shorts sat one page further down.
    rows: list[dict] = []
    page_token = None
    while len(rows) < args.limit:
        params = {"part": "contentDetails", "playlistId": uploads,
                  "maxResults": 50 if args.short_form
                  else min(50, args.limit - len(rows))}
        if page_token:
            params["pageToken"] = page_token
        page = api_get(f"{DATA_API}/playlistItems", params, access)
        batch = [i["contentDetails"]["videoId"] for i in page.get("items", [])]
        page_token = page.get("nextPageToken")

        for chunk_start in range(0, len(batch), 50):
            chunk = batch[chunk_start:chunk_start + 50]
            if not chunk:
                continue
            detail = api_get(f"{DATA_API}/videos",
                             {"part": "snippet,statistics,contentDetails",
                              "id": ",".join(chunk)}, access)
            for v in detail.get("items", []):
                seconds = parse_iso8601_duration(
                    v.get("contentDetails", {}).get("duration", ""))
                if args.short_form and (seconds is None
                                        or seconds > SHORT_FORM_MAX_SECONDS):
                    continue
                stats = v.get("statistics", {})
                rows.append({
                    "video_id": v["id"],
                    "title": v["snippet"]["title"],
                    "published_at": v["snippet"]["publishedAt"],
                    "duration_seconds": seconds,
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                })

        if not page_token:
            break   # uploads playlist exhausted

    rows.sort(key=lambda r: r["views"], reverse=True)
    rows = rows[:args.limit]
    print(json.dumps(rows, indent=2))
    return 0


def cmd_retention(args) -> int:
    access = ensure_access_token()
    end = _today()
    start = end - _dt.timedelta(days=args.days)
    payload = api_get(ANALYTICS_API, {
        "ids": "channel==MINE",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "metrics": "audienceWatchRatio,relativeRetentionPerformance",
        "dimensions": "elapsedVideoTimeRatio",
        # This report takes exactly one video id — no comma-separated list.
        "filters": f"video=={args.video_id}",
        "maxResults": RETENTION_MAX_RESULTS,
    }, access)

    duration = None
    detail = api_get(f"{DATA_API}/videos",
                     {"part": "contentDetails,snippet", "id": args.video_id}, access)
    title = None
    if detail.get("items"):
        item = detail["items"][0]
        title = item["snippet"]["title"]
        duration = parse_iso8601_duration(
            item.get("contentDetails", {}).get("duration", ""))

    rows = rows_to_dicts(payload)
    print(json.dumps({
        "video_id": args.video_id,
        "title": title,
        "duration_seconds": duration,
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "summary": summarise_retention(rows, duration),
        "curve": rows,
    }, indent=2))
    return 0


def cmd_channel(args) -> int:
    access = ensure_access_token()
    end = _today()
    start = end - _dt.timedelta(days=args.days)
    payload = api_get(ANALYTICS_API, {
        "ids": "channel==MINE",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "metrics": ("views,estimatedMinutesWatched,averageViewDuration,"
                    "averageViewPercentage,subscribersGained,subscribersLost"),
        "dimensions": "day",
        "sort": "day",
    }, access)
    print(json.dumps({
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "days": rows_to_dicts(payload),
    }, indent=2))
    return 0


def cmd_traffic(args) -> int:
    access = ensure_access_token()
    end = _today()
    start = end - _dt.timedelta(days=args.days)
    params = {
        "ids": "channel==MINE",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "insightTrafficSourceType",
        "sort": "-views",
    }
    if args.video_id:
        params["filters"] = f"video=={args.video_id}"
    print(json.dumps(rows_to_dicts(api_get(ANALYTICS_API, params, access)), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only YouTube Data + Analytics client for your own channel.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("auth", help="run the OAuth consent flow").set_defaults(
        func=cmd_auth)

    p_videos = sub.add_parser("videos", help="list your uploads with basic stats")
    p_videos.add_argument("--limit", type=int, default=50)
    p_videos.add_argument("--short-form", action="store_true",
                          help=f"only videos <= {SHORT_FORM_MAX_SECONDS}s")
    p_videos.set_defaults(func=cmd_videos)

    p_ret = sub.add_parser("retention", help="audience retention curve for one video")
    p_ret.add_argument("video_id")
    p_ret.add_argument("--days", type=int, default=90)
    p_ret.set_defaults(func=cmd_retention)

    p_chan = sub.add_parser("channel", help="day-by-day channel metrics")
    p_chan.add_argument("--days", type=int, default=90)
    p_chan.set_defaults(func=cmd_channel)

    p_traffic = sub.add_parser("traffic", help="traffic sources")
    p_traffic.add_argument("--days", type=int, default=90)
    p_traffic.add_argument("--video-id", default=None)
    p_traffic.set_defaults(func=cmd_traffic)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
