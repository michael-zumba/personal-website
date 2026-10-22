#!/usr/bin/env python3
"""Collect and classify journal AI guidance from dated author pages.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Identify whether AI guidance is visible on selected journal author pages.
"""

from __future__ import annotations

import csv
import gzip
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

from bs4 import BeautifulSoup


PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
SNAPSHOTS = PROJECT / "evidence" / "snapshots" / "policies"
ACCESS_DATE = date.today().isoformat()
USER_AGENT = (
    "accounting-finance-research-ai-era/1.0 "
    "(mailto:research@zhangyuqian.com)"
)

JOURNALS = [
    (
        "The Accounting Review",
        "Accounting",
        "https://aaahq.org/Research/Journals/The-Accounting-Review/Guide-for-Authors",
    ),
    (
        "Journal of Accounting Research",
        "Accounting",
        "https://onlinelibrary.wiley.com/page/journal/1475679x/homepage/ForAuthors.html",
    ),
    (
        "Journal of Accounting and Economics",
        "Accounting",
        "https://www.elsevier.com/journals/journal-of-accounting-and-economics/0165-4101/guide-for-authors",
    ),
    (
        "Contemporary Accounting Research",
        "Accounting",
        "https://onlinelibrary.wiley.com/page/journal/19113846/homepage/ForAuthors.html",
    ),
    (
        "Review of Accounting Studies",
        "Accounting",
        "https://link.springer.com/journal/11142/submission-guidelines",
    ),
    (
        "Accounting, Organizations and Society",
        "Accounting",
        "https://www.elsevier.com/journals/accounting-organizations-and-society/0361-3682/guide-for-authors",
    ),
    (
        "The Journal of Finance",
        "Finance",
        "https://onlinelibrary.wiley.com/page/journal/15406261/homepage/ForAuthors.html",
    ),
    (
        "Journal of Financial Economics",
        "Finance",
        "https://www.elsevier.com/journals/journal-of-financial-economics/0304-405x/guide-for-authors",
    ),
    (
        "The Review of Financial Studies",
        "Finance",
        "https://academic.oup.com/rfs/pages/General_Instructions",
    ),
    (
        "Journal of Financial and Quantitative Analysis",
        "Finance",
        "https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/information/instructions-contributors",
    ),
    (
        "Review of Finance",
        "Finance",
        "https://academic.oup.com/rof/pages/General_Instructions",
    ),
]

PERIODS = (
    ("baseline", "20210101", "20220630"),
    ("latest", "20230101", "20261022"),
)
AI_TERMS = (
    "generative ai",
    "generative artificial intelligence",
    "artificial intelligence",
    "ai-assisted",
    "large language model",
    "large language models",
    "llm",
    "chatgpt",
)
POLICY_TERMS = (
    "disclose",
    "disclosure",
    "must not",
    "cannot",
    "not permitted",
    "authorship",
    "confidential",
    "accountable",
    "responsibility",
    "responsible",
)


def _get(url: str, timeout: int = 60) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = response.read()
                if data[:2] == b"\x1f\x8b":
                    data = gzip.decompress(data)
                return data
        except urllib.error.HTTPError as error:
            if attempt == 3:
                raise
            if error.code not in {429, 500, 502, 503, 504}:
                raise
            time.sleep(2 ** attempt)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Could not fetch {url}")


def _timestamp_for_period(url: str, start: str, end: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "url": url,
            "from": start,
            "to": end,
            "output": "json",
            "filter": ["statuscode:200", "mimetype:text/html"],
            "collapse": "digest",
        },
        doseq=True,
    )
    payload = json.loads(
        _get(f"https://web.archive.org/cdx/search/cdx?{params}")
    )
    rows = payload[1:] if payload else []
    if not rows:
        return None
    return max(row[1] for row in rows)


def _classify(html: str) -> tuple[dict[str, object], str]:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()
    text = " ".join(soup.get_text(" ", strip=True).split())
    folded = text.casefold()
    headings = " ".join(
        heading.get_text(" ", strip=True).casefold()
        for heading in soup.find_all(["h1", "h2", "h3", "h4"])
    )
    ai_index = next(
        (folded.find(term) for term in AI_TERMS if folded.find(term) >= 0),
        -1,
    )
    generic_ai = ai_index >= 0
    generative_ai = any(
        term in folded for term in AI_TERMS[:2]
    )
    policy_hits = sum(term in folded for term in POLICY_TERMS)
    section_heading = any(term in headings for term in AI_TERMS)
    if generic_ai and policy_hits >= 1:
        status = "Explicit AI guidance"
    elif generic_ai:
        status = "AI mentioned only"
    else:
        status = "No visible AI guidance"
    context = text[max(0, ai_index - 250) : ai_index + 1200] if generic_ai else ""
    record = {
        "generic_ai_visible": int(generic_ai),
        "generative_ai_visible": int(generative_ai),
        "section_heading_ai": int(section_heading),
        "policy_term_hits": policy_hits,
        "policy_status": status,
        "context": context,
    }
    return record, text


def collect() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for journal, field, url in JOURNALS:
        print(f"Collecting {journal}", flush=True)
        safe_name = re.sub(r"[^a-z0-9]+", "-", journal.casefold()).strip("-")
        for period, start, end in PERIODS:
            existing = sorted(SNAPSHOTS.glob(f"{safe_name}-*.html"))
            existing = [
                path
                for path in existing
                if start <= path.stem[-14:] <= end
            ]
            if existing:
                snapshot_path = existing[-1]
                timestamp = snapshot_path.stem[-14:]
            else:
                try:
                    timestamp = _timestamp_for_period(url, start, end)
                except Exception as error:
                    print(f"  {period}: CDX skipped: {error}", flush=True)
                    time.sleep(2)
                    continue
                snapshot_path = SNAPSHOTS / f"{safe_name}-{timestamp}.html"
            if timestamp is None:
                continue
            archive_url = f"https://web.archive.org/web/{timestamp}id_/{url}"
            print(f"  {period}: {timestamp}", flush=True)
            if snapshot_path.exists():
                html = snapshot_path.read_bytes()
            else:
                try:
                    html = _get(archive_url)
                except Exception as error:
                    print(f"    skipped: {error}", flush=True)
                    time.sleep(2)
                    continue
                snapshot_path.write_bytes(html)
            classification, visible_text = _classify(
                html.decode("utf-8", errors="replace")
            )
            if len(visible_text) < 2000:
                print("    skipped: page content did not load", flush=True)
                continue
            rows.append(
                {
                    "source_id": (
                        "S_POLICY_"
                        + safe_name.upper().replace("-", "_")
                        + "_"
                        + timestamp[:8]
                    ),
                    "journal": journal,
                    "field": field,
                    "period": period,
                    "window_start": start,
                    "window_end": end,
                    "snapshot_timestamp": timestamp,
                    "snapshot_url": archive_url,
                    "canonical_url": url,
                    **classification,
                    "snapshot_path": str(
                        snapshot_path.relative_to(PROJECT)
                    ),
                    "accessed_at": ACCESS_DATE,
                }
            )
            time.sleep(0.4)
        if rows:
            path = DATA / "ai_policy_status.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)

    path = DATA / "ai_policy_status.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} dated policy observations")


if __name__ == "__main__":
    collect()
