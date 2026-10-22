#!/usr/bin/env python3
"""Collect Crossref-indexed journal articles for the approved journal sample.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Create auditable article and journal-year CSVs for the research brief.
"""

from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
ACCESS_DATE = "2026-10-22"
NONRESEARCH_TITLE = re.compile(
    r"^(?:"
    r"editor(?:['\u2019])?s?\s+note\b|editorial\b|"
    r"(?:annual\s+)?editor\s+report\b|"
    r"annual\s+report\s+(?:of|and)\b|report\s+of\s+the\b|"
    r"(?:retraction|retractions|retracted)\b|"
    r"errat(?:um|a)\b|corrigend(?:um|a)\b|correction\b|"
    r"expression\s+of\s+concern\b|addendum\b|"
    r"publisher(?:['\u2019])?s?\s+(?:note|correction)\b|"
    r"book\s+reviews?\b|commentary\b|comment\s+on\b|"
    r"discussion\s+of\b|introduction\b|"
    r"issue\s+information\b|covers?\s+and\s+front\s+matter\b|"
    r"front\s+matter\b|back\s+matter\b|"
    r"cover(?:\s*$|\s+image\b)|in\s+this\s+issue\b|masthead\b|"
    r"table\s+of\s+contents\b|"
    r"announcements?\b|american\s+finance\s+association\b|"
    r"miscellanea\b|dimensional\s+fund\s+advisors\b|"
    r"brattle\s+group\b|amundi\b|"
    r"call\s+for\s+papers?\b|forthcoming\s+articles?\b|"
    r"preliminary\s+program\b|participant\s+schedule\b|"
    r"afa\s+\d{4}\b|index\s+to\s+volume\b|"
    r"acknowledg(?:e)?ments?\b|in\s+memoriam\b|minutes\s+of\b|"
    r"obituary\b|preface\b|foreward\b|foreword\b|"
    r"list\s+of\s+(?:reviewers|referees)\b|ad\s+hoc\s+reviewers\b|"
    r"\d{4}\s+excellence\s+in\s+refereeing\b|"
    r"jfq\b|car\b|abstracts/|oup\s+accepted\s+manuscript\b|"
    r"sfs\s+statement\b|aaa\b|biblioscene\b|"
    r"be\s+the\s+thought\s+leaders\b"
    r")",
    re.IGNORECASE,
)
NONRESEARCH_ANYWHERE = re.compile(r"\bplacement\s+ads?\b", re.IGNORECASE)


def _clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value or ""))).strip()
USER_AGENT = (
    "accounting-finance-research-ai-era/1.0 "
    "(mailto:research@zhangyuqian.com)"
)

JOURNALS = [
    ("The Accounting Review", "0001-4826", "Accounting"),
    ("Journal of Accounting Research", "0021-8456", "Accounting"),
    ("Journal of Accounting and Economics", "0165-4101", "Accounting"),
    ("Contemporary Accounting Research", "0823-9150", "Accounting"),
    ("Review of Accounting Studies", "1380-6653", "Accounting"),
    ("Accounting, Organizations and Society", "0361-3682", "Accounting"),
    ("The Journal of Finance", "0022-1082", "Finance"),
    ("Journal of Financial Economics", "0304-405X", "Finance"),
    ("The Review of Financial Studies", "0893-9454", "Finance"),
    ("Journal of Financial and Quantitative Analysis", "0022-1090", "Finance"),
    ("Review of Finance", "1572-3097", "Finance"),
]


def _fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Crossref request failed")


def _year(item: dict) -> int | None:
    for key in ("published-print", "published-online", "issued"):
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def collect() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for journal, issn, field in JOURNALS:
        cursor = "*"
        while cursor:
            params = urllib.parse.urlencode(
                {
                    "filter": (
                        "type:journal-article,"
                        "from-pub-date:2014-01-01,"
                        "until-pub-date:2026-12-31"
                    ),
                    "rows": 1000,
                    "cursor": cursor,
                    "select": (
                        "DOI,title,type,published-print,published-online,"
                        "issued,container-title"
                    ),
                }
            )
            payload = _fetch_json(
                f"https://api.crossref.org/journals/{issn}/works?{params}"
            )
            message = payload["message"]
            for item in message["items"]:
                year = _year(item)
                if year is None or not 2015 <= year <= 2025:
                    continue
                title = _clean_title((item.get("title") or [""])[0])
                if NONRESEARCH_TITLE.search(title) or NONRESEARCH_ANYWHERE.search(title):
                    continue
                rows.append(
                    {
                        "journal": journal,
                        "field": field,
                        "issn": issn,
                        "publication_year": year,
                        "doi": item.get("DOI", "").lower(),
                        "title": title,
                        "crossref_type": item.get("type", ""),
                        "source": "Crossref REST API",
                        "accessed_at": ACCESS_DATE,
                    }
                )
            cursor = message.get("next-cursor")
            if not message["items"]:
                cursor = None
            time.sleep(0.25)
        print(f"{journal}: {sum(r['journal'] == journal for r in rows)} articles")

    deduped = {row["doi"]: row for row in rows}
    article_rows = sorted(
        deduped.values(),
        key=lambda row: (row["journal"], row["publication_year"], row["doi"]),
    )
    article_path = DATA / "crossref_articles.csv"
    with article_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(article_rows[0]))
        writer.writeheader()
        writer.writerows(article_rows)

    counts: dict[tuple[str, str, int], int] = {}
    for row in article_rows:
        key = (str(row["journal"]), str(row["field"]), int(row["publication_year"]))
        counts[key] = counts.get(key, 0) + 1

    count_rows = [
        {
            "journal": journal,
            "field": field,
            "year": year,
            "crossref_research_articles": count,
            "source": "Crossref REST API",
            "accessed_at": ACCESS_DATE,
        }
        for (journal, field, year), count in sorted(counts.items())
    ]
    aggregate_path = DATA / "crossref_article_counts.csv"
    with aggregate_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(count_rows[0]))
        writer.writeheader()
        writer.writerows(count_rows)

    print(f"Wrote {len(article_rows)} unique articles")
    print(f"Wrote {len(count_rows)} journal-year observations")


if __name__ == "__main__":
    collect()
