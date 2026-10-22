#!/usr/bin/env python3
"""Collect OpenAlex article and citation cohorts for the approved journal sample.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Build a reproducible three-calendar-year attention measure.
"""

from __future__ import annotations

import csv
import html
import json
import re
import statistics
import time
import urllib.error
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
API = "https://api.openalex.org/works"

JOURNALS = [
    ("The Accounting Review", "Accounting", "S160506855"),
    ("Journal of Accounting Research", "Accounting", "S111116695"),
    ("Journal of Accounting and Economics", "Accounting", "S62142384"),
    ("Contemporary Accounting Research", "Accounting", "S65924262"),
    ("Review of Accounting Studies", "Accounting", "S11853582"),
    ("Accounting, Organizations and Society", "Accounting", "S198892436"),
    ("The Journal of Finance", "Finance", "S5353659"),
    ("Journal of Financial Economics", "Finance", "S149240962"),
    ("The Review of Financial Studies", "Finance", "S170137484"),
    ("Journal of Financial and Quantitative Analysis", "Finance", "S193228710"),
]

YEARS = range(2020, 2023)


def _fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if attempt == 3:
                body = error.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"OpenAlex HTTP {error.code}: {body[:500]}"
                ) from error
            time.sleep(2 ** attempt)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("OpenAlex request failed")


def _doi(value: str | None) -> str:
    return (value or "").removeprefix("https://doi.org/").lower()


def _read_crossref() -> list[dict[str, str]]:
    with (DATA / "crossref_articles.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    return [
        row
        for row in rows
        if int(row["publication_year"]) in YEARS
    ]


def collect() -> None:
    crossref = _read_crossref()
    crossref_by_journal: dict[str, set[str]] = {}
    for row in crossref:
        crossref_by_journal.setdefault(row["journal"], set()).add(row["doi"])

    article_rows: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []
    for journal, field, source_id in JOURNALS:
        print(f"Collecting {journal}", flush=True)
        journal_rows: list[dict[str, object]] = []
        for year in YEARS:
            print(f"  {year}", flush=True)
            page = 1
            expected = None
            while expected is None or (page - 1) * 200 < expected:
                params = urllib.parse.urlencode(
                    {
                        "filter": (
                            f"primary_location.source.id:{source_id},"
                            f"publication_year:{year},"
                            "type:article,has_doi:true"
                        ),
                        "select": (
                            "id,doi,title,publication_year,cited_by_count,"
                            "counts_by_year,type"
                        ),
                        "per-page": 200,
                        "page": page,
                        "mailto": "research@zhangyuqian.com",
                    }
                )
                payload = _fetch_json(f"{API}?{params}")
                expected = payload["meta"]["count"]
                for item in payload["results"]:
                    item_year = int(item["publication_year"])
                    doi = _doi(item.get("doi"))
                    if item_year not in YEARS or not doi:
                        continue
                    title = _clean_title(item.get("title") or "")
                    if NONRESEARCH_TITLE.search(title) or NONRESEARCH_ANYWHERE.search(title):
                        continue
                    first_three = sum(
                        int(c["cited_by_count"])
                        for c in item.get("counts_by_year", [])
                        if item_year
                        <= int(c["year"])
                        <= item_year + 2
                    )
                    journal_rows.append(
                        {
                            "journal": journal,
                            "field": field,
                            "publication_year": item_year,
                            "doi": doi,
                            "openalex_id": item.get("id", ""),
                            "title": title,
                            "citations_first_3y": first_three,
                            "zero_citations_first_3y": int(first_three == 0),
                            "current_citations": int(
                                item.get("cited_by_count") or 0
                            ),
                            "matched_crossref": int(
                                doi
                                in crossref_by_journal.get(journal, set())
                            ),
                            "accessed_at": ACCESS_DATE,
                        }
                    )
                if not payload["results"]:
                    break
                page += 1
                time.sleep(0.4)

        deduped = {str(row["doi"]): row for row in journal_rows}
        article_rows.extend(deduped.values())
        crossref_dois = crossref_by_journal.get(journal, set())
        matched_dois = crossref_dois & set(deduped)
        coverage_rows.append(
            {
                "journal": journal,
                "field": field,
                "openalex_source_id": f"https://openalex.org/{source_id}",
                "crossref_dois_2020_2022": len(crossref_dois),
                "openalex_matched_dois_2020_2022": len(matched_dois),
                "doi_coverage_share": (
                    len(matched_dois) / len(crossref_dois)
                    if crossref_dois
                    else ""
                ),
                "assessment": "Included in attention analysis.",
                "accessed_at": ACCESS_DATE,
            }
        )
        print(
            f"{journal}: {len(deduped)} OpenAlex records, "
            f"{len(matched_dois)}/{len(crossref_dois)} Crossref DOIs matched"
        )

    article_rows.sort(
        key=lambda row: (
            str(row["journal"]),
            int(row["publication_year"]),
            str(row["doi"]),
        )
    )
    article_path = DATA / "openalex_attention_articles.csv"
    with article_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(article_rows[0]))
        writer.writeheader()
        writer.writerows(article_rows)

    groups: dict[tuple[str, str, int], list[int]] = {}
    for row in article_rows:
        key = (
            str(row["journal"]),
            str(row["field"]),
            int(row["publication_year"]),
        )
        groups.setdefault(key, []).append(int(row["citations_first_3y"]))

    cohort_rows = []
    for (journal, field, year), values in sorted(groups.items()):
        cohort_rows.append(
            {
                "journal": journal,
                "field": field,
                "publication_year": year,
                "articles": len(values),
                "zero_citations_articles": sum(value == 0 for value in values),
                "zero_citation_share": sum(value == 0 for value in values)
                / len(values),
                "median_citations_first_3y": statistics.median(values),
                "mean_citations_first_3y": statistics.mean(values),
                "maximum_citations_first_3y": max(values),
                "window": "publication year through publication year plus two",
                "source": "OpenAlex work counts_by_year",
                "accessed_at": ACCESS_DATE,
            }
        )
    cohort_path = DATA / "attention_cohorts.csv"
    with cohort_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cohort_rows[0]))
        writer.writeheader()
        writer.writerows(cohort_rows)

    coverage_path = DATA / "openalex_coverage.csv"
    with coverage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage_rows[0]))
        writer.writeheader()
        writer.writerows(coverage_rows)

    print(f"Wrote {len(article_rows)} OpenAlex article records")
    print(f"Wrote {len(cohort_rows)} included journal-year cohorts")


if __name__ == "__main__":
    collect()
