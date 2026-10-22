#!/usr/bin/env python3
"""Reproduce the Crossref correction, erratum and retraction record counts.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Make the update-record counts in the report executable and auditable.

For each selected journal ISSN the script issues three Crossref journal-works
requests with update-type filters (retraction, erratum, correction) over
2015-01-01 to 2025-12-31 and records message.total-results. Counts are filtered
record counts, not retraction rates: one event can appear more than once.
"""

from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
ACCESS_DATE = "2026-10-22"
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
UPDATE_TYPES = ["retraction", "erratum", "correction"]


def _count(issn: str, update_type: str) -> int:
    params = urllib.parse.urlencode(
        {
            "filter": (
                f"update-type:{update_type},"
                "from-pub-date:2015-01-01,until-pub-date:2025-12-31"
            ),
            "rows": 0,
        }
    )
    url = f"https://api.crossref.org/journals/{issn}/works?{params}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.load(response)
            return int(payload["message"]["total-results"])
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Crossref request failed")


def main() -> None:
    rows = []
    for journal, issn, field in JOURNALS:
        counts = {kind: _count(issn, kind) for kind in UPDATE_TYPES}
        rows.append(
            {
                "journal": journal,
                "field": field,
                "retraction_update_records": counts["retraction"],
                "erratum_update_records": counts["erratum"],
                "correction_update_records": counts["correction"],
                "period_start": "2015-01-01",
                "period_end": "2025-12-31",
                "source_id": "S_CROSSREF_API",
                "definition_note": (
                    "Crossref works matching each update-type filter; a single "
                    "event can appear more than once"
                ),
            }
        )
        print(journal, counts)
        time.sleep(0.3)
    path = DATA / "corrections_retractions.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    totals = {
        kind: sum(row[f"{kind}_update_records"] for row in rows)
        for kind in UPDATE_TYPES
    }
    print("Totals:", totals)


if __name__ == "__main__":
    main()
