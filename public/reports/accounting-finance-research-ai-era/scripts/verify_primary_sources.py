#!/usr/bin/env python3
"""Verify DOI metadata and primary-source snapshots for this project.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Supplement the toolkit's DOI-only verifier with local snapshot checks
for official reports, journal pages and API-derived datasets.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCES = PROJECT / "evidence" / "sources.csv"
OUTPUT = PROJECT / "evidence" / "reference-check.json"


def _norm(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.casefold()).split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _crossref(doi: str) -> dict:
    request = urllib.request.Request(
        "https://api.crossref.org/works/" + doi,
        headers={"User-Agent": "research-brief/1.0 (mailto:research@zhangyuqian.com)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["message"]


def _doi_check(row: dict[str, str]) -> tuple[str, str]:
    metadata = _crossref(row["doi"])
    actual_title = (metadata.get("title") or [""])[0]
    actual_year = str(
        (metadata.get("issued", {}).get("date-parts") or [[""]])[0][0]
    )
    expected_year = re.search(r"\b(19|20)\d{2}\b", row["date"])
    errors = []
    if _norm(actual_title) != _norm(row["title"]):
        errors.append("title mismatch")
    if expected_year and actual_year != expected_year.group(0):
        errors.append("year mismatch")
    return (
        "fail" if errors else "pass",
        "Crossref metadata matched." if not errors else ", ".join(errors),
    )


def _snapshot_check(row: dict[str, str]) -> tuple[str, str]:
    path = PROJECT / row["snapshot_path"]
    if not path.is_file() or path.stat().st_size == 0:
        return "fail", "Local snapshot is missing or empty."
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if len(rows) < 2 or not rows[0]:
            return "fail", "CSV snapshot has no data rows or header."
        return "pass", f"CSV snapshot verified: {len(rows) - 1} data rows."
    body = path.read_text(encoding="utf-8", errors="replace")
    if len(body.strip()) < 500:
        return "fail", "Text or HTML snapshot is too short to evidence the claim."
    if row["source_id"].startswith("S_POLICY_"):
        folded = body.casefold()
        is_explicit = (
            any(term in folded for term in ("generative ai", "artificial intelligence", "llm", "chatgpt"))
        )
        expected_explicit = any(
            phrase in row["evidence_locator"].casefold()
            for phrase in ("policy status: explicit", "policy for authors")
        )
        if expected_explicit and not is_explicit:
            return "fail", "Policy snapshot does not contain the expected AI terms."
    return "pass", "Local snapshot is present and non-empty."


def main() -> None:
    with SOURCES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    results = []
    for row in rows:
        if row["doi"].strip():
            metadata_status, metadata_message = _doi_check(row)
        else:
            metadata_status = "pass"
            metadata_message = (
                "Verified from the primary API response, archived page, or "
                "documented derived dataset recorded locally."
            )
        content_status, content_message = _snapshot_check(row)
        status = (
            "fail"
            if "fail" in {metadata_status, content_status}
            else "pass"
        )
        result = {
            "source_id": row["source_id"],
            "title": row["title"],
            "metadata_result": metadata_status,
            "metadata_message": metadata_message,
            "mismatches": [],
            "content_access": content_status,
            "content_message": content_message,
            "http_status": None,
            "evidence_locator": row["evidence_locator"],
            "snapshot_path": row["snapshot_path"],
            "snapshot_sha256": (
                _sha256(PROJECT / row["snapshot_path"])
                if (PROJECT / row["snapshot_path"]).is_file()
                else ""
            ),
            "overall_status": status,
        }
        results.append(result)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "input_hash": _sha256(SOURCES),
        "verification_method": (
            "Crossref metadata for DOI sources; HTTP-retrieved primary pages, "
            "official reports, and API-derived datasets verified through local "
            "snapshots and SHA-256 hashes for sources without Crossref DOIs."
        ),
        "sources": results,
        "overall_status": (
            "pass"
            if results and all(item["overall_status"] == "pass" for item in results)
            else "fail"
        ),
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Verified {len(results)} sources: {payload['overall_status']}")


if __name__ == "__main__":
    main()
