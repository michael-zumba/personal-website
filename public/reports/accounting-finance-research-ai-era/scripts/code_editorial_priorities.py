#!/usr/bin/env python3
"""Assemble the manual editorial-priority coding into the published data table.

Author: Dr Yuqian Zhang
Date: 2026-10-22 (revised after technical review)
Purpose: Record a context-verified, hand-coded matrix of stated editorial criteria.

The coding is done by hand from the extracted visible guidance text of each
journal's latest usable official page. Each PRESENT cell carries a short
quotable excerpt in evidence/expansion/editorial_recode/editorial_recode.csv.
A criterion counts only when the page states it as an author requirement or an
editorial expectation. Site navigation, JEL browse lists, copyright and cookie
boilerplate, proof-stage notices and shared publisher template paragraphs are
excluded: only "journal-specific" and "society-or-publisher-policy" bases are
counted.
"""

from __future__ import annotations

import csv
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
RECODE = PROJECT / "evidence/expansion/editorial_recode/editorial_recode.csv"
CATEGORIES = [
    "Contribution",
    "Research design",
    "Data transparency",
    "Reproducibility",
    "Decision relevance",
    "Integrity and accountability",
]
SUBSTANTIVE_BASES = {"journal-specific", "society-or-publisher-policy"}


def main() -> None:
    recode = list(csv.DictReader(RECODE.open(newline="", encoding="utf-8")))

    latest: dict[str, dict[str, str]] = {}
    with (DATA / "ai_policy_status.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        for row in csv.DictReader(handle):
            current = latest.get(row["journal"])
            if (
                current is None
                or row["snapshot_timestamp"] > current["snapshot_timestamp"]
            ):
                latest[row["journal"]] = row

    rows = []
    for code in recode:
        source = latest[code["journal"]]
        present = int(code["present"]) if code["basis"] in SUBSTANTIVE_BASES else 0
        rows.append(
            {
                "journal": code["journal"],
                "field": source["field"],
                "snapshot_date": source["snapshot_timestamp"][:8],
                "category": code["category"],
                "present": present,
                "matched_terms": f"manual code: {code['basis']}",
                "source_id": source["source_id"],
                "snapshot_path": source["snapshot_path"],
            }
        )
    rows.sort(key=lambda row: (row["journal"], row["category"]))
    path = DATA / "editorial_priorities.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    counts = {
        category: sum(
            row["present"] == 1 for row in rows if row["category"] == category
        )
        for category in CATEGORIES
    }
    print(f"Wrote {len(rows)} coded journal-category observations")
    print("Counts:", counts)


if __name__ == "__main__":
    main()
