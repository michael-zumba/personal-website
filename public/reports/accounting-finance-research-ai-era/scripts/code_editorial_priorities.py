#!/usr/bin/env python3
"""Code explicit editorial priorities in the latest author-guidance snapshots.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Produce an auditable text-presence matrix with a simple published codebook.
"""

from __future__ import annotations

import csv
from pathlib import Path

from bs4 import BeautifulSoup


PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"

CODEBOOK = {
    "Contribution": ("contribution", "novelty", "significance", "importance"),
    "Research design": ("research design", "identification", "rigorous", "rigor"),
    "Data transparency": (
        "data availability",
        "data sharing",
        "data access",
        "data policy",
        "research data",
    ),
    "Reproducibility": (
        "replicat",
        "reproduc",
        "code sharing",
        "code and data",
    ),
    "Decision relevance": (
        "practitioner",
        "practice",
        "policymaker",
        "regulation",
        "decision-making",
    ),
    "Integrity and accountability": (
        "research integrity",
        "plagiarism",
        "misconduct",
        "accountab",
    ),
}


def _main_text(path: Path) -> str:
    soup = BeautifulSoup(
        path.read_text(encoding="utf-8", errors="replace"), "html.parser"
    )
    for node in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        node.decompose()
    main = soup.find("main") or soup.body or soup
    return " ".join(main.get_text(" ", strip=True).split())


def main() -> None:
    with (DATA / "ai_policy_status.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        policy_rows = list(csv.DictReader(handle))

    latest = {}
    for row in policy_rows:
        current = latest.get(row["journal"])
        if current is None or row["snapshot_timestamp"] > current["snapshot_timestamp"]:
            latest[row["journal"]] = row

    rows = []
    for journal in sorted(latest):
        source = latest[journal]
        text = _main_text(PROJECT / source["snapshot_path"])
        folded = text.casefold()
        for category, terms in CODEBOOK.items():
            matches = [term for term in terms if term in folded]
            rows.append(
                {
                    "journal": journal,
                    "field": source["field"],
                    "snapshot_date": source["snapshot_timestamp"][:8],
                    "category": category,
                    "present": int(bool(matches)),
                    "matched_terms": ";".join(matches),
                    "source_id": f"S_POLICY_{journal.upper().replace(' ', '_').replace(',', '').replace('.', '')}_{source['snapshot_timestamp'][:8]}",
                    "snapshot_path": source["snapshot_path"],
                }
            )

    path = DATA / "editorial_priorities.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} coded journal-category observations")


if __name__ == "__main__":
    main()
