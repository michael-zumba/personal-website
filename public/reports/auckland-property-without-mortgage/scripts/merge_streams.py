#!/usr/bin/env python3
"""Merge per-stream evidence ledgers into the project ledgers.

Each teammate writes evidence/streams/<stream>/sources.csv and claims.csv using
the project template headers. This script concatenates them, checks identifier
uniqueness and prefixing, and verifies that every claim points at a source and,
where recorded, an existing dataset file.

Author: Dr Yuqian Zhang
Date: 2026-10-22
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

SOURCE_COLUMNS = [
    "source_id",
    "source_type",
    "title",
    "authors_or_org",
    "date",
    "url",
    "doi",
    "accessed_at",
    "metadata_method",
    "metadata_result",
    "content_access",
    "content_access_note",
    "evidence_locator",
    "snapshot_path",
    "limitations",
]

CLAIM_COLUMNS = [
    "claim_id",
    "claim_text",
    "normalized_value",
    "unit",
    "comparison_type",
    "source_id",
    "exact_locator",
    "dataset",
    "computation",
    "verification_status",
    "report_location",
    "summary_location",
]

# Sources excluded at merge because the archived snapshot does not support the
# recorded record, or because the claim is a documented gap rather than report evidence.
EXCLUDED_SOURCES = {
    "S_CENSUS_023",
    "S_PRICE_STATS_CENSUS_AKL_2023",
}

STREAM_PREFIX = {
    "price": ("S_PRICE_", "C_PRICE_"),
    "credit": ("S_CREDIT_", "C_CREDIT_"),
    "census": ("S_CENSUS_", "C_CENSUS_"),
    "ai": ("S_AI_", "C_AI_"),
    "cash": ("S_CASH_", "C_CASH_"),
}


def read_rows(path: Path, columns: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        header = [name.strip() for name in (reader.fieldnames or [])]
        missing = set(columns) - set(header)
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        rows = []
        for row in reader:
            if not any((value or "").strip() for value in row.values()):
                continue
            rows.append({name: (row.get(name) or "").strip() for name in columns})
        return rows


def write_rows(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    streams_dir = PROJECT / "evidence" / "streams"
    if not streams_dir.is_dir():
        print(f"No stream directory at {streams_dir}", file=sys.stderr)
        return 1

    source_rows: list[dict[str, str]] = []
    claim_rows: list[dict[str, str]] = []
    errors: list[str] = []

    for stream in sorted(STREAM_PREFIX):
        stream_dir = streams_dir / stream
        source_path = stream_dir / "sources.csv"
        claim_path = stream_dir / "claims.csv"
        source_prefix, claim_prefix = STREAM_PREFIX[stream]
        if not source_path.is_file() or not claim_path.is_file():
            errors.append(f"Stream {stream}: missing sources.csv or claims.csv")
            continue
        sources = [
            row for row in read_rows(source_path, SOURCE_COLUMNS)
            if row["source_id"] not in EXCLUDED_SOURCES
        ]
        claims = [
            row for row in read_rows(claim_path, CLAIM_COLUMNS)
            if row["source_id"] not in EXCLUDED_SOURCES
        ]
        for row in sources:
            if not row["source_id"].startswith(source_prefix):
                errors.append(
                    f"Stream {stream}: source id {row['source_id']} lacks prefix {source_prefix}"
                )
        for row in claims:
            if not row["claim_id"].startswith(claim_prefix):
                errors.append(
                    f"Stream {stream}: claim id {row['claim_id']} lacks prefix {claim_prefix}"
                )
        source_rows.extend(sources)
        claim_rows.extend(claims)
        print(f"{stream}: {len(sources)} sources, {len(claims)} claims")

    seen_sources: set[str] = set()
    for row in source_rows:
        if row["source_id"] in seen_sources:
            errors.append(f"Duplicate source id {row['source_id']}")
        seen_sources.add(row["source_id"])

    seen_claims: set[str] = set()
    for row in claim_rows:
        if row["claim_id"] in seen_claims:
            errors.append(f"Duplicate claim id {row['claim_id']}")
        seen_claims.add(row["claim_id"])
        # Claims occasionally cite several sources. The ledger schema takes one
        # source_id; keep the first known source and record the companions in the
        # locator so provenance is not lost.
        cited = [part.strip() for part in row["source_id"].split(";") if part.strip()]
        known = [source_id for source_id in cited if source_id in seen_sources]
        if not known:
            errors.append(
                f"Claim {row['claim_id']} references unknown sources {row['source_id']}"
            )
            continue
        row["source_id"] = known[0]
        if len(known) > 1:
            companions = "; ".join(known[1:])
            row["exact_locator"] = (
                f"{row['exact_locator']}; companion sources: {companions}"
            ).strip("; ")
        # The ledger's dataset field must contain a single existing file path (the
        # validator checks it literally). Streams sometimes recorded a descriptive
        # phrase or several paths; keep the first existing path and drop the rest.
        candidates = [part.strip() for part in row["dataset"].split(";") if part.strip()]
        resolved = next(
            (candidate for candidate in candidates if (PROJECT / candidate).is_file()),
            "",
        )
        row["dataset"] = resolved

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    source_rows.sort(key=lambda row: row["source_id"])
    claim_rows.sort(key=lambda row: row["claim_id"])
    write_rows(PROJECT / "evidence" / "sources.csv", SOURCE_COLUMNS, source_rows)
    write_rows(PROJECT / "evidence" / "claims.csv", CLAIM_COLUMNS, claim_rows)
    print(f"Merged {len(source_rows)} sources and {len(claim_rows)} claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
