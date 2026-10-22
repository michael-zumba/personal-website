#!/usr/bin/env python3
"""Build ai_capex.csv from SEC EDGAR XBRL company facts API.

Source: https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
Each value in the API carries the accession number, form type (10-K/10-Q),
fiscal year/period label and filing date of the filing that reported it.

Method
------
1. Download companyfacts JSON for each firm.
2. Select the cash-flow capex concept used by the firm:
   - PaymentsToAcquirePropertyPlantAndEquipment (MSFT, GOOGL, META, ORCL)
   - PaymentsToAcquireProductiveAssets (AMZN, NVDA; their current tag for
     "purchases of property and equipment"). The alternative tag has no entries
     after 2020 for NVDA and after 2017 for AMZN, so it is not the current tag.
3. Deduplicate facts by (start,end), keeping the latest-filed value.
4. Classify each fact by duration and by the fiscal period (fp) of the filing
   that reported it:
   - 12-month facts reported in a 10-K are annual (FY) values.
   - 3-month facts reported in a Q1/Q2/Q3 10-Q are that quarter (directly
     as-filed: Q1, Q2, Q3). Prior-year comparatives carry their own end date
     and are assigned to the earlier fiscal year.
   - 6-month facts (H1) and 9-month facts (9M) are year-to-date figures.
   - Q4 is derived as FY annual minus (Q1+Q2+Q3) from the same fiscal year.
     If a direct 3-month Q4 fact exists it is used instead. A 12-month fact
     reported inside a 10-Q is a trailing-twelve-month figure and is excluded.
5. Fiscal-year labels are computed from each firm's fiscal year end:
   Microsoft (June), NVIDIA (late January) and Oracle (May) have non-calendar
   fiscal years. The label is the calendar year in which the fiscal year ends.

Output: ai_capex.csv (tidy), plus per-company snapshot CSVs written to the
directory given by --snapshot-dir (normally evidence/snapshots/ai/).
"""
import argparse
import csv
import json
import os
import tempfile
import time
import urllib.request
from datetime import date

UA = "Mozilla/5.0"
BASE = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# old_concept is a fallback for annual values only, used where a firm changed
# the XBRL tag it uses for cash capex and earlier 10-K annual values exist only
# under the older tag.
FIRMS = [
    ("MSFT", "0000789019", "Microsoft Corporation", "June", "PaymentsToAcquirePropertyPlantAndEquipment", None),
    ("GOOGL", "0001652044", "Alphabet Inc.", "December", "PaymentsToAcquirePropertyPlantAndEquipment", None),
    ("AMZN", "0001018724", "Amazon.com, Inc.", "December", "PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment"),
    ("META", "0001326801", "Meta Platforms, Inc.", "December", "PaymentsToAcquirePropertyPlantAndEquipment", None),
    ("NVDA", "0001045810", "NVIDIA Corporation", "January", "PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment"),
    ("ORCL", "0001341439", "Oracle Corporation", "May", "PaymentsToAcquirePropertyPlantAndEquipment", None),
]

START_YEAR = 2015            # AI-capital evidence window (annual panel)
QUARTER_FROM = "2019-01-01"  # quarterly panel start

FY_END_MONTH = {"June": 6, "May": 5, "January": 1, "December": 12}


def d(s):
    y, m, dd = map(int, s.split("-"))
    return date(y, m, dd)


def fetch(cik, cache_dir):
    path = os.path.join(cache_dir, f"CIK{cik}.json")
    if os.path.exists(path) and os.path.getsize(path) > 100000:
        return json.load(open(path))
    req = urllib.request.Request(BASE.format(cik=cik),
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    with open(path, "wb") as f:
        f.write(raw)
    time.sleep(0.3)
    return json.loads(raw)


def concept_facts(doc, concept):
    """Return USD facts with start/end, deduplicated to the latest filing."""
    node = doc.get("facts", {}).get("us-gaap", {}).get(concept)
    if not node:
        return []
    rows = {}
    for unit, arr in node["units"].items():
        if unit != "USD":
            continue
        for x in arr:
            if x.get("form") not in ("10-K", "10-Q"):
                continue
            if not x.get("start") or not x.get("end"):
                continue
            key = (x["start"], x["end"])
            prev = rows.get(key)
            if prev is None or x.get("filed", "") >= prev.get("filed", ""):
                rows[key] = x
    return [rows[k] for k in sorted(rows, key=lambda k: (k[1], k[0]))]


def fiscal_label(end, fy_end_month):
    """Fiscal year label = calendar year in which the fiscal year ends.

    If the period ends after the fiscal-year-end month, it belongs to the
    fiscal year ending in the following calendar year (e.g. an Oracle quarter
    ending Aug 2026 belongs to the fiscal year ending May 2027 = FY2027).
    """
    e = d(end)
    m = FY_END_MONTH[fy_end_month]
    return e.year + 1 if e.month > m else e.year


def duration_type(start, end):
    days = (d(end) - d(start)).days
    if 350 <= days <= 380:
        return "12M"
    if 255 <= days <= 295:
        return "9M"
    if 165 <= days <= 200:
        return "6M"
    if 80 <= days <= 100:
        return "3M"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ai_capex.csv")
    ap.add_argument("--snapshot-dir", default=None)
    ap.add_argument("--cache-dir", default=None)
    args = ap.parse_args()

    cache_dir = args.cache_dir or tempfile.mkdtemp(prefix="sec_facts_")
    os.makedirs(cache_dir, exist_ok=True)
    if args.snapshot_dir:
        os.makedirs(args.snapshot_dir, exist_ok=True)

    out_rows = []
    summary = []
    for tk, cik, name, fy_end, concept, old_concept in FIRMS:
        doc = fetch(cik, cache_dir)
        facts = concept_facts(doc, concept)
        old_facts = concept_facts(doc, old_concept) if old_concept else []

        # Snapshot: full transcription of the concept facts with provenance.
        if args.snapshot_dir:
            snap = os.path.join(args.snapshot_dir, f"S_AI_SEC_{tk}_20261022.csv")
            with open(snap, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["cik", "company", "concept", "form", "fy", "fp", "start", "end",
                            "duration_days", "value_usd", "accession", "filed", "frame"])
                for conc, fact_list in [(concept, facts), (old_concept, old_facts)]:
                    if not conc:
                        continue
                    for x in fact_list:
                        w.writerow([cik, name, conc, x.get("form"), x.get("fy"), x.get("fp"),
                                    x.get("start"), x.get("end"),
                                    (d(x["end"]) - d(x["start"])).days, x.get("val"),
                                    x.get("accn"), x.get("filed"), x.get("frame", "")])

        annual = {}      # (fy, end) -> fact (10-K 12-month only)
        quarters = {}    # (fy, Qn) -> (fact, note, value)
        ytd = {}         # (fy, 'H1'|'9M') -> fact
        for x in facts:
            kind = duration_type(x["start"], x["end"])
            if kind is None:
                continue
            fy = fiscal_label(x["end"], fy_end)
            fp = (x.get("fp") or "").upper()
            form = x.get("form")
            if kind == "12M":
                if form == "10-K" and fp == "FY":
                    annual[(fy, x["end"])] = x
                # 12M facts tagged inside a 10-Q are trailing-twelve-month
                # figures, not annual results; excluded.
            elif kind == "3M":
                if fp in ("Q1", "Q2", "Q3"):
                    quarters[(fy, fp)] = (x, f"as-filed 3-month {fp} value", x["val"])
                elif fp == "Q4" and form == "10-K":
                    quarters[(fy, "Q4")] = (x, "as-filed 3-month Q4 value (10-K)", x["val"])
            elif kind in ("6M", "9M"):
                ytd[(fy, "H1" if kind == "6M" else "9M")] = x

        # Fallbacks: derive missing quarters from the YTD ladder / annual total.
        for fy in {k[0] for k in list(quarters) + list(ytd) + list(annual)}:
            if (fy, "Q2") not in quarters and (fy, "H1") in ytd and (fy, "Q1") in quarters:
                h1, q1 = ytd[(fy, "H1")], quarters[(fy, "Q1")][0]
                if d(h1["end"]) > d(q1["end"]):
                    quarters[(fy, "Q2")] = (h1, "derived: H1 YTD minus Q1 3-month",
                                            h1["val"] - q1["val"])
            if (fy, "Q3") not in quarters and (fy, "9M") in ytd and (fy, "H1") in ytd:
                nine, h1 = ytd[(fy, "9M")], ytd[(fy, "H1")]
                if d(nine["end"]) > d(h1["end"]):
                    quarters[(fy, "Q3")] = (nine, "derived: 9M YTD minus H1 YTD",
                                            nine["val"] - h1["val"])
            if (fy, "Q4") not in quarters and any(yy == fy for yy, _ in annual):
                fyf = next(v for (yy, _), v in annual.items() if yy == fy)
                if all((fy, q) in quarters for q in ("Q1", "Q2", "Q3")):
                    s = sum(quarters[(fy, q)][2] for q in ("Q1", "Q2", "Q3"))
                    quarters[(fy, "Q4")] = (fyf,
                                            "derived: FY annual minus sum of Q1-Q3 3-month values",
                                            fyf["val"] - s)
                elif (fy, "9M") in ytd:
                    quarters[(fy, "Q4")] = (fyf, "derived: FY annual minus 9M YTD",
                                            fyf["val"] - ytd[(fy, "9M")]["val"])

        # Fallback: annual values from the older tag where the current tag has
        # no 10-K annual value for that fiscal year (firms that switched tags).
        if old_facts:
            for x in old_facts:
                kind = duration_type(x["start"], x["end"])
                fy = fiscal_label(x["end"], fy_end)
                if kind == "12M" and x.get("form") == "10-K" and (x.get("fp") or "").upper() == "FY":
                    if not any(yy == fy for yy, _ in annual):
                        x = dict(x, note_tag=old_concept)
                        annual[(fy, x["end"])] = x

        # Annual rows
        for (fy, end), x in sorted(annual.items(), key=lambda kv: kv[0][1]):
            if int(end[:4]) < START_YEAR:
                continue
            out_rows.append(dict(period_start=x["start"], period_end=end, period_type="annual",
                                 fiscal_year=fy, fiscal_period="FY", company=name, ticker=tk,
                                 metric="cash capex (purchases of PP&E)", value_usd=x["val"],
                                 source_id=f"S_AI_SEC_{tk}", filing_form=x["form"],
                                 accession=x.get("accn"),
                                 note=("as-filed 10-K annual value (older XBRL tag "
                                       + x["note_tag"] + ")") if x.get("note_tag")
                                      else "as-filed 10-K annual value"))

        # Quarterly rows (Q1-Q4 only; YTD helper facts are not emitted)
        for (fy, q), (x, note, val) in sorted(quarters.items(),
                                              key=lambda kv: (kv[1][0]["end"], kv[0][1])):
            if x["end"] < QUARTER_FROM:
                continue
            out_rows.append(dict(period_start=x["start"], period_end=x["end"], period_type="quarterly",
                                 fiscal_year=fy, fiscal_period=q, company=name, ticker=tk,
                                 metric="cash capex (purchases of PP&E)", value_usd=val,
                                 source_id=f"S_AI_SEC_{tk}", filing_form=x["form"],
                                 accession=x.get("accn"), note=note))

        latest = max(annual.items(), key=lambda kv: kv[0][1]) if annual else None
        if latest:
            summary.append((tk, name, latest[0][0], latest[1]["val"] / 1e9, latest[1]["end"]))

    out_rows.sort(key=lambda r: (r["period_end"], r["ticker"], r["period_type"], r["fiscal_period"]))
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["period_start", "period_end", "period_type", "fiscal_year",
                                          "fiscal_period", "ticker", "company", "metric", "value_usd",
                                          "source_id", "filing_form", "accession", "note"])
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"wrote {args.out}: {len(out_rows)} rows")
    print("\nLatest annual as-filed cash capex per firm:")
    for tk, name, fy, val, end in summary:
        print(f"  {tk:6s} FY{fy} ending {end}: {val:8.3f} USD bn")
    from collections import Counter
    print("\nrows per firm:", dict(Counter(r["ticker"] for r in out_rows)))


if __name__ == "__main__":
    main()
