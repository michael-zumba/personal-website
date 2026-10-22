#!/usr/bin/env python3
"""Build the report's derived tables from audited raw datasets.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Keep every derived statistic deterministic and inspectable.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"


def _read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write(name: str, rows: list[dict[str, object]]) -> None:
    with (DATA / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build() -> None:
    crossref = _read("crossref_article_counts.csv")
    field_year: dict[tuple[str, int], int] = defaultdict(int)
    journal_year: dict[tuple[str, int], int] = defaultdict(int)
    for row in crossref:
        year = int(row["year"])
        count = int(row["crossref_research_articles"])
        field_year[(row["field"], year)] += count
        journal_year[(row["journal"], year)] += count
    _write(
        "field_article_counts.csv",
        [
            {
                "field": field,
                "year": year,
                "crossref_research_articles": count,
            }
            for (field, year), count in sorted(field_year.items())
        ],
    )

    cohorts = _read("attention_cohorts.csv")
    attention: dict[tuple[str, str], list[int]] = {}
    for row in cohorts:
        key = (row["journal"], row["field"])
        values = attention.setdefault(key, [0, 0])
        values[0] += int(row["zero_citations_articles"])
        values[1] += int(row["articles"])
    _write(
        "attention_journal_summary.csv",
        [
            {
                "journal": journal,
                "field": field,
                "zero_citations_articles": values[0],
                "articles": values[1],
                "zero_citation_share": values[0] / values[1],
                "cohorts": "2020-2022",
                "window": "publication year through publication year plus two",
            }
            for (journal, field), values in sorted(attention.items())
        ],
    )

    submissions = _read("submissions_outputs.csv")
    first: dict[str, tuple[str, int]] = {}
    indexed = []
    for row in sorted(submissions, key=lambda item: item["reporting_period_start"]):
        journal = row["journal"]
        total = int(row["total_submissions"])
        if journal not in first:
            first[journal] = (row["reporting_period_start"], total)
        base_date, base_total = first[journal]
        indexed.append(
            {
                "journal": journal,
                "reporting_period_start": row["reporting_period_start"],
                "reporting_period_end": row["reporting_period_end"],
                "total_submissions": total,
                "base_period_start": base_date,
                "base_submissions": base_total,
                "submission_index": total / base_total * 100,
            }
        )
    _write("submission_index.csv", indexed)

    policy = _read("ai_policy_status.csv")
    latest: dict[str, dict[str, str]] = {}
    for row in policy:
        current = latest.get(row["journal"])
        if current is None or row["snapshot_timestamp"] > current["snapshot_timestamp"]:
            latest[row["journal"]] = row
    _write(
        "ai_policy_latest.csv",
        [
            {
                "journal": row["journal"],
                "field": row["field"],
                "snapshot_date": row["snapshot_timestamp"][:8],
                "policy_status": row["policy_status"],
                "source_id": row["source_id"],
                "snapshot_url": row["snapshot_url"],
            }
            for _, row in sorted(latest.items())
        ],
    )

    priorities = _read("editorial_priorities.csv")
    by_category: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for row in priorities:
        by_category[row["category"]][0] += int(row["present"])
        by_category[row["category"]][1] += 1
    _write(
        "editorial_priority_summary.csv",
        [
            {
                "category": category,
                "journals_with_explicit_mention": values[0],
                "journals_observed": values[1],
                "share": values[0] / values[1],
            }
            for category, values in sorted(by_category.items())
        ],
    )

    field_2015 = field_year[("Accounting", 2015)] + field_year[("Finance", 2015)]
    field_2025 = field_year[("Accounting", 2025)] + field_year[("Finance", 2025)]
    zero_total = sum(values[0] for values in attention.values())
    article_total = sum(values[1] for values in attention.values())
    latest_policy = list(latest.values())
    jf = {
        row["reporting_period_start"]: row
        for row in submissions
        if row["journal"] == "The Journal of Finance"
    }
    rfs = {
        row["reporting_period_start"]: row
        for row in submissions
        if row["journal"] == "The Review of Financial Studies"
    }
    statistics = [
        {
            "statistic_id": "articles_2015",
            "value": field_2015,
            "unit": "Crossref research articles",
            "definition": "Sum across 11 selected journals",
        },
        {
            "statistic_id": "articles_2025",
            "value": field_2025,
            "unit": "Crossref research articles",
            "definition": "Sum across 11 selected journals",
        },
        {
            "statistic_id": "articles_change_2015_2025",
            "value": field_2025 / field_2015 - 1,
            "unit": "fraction",
            "definition": "2025 count divided by 2015 count minus one",
        },
        {
            "statistic_id": "jf_submissions_2015",
            "value": jf["2015-01-01"]["total_submissions"],
            "unit": "submissions",
            "definition": "Journal of Finance calendar-year total",
        },
        {
            "statistic_id": "jf_submissions_2024",
            "value": jf["2024-01-01"]["total_submissions"],
            "unit": "submissions",
            "definition": "Journal of Finance calendar-year total",
        },
        {
            "statistic_id": "rfs_submissions_2023",
            "value": rfs["2022-05-15"]["total_submissions"],
            "unit": "submissions",
            "definition": "RFS 2022-05-15 to 2023-05-15 reporting period",
        },
        {
            "statistic_id": "rfs_submissions_2026",
            "value": rfs["2025-05-01"]["total_submissions"],
            "unit": "submissions",
            "definition": "RFS 2025-05-01 to 2026-05-01 reporting period",
        },
        {
            "statistic_id": "zero_citation_share_2020_2022",
            "value": zero_total / article_total,
            "unit": "fraction",
            "definition": "Pooled zero-citation share for Crossref-matched OpenAlex articles, 2020-2022 issue-year cohorts, three calendar years from the Crossref year",
        },
        {
            "statistic_id": "explicit_ai_guidance_latest",
            "value": sum(
                row["policy_status"] == "Explicit AI guidance"
                for row in latest_policy
            ),
            "unit": "journals",
            "definition": "Latest verified author-page snapshot in the sample",
        },
        {
            "statistic_id": "journals_with_policy_snapshot",
            "value": len(latest_policy),
            "unit": "journals",
            "definition": "Journals with a usable latest author-page snapshot",
        },
    ]
    _write("analysis_statistics.csv", statistics)

    for row in statistics:
        print(f"{row['statistic_id']}: {row['value']} {row['unit']}")


if __name__ == "__main__":
    build()
