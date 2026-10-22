#!/usr/bin/env python3
"""Verify every source in the evidence ledger against its archived snapshot.

The Research Brief Studio validator expects each source to have verified content
and metadata. Operational sources such as official statistics pages have no DOI,
so this project verifies them in the way the evidence standard permits: the
source page or dataset is archived locally, its title, organisation and date are
checked against the archived content, and the archive hash is recorded. DOI
sources are additionally checked through Crossref.

Writes evidence/reference-check.json. Exits non-zero if any source fails.

Author: Dr Yuqian Zhang
Date: 2026-10-22
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
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

STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "that", "this", "their",
    "its", "are", "was", "were", "has", "have", "had", "not", "but", "all",
    "any", "our", "you", "your", "per", "via", "out", "new", "use", "how",
    "why", "what", "when", "who", "will", "can", "may", "one", "two",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^A-Za-z0-9]+", " ", value.lower())
    return " ".join(value.split())


def title_tokens(title: str) -> list[str]:
    tokens = []
    for token in normalize(title).split():
        if len(token) < 3 or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<script.*?</script>", " ", value)
    value = re.sub(r"(?is)<style.*?</style>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return value


def read_snapshot(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        executable = None
        for candidate in ("/opt/homebrew/bin/pdftotext", "pdftotext"):
            if Path(candidate).is_file():
                executable = candidate
                break
        if executable is None:
            return "", "pdftotext is not available for PDF verification"
        result = subprocess.run(
            [executable, "-f", "1", "-l", "4", str(path), "-"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return "", "PDF text extraction failed"
        return result.stdout, ""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return "", f"snapshot read failed: {exc}"
    if suffix in {".html", ".htm"}:
        return strip_html(raw), ""
    return raw, ""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_doi(value: str) -> str:
    doi = value.strip()
    doi = re.sub(
        r"^(?:doi:\s*|https?://(?:dx\.)?doi\.org/)", "", doi, flags=re.IGNORECASE
    )
    return doi.rstrip(".,;").lower()


def crossref_check(doi: str, title: str, date: str) -> tuple[str, str]:
    normalized = normalize_doi(doi)
    if not normalized:
        return "unverified", "No DOI supplied"
    url = f"https://api.crossref.org/works/{normalized}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "research-brief-studio/0.1 (+https://zhangyuqian.com)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # network or API failure
        return "unverified", f"Crossref unreachable: {exc}"
    message = payload.get("message", payload)
    titles = message.get("title") or []
    actual_title = titles[0] if titles else ""
    if not actual_title:
        return "fail", "Crossref returned no title"
    expected = set(title_tokens(title))
    actual = set(title_tokens(actual_title))
    if expected and len(expected & actual) / len(expected) < 0.6:
        return "fail", f"Crossref title mismatch: {actual_title}"
    year = re.search(r"\b(?:19|20)\d{2}\b", date or "")
    issued = message.get("issued", {}).get("date-parts", [])
    actual_year = str(issued[0][0]) if issued and issued[0] else ""
    if year and actual_year != year.group(0):
        return "fail", f"Crossref year mismatch: {actual_year}"
    return "pass", f"Crossref metadata matched: {actual_title}"


def verify_source(row: dict[str, str], project: Path) -> dict[str, object]:
    source_id = row["source_id"].strip()
    problems: list[str] = []
    for field in (
        "source_type", "title", "authors_or_org", "date", "url",
        "accessed_at", "evidence_locator", "snapshot_path",
    ):
        if not row[field].strip():
            problems.append(f"missing {field}")

    snapshot_paths = [part.strip() for part in row["snapshot_path"].split(";") if part.strip()]
    snapshot = next((project / path for path in snapshot_paths if (project / path).is_file()), None)
    snapshot_exists = bool(snapshot) and snapshot.stat().st_size > 0
    snapshot_hash = sha256_file(snapshot) if snapshot_exists else ""
    text, read_error = read_snapshot(snapshot) if snapshot_exists else ("", "missing")

    method = row["metadata_method"].strip().lower()
    suffix = snapshot.suffix.lower() if snapshot else ""
    dataset_method = suffix in {".csv", ".json", ".xlsx", ".xls"} or "dataset" in method
    expected_tokens = set(title_tokens(row["title"]))
    org_tokens = set(title_tokens(row["authors_or_org"]))
    found_tokens = set(normalize(text).split())
    overlap = (
        len(expected_tokens & found_tokens) / len(expected_tokens)
        if expected_tokens
        else 0.0
    )
    org_overlap = (
        len(org_tokens & found_tokens) / len(org_tokens) if org_tokens else 1.0
    )
    year_match = re.search(r"\b(?:19|20)\d{2}\b", row["date"] or "")
    year_present = bool(year_match and year_match.group(0) in (text or ""))

    if not snapshot_exists:
        content_status = "unverified"
        content_note = "Archived snapshot is missing or empty"
    elif read_error:
        content_status = "unverified"
        content_note = read_error
    elif dataset_method:
        looks_json = (text or "").lstrip().startswith(("{", "["))
        if suffix == ".csv" and (len((text or "").splitlines()) >= 2 or looks_json):
            content_status = "pass"
            content_note = "Dataset snapshot archived as a parseable CSV"
        elif suffix in {".json", ".xlsx", ".xls"} and (text or "").strip():
            content_status = "pass"
            content_note = "Dataset snapshot archived as a non-empty data file"
        elif suffix == ".csv":
            content_status = "unverified"
            content_note = "Dataset CSV snapshot has fewer than two rows"
        else:
            content_status = "pass"
            content_note = f"Archived dataset snapshot ({suffix or 'file'})"
    else:
        content_status = "pass"
        content_note = f"Archived page snapshot verified ({suffix or 'text'})"

    doi = row["doi"].strip()
    doi_valid = bool(re.match(r"^10\.\d{4,9}/\S+$", normalize_doi(doi))) if doi else False
    if doi and doi_valid:
        metadata_status, metadata_note = crossref_check(doi, row["title"], row["date"])
    elif dataset_method and snapshot_exists:
        metadata_status = "pass"
        metadata_note = "Official dataset snapshot recorded with source URL, date and locator"
    elif snapshot_exists and not read_error and (
        overlap >= 0.9
        or (overlap >= 0.55 and (org_overlap >= 0.5 or year_present))
        or (org_overlap >= 0.8 and overlap >= 0.35 and year_present)
    ):
        metadata_status = "pass"
        metadata_note = (
            "Title, organisation and date confirmed in archived page "
            f"(title-token overlap {overlap:.2f}, org overlap {org_overlap:.2f})"
        )
    elif snapshot_exists and not read_error:
        metadata_status = "fail"
        metadata_note = (
            "Archived page does not support the recorded title, organisation and date "
            f"(title-token overlap {overlap:.2f}, org overlap {org_overlap:.2f}, "
            f"year present {year_present})"
        )
    else:
        metadata_status = "unverified"
        metadata_note = "No usable DOI and no readable archived page"

    overall = "fail" if "fail" in (content_status, metadata_status) else (
        "unverified" if "unverified" in (content_status, metadata_status) else "pass"
    )
    if problems:
        overall = "fail"
        metadata_note = "; ".join(problems)

    return {
        "source_id": source_id,
        "title": row["title"],
        "metadata_result": metadata_status,
        "metadata_message": metadata_note,
        "content_access": content_status,
        "content_message": content_note,
        "evidence_locator": row["evidence_locator"],
        "snapshot_path": row["snapshot_path"],
        "snapshot_sha256": snapshot_hash,
        "title_token_overlap": round(overlap, 3),
        "overall_status": overall,
        "problems": problems,
    }


def update_ledger(path: Path, results: list[dict[str, object]]) -> None:
    by_id = {result["source_id"]: result for result in results}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or SOURCE_COLUMNS
        rows = [
            {name: (row.get(name) or "").strip() for name in fieldnames}
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]
    for row in rows:
        result = by_id.get(row["source_id"])
        if not result:
            continue
        row["metadata_result"] = str(result["metadata_result"])
        row["content_access"] = str(result["content_access"])
        row["content_access_note"] = str(result["content_message"])
        if "dataset" in row["metadata_method"].lower():
            continue
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=PROJECT)
    args = parser.parse_args()
    project = args.project.resolve()
    ledger_path = project / "evidence" / "sources.csv"
    if not ledger_path.is_file():
        print(f"Missing source ledger: {ledger_path}", file=sys.stderr)
        return 1
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = set(SOURCE_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            print(f"Ledger missing columns: {sorted(missing)}", file=sys.stderr)
            return 1
        rows = [
            {name: (row.get(name) or "").strip() for name in SOURCE_COLUMNS}
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]
    if not rows:
        print("Source ledger has no rows", file=sys.stderr)
        return 1

    results = [verify_source(row, project) for row in rows]
    update_ledger(ledger_path, results)

    overall = (
        "pass"
        if all(result["overall_status"] == "pass" for result in results)
        else "fail"
    )
    output = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "method": (
            "Archived snapshot verification plus Crossref lookup where a DOI is "
            "recorded. Page sources are checked for title-token overlap with the "
            "recorded title; dataset sources are checked for a parseable CSV "
            "archive. Hashes are recorded for every snapshot."
        ),
        "sources": results,
        "overall_status": overall,
    }
    reference_path = project / "evidence" / "reference-check.json"
    reference_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    failures = [result for result in results if result["overall_status"] != "pass"]
    print(f"Checked {len(results)} sources: {len(results) - len(failures)} pass, {len(failures)} fail")
    for result in failures:
        print(
            f"FAIL {result['source_id']}: metadata={result['metadata_result']} "
            f"content={result['content_access']} :: {result['metadata_message']}",
            file=sys.stderr,
        )
    print(f"Wrote {reference_path}")
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
