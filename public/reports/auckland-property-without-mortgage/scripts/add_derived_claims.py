#!/usr/bin/env python3
"""Add author-calculation claims for numbers derived in the report.

These are reproducible calculations from verified inputs (or calculations that
combine a verified input with a clearly labelled assumption). They are appended
to the project claim ledger once, so every headline number in the report has a
claim row with source, locator, dataset and computation.

Author: Dr Yuqian Zhang
Date: 2026-10-22
"""

from __future__ import annotations

import csv
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
CLAIMS = PROJECT / "evidence" / "claims.csv"

COLUMNS = [
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

ROWS = [
    {
        "claim_id": "C_DERIVED_001",
        "claim_text": "Big-four hyperscaler cash capex summed across Microsoft, Alphabet, Amazon and Meta was 23.0 billion US dollars in fiscal 2015 and 357.5 billion in fiscal 2025.",
        "normalized_value": "357.5",
        "unit": "USD billion",
        "comparison_type": "level",
        "source_id": "S_AI_SEC_MSFT",
        "exact_locator": "SEC XBRL company facts, us-gaap:PaymentsToAcquirePropertyPlantAndEquipment; annual values for FY2015 and FY2025 summed for four firms",
        "dataset": "data/ai_capital_cycle.csv",
        "computation": "sum of annual cash capex for MSFT, GOOGL, AMZN and META; fiscal-year endpoints differ",
        "verification_status": "pass",
        "report_location": "Findings 5.6 and Figure 5",
        "summary_location": "",
    },
    {
        "claim_id": "C_DERIVED_002",
        "claim_text": "Provisional net migration for the June 2026 year was 17,600 persons.",
        "normalized_value": "17600",
        "unit": "persons",
        "comparison_type": "level",
        "source_id": "S_AI_STATSNZ_MIGRATION",
        "exact_locator": "Stats NZ international migration, June 2026 year, key facts",
        "dataset": "data/nz_transmission.csv",
        "computation": "published provisional estimate; plus or minus 1,500",
        "verification_status": "pass",
        "report_location": "Background and Findings 5.6",
        "summary_location": "",
    },
    {
        "claim_id": "C_DERIVED_003",
        "claim_text": "The annualised real return on Auckland housing from September 2007 to September 2026 was 1.29 percent a year.",
        "normalized_value": "1.29",
        "unit": "percent a year",
        "comparison_type": "annualised change",
        "source_id": "S_PRICE_QV_HPI_API",
        "exact_locator": "QV HPI September 2007 and September 2026; Stats NZ CPI same quarters",
        "dataset": "data/real_returns.csv",
        "computation": "((1 + real total return) ^ (1 / 19) - 1) x 100; real total 27.50 percent",
        "verification_status": "pass",
        "report_location": "Executive Summary and Findings 5.1",
        "summary_location": "Key Findings",
    },
    {
        "claim_id": "C_DERIVED_004",
        "claim_text": "The price-to-income ratio was 10.70 in 2023 using the IDI median gross household income denominator.",
        "normalized_value": "10.70",
        "unit": "ratio",
        "comparison_type": "ratio",
        "source_id": "S_PRICE_QV_HPI_API",
        "exact_locator": "QV average equalised value September 2023 and Auckland Council IDI median household income 2023",
        "dataset": "data/affordability_yield.csv",
        "computation": "1,261,919 / 117,900",
        "verification_status": "pass",
        "report_location": "Findings 5.2 and Figure 2",
        "summary_location": "",
    },
    {
        "claim_id": "C_DERIVED_005",
        "claim_text": "Gross rent avoided on the average equalised Auckland dwelling was 33,800 dollars a year, 2.92 percent of value.",
        "normalized_value": "33800",
        "unit": "NZD per year",
        "comparison_type": "level",
        "source_id": "S_PRICE_MBIE_BOND_REGION",
        "exact_locator": "MBIE Auckland median weekly rent, August 2026, 650 dollars; QV average equalised value September 2026",
        "dataset": "data/housing_user_cost.csv",
        "computation": "650 x 52 = 33,800; 33,800 / 1,159,440 = 2.92 percent",
        "verification_status": "pass",
        "report_location": "Discussion 6.1",
        "summary_location": "",
    },
    {
        "claim_id": "C_DERIVED_006",
        "claim_text": "Net shelter return is about 1.42 percent of value a year, after assumed ownership costs of 1.50 percent of value.",
        "normalized_value": "1.42",
        "unit": "percent of value",
        "comparison_type": "difference",
        "source_id": "S_PRICE_QV_HPI_API",
        "exact_locator": "Gross yield 2.92 percent; ownership-cost assumptions in data/housing_user_cost.csv",
        "dataset": "data/housing_user_cost.csv",
        "computation": "2.92 percent gross yield minus 1.50 percent assumed costs (rates 0.35, insurance 0.30, maintenance 0.85)",
        "verification_status": "pass",
        "report_location": "Discussion 6.1",
        "summary_location": "",
    },
    {
        "claim_id": "C_DERIVED_007",
        "claim_text": "A one-year term deposit at 4.02 percent returns 2.69 percent after 33 percent tax and minus 0.97 percent in real terms at 3.7 percent inflation.",
        "normalized_value": "-0.97",
        "unit": "percent a year",
        "comparison_type": "real change",
        "source_id": "S_CASH_003",
        "exact_locator": "RBNZ B26 one-year term deposit rate September 2026; Stats NZ CPI September 2026 quarter; IRD 33 percent rate",
        "dataset": "data/housing_user_cost.csv",
        "computation": "((1 + 4.02 x (1 - 0.33)) / (1 + 0.037) - 1) x 100",
        "verification_status": "pass",
        "report_location": "Executive Summary and Discussion 6.4",
        "summary_location": "Key Statistics",
    },
    {
        "claim_id": "C_DERIVED_008",
        "claim_text": "The owning-versus-renting real-return hurdle is about minus 2.39 percent a year at the current cash return, before transaction costs.",
        "normalized_value": "-2.39",
        "unit": "percent a year",
        "comparison_type": "difference",
        "source_id": "S_CASH_002",
        "exact_locator": "Cash real return minus 0.97 percent; net shelter return 1.42 percent; data/housing_user_cost.csv",
        "dataset": "data/housing_user_cost.csv",
        "computation": "minus 0.97 minus 1.42",
        "verification_status": "pass",
        "report_location": "Discussion 6.1",
        "summary_location": "The Six Rules for a Cash Buyer",
    },
    {
        "claim_id": "C_DERIVED_009",
        "claim_text": "New Zealand real house prices fell 15.69 percent in the Global Financial Crisis and rose 8.70 percent through the dot-com bust.",
        "normalized_value": "15.69",
        "unit": "percent",
        "comparison_type": "peak-to-trough change",
        "source_id": "S_AI_BIS_SPP",
        "exact_locator": "BIS WS_SPP, New Zealand real residential property prices, 2007-Q2 to 2011-Q2 and 2000-Q1 to 2002-Q4",
        "dataset": "data/nz_transmission.csv",
        "computation": "published BIS real house price index changes",
        "verification_status": "pass",
        "report_location": "Executive Summary and Discussion 6.3",
        "summary_location": "",
    },
]


def main() -> None:
    with CLAIMS.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or COLUMNS
    existing = {row["claim_id"] for row in rows}
    added = 0
    for row in ROWS:
        if row["claim_id"] in existing:
            continue
        rows.append({name: row.get(name, "") for name in fieldnames})
        added += 1
    with CLAIMS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Added {added} derived claims; {len(rows)} claims total.")


if __name__ == "__main__":
    main()
