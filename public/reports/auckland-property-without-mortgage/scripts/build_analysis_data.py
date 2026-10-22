#!/usr/bin/env python3
"""Build the canonical analysis datasets for the research brief.

Reads the verified raw evidence streams under data/raw/ and writes the tidy
datasets used by the report, by scripts/replicate.py and by the figure ledger.

Author: Dr Yuqian Zhang
Date: 2026-10-22
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
RAW = PROJECT / "data" / "raw"
OUT = PROJECT / "data"

TITLE = "Auckland Property, Cash and the AI Bubble"


def read(relative: str) -> pd.DataFrame:
    return pd.read_csv(RAW / relative)


def write(frame: pd.DataFrame, name: str, columns: list[str] | None = None) -> None:
    if columns:
        frame = frame[columns]
    frame.to_csv(OUT / name, index=False, float_format="%.6g")
    print(f"wrote {name}: {len(frame)} rows")


# ---------------------------------------------------------------------------
# 1. Auckland price index (monthly nominal, CPI-deflated real)
# ---------------------------------------------------------------------------
def build_price_index() -> pd.DataFrame:
    price = read("price/auckland_qv_hpi.csv")
    cpi = read("price/national_cpi.csv")
    cpi["quarter"] = pd.PeriodIndex(cpi["period"], freq="Q")
    cpi_map = cpi.set_index("quarter")["cpi_index_all_groups_base_jun2017_1000"]

    price["month_dt"] = pd.to_datetime(price["month"])
    price["quarter"] = price["month_dt"].dt.to_period("Q")
    price["cpi_index"] = price["quarter"].map(cpi_map)
    price["nominal_index"] = price["qv_hpi_index_base_2007_01_1000"]
    price["real_index"] = price["nominal_index"] / price["cpi_index"] * 1000

    nominal_peak = price["nominal_index"].max()
    real_peak = price["real_index"].max()
    price["pct_from_nominal_peak"] = (price["nominal_index"] / nominal_peak - 1) * 100
    price["pct_from_real_peak"] = (price["real_index"] / real_peak - 1) * 100

    frame = price.rename(
        columns={
            "month": "month",
            "qv_avg_equalised_value_nzd": "average_equalised_value_nzd",
        }
    )
    columns = [
        "month",
        "nominal_index",
        "average_equalised_value_nzd",
        "cpi_index",
        "real_index",
        "pct_from_nominal_peak",
        "pct_from_real_peak",
        "source_id",
    ]
    write(frame, "auckland_price_index.csv", columns)
    return frame


# ---------------------------------------------------------------------------
# 2. Affordability, rent and gross yield
# ---------------------------------------------------------------------------
def build_affordability() -> pd.DataFrame:
    derived = read("price/derived_affordability_yield.csv")
    derived["year"] = derived["period"].astype(str).str[:4].astype(int)
    yields = (
        derived[derived["gross_yield_pct"].notna()]
        .set_index("year")[["qv_avg_equalised_value_nzd", "mbie_bond_auckland_weekly_rent_nzd", "gross_yield_pct", "source_ids"]]
        .rename(columns={"source_ids": "yield_source_ids"})
    )
    ratios = (
        derived[derived["price_to_income_ratio"].notna()]
        .set_index("year")[["median_household_income_nzd", "price_to_income_ratio", "source_ids"]]
        .rename(columns={"source_ids": "income_source_ids"})
    )
    frame = yields.join(ratios, how="outer").sort_index().reset_index()
    frame["income_concept"] = ""
    frame.loc[frame["median_household_income_nzd"].notna(), "income_concept"] = (
        "median gross household income, Auckland region"
    )
    frame["note"] = (
        "Gross yield = (median weekly rent for new bonds x 52) / average equalised value. "
        "Price-to-income = average equalised value / median gross household income. "
        "Income and yield rows come from different releases; see evidence ledger."
    )
    columns = [
        "year",
        "qv_avg_equalised_value_nzd",
        "mbie_bond_auckland_weekly_rent_nzd",
        "gross_yield_pct",
        "median_household_income_nzd",
        "price_to_income_ratio",
        "income_concept",
        "yield_source_ids",
        "income_source_ids",
        "note",
    ]
    write(frame, "affordability_yield.csv", columns)
    return frame


# ---------------------------------------------------------------------------
# 3. Real returns by holding window
# ---------------------------------------------------------------------------
def build_real_returns(price_index: pd.DataFrame) -> pd.DataFrame:
    series = price_index.copy()
    series["month_dt"] = pd.to_datetime(series["month"])
    nominal = series.set_index("month_dt")["nominal_index"]
    real = series.set_index("month_dt")["real_index"]
    cpi = series.set_index("month_dt")["cpi_index"]

    cash = read("cash/cash_returns.csv")
    cash["month_dt"] = pd.to_datetime(cash["month"])
    cash = cash.set_index("month_dt")["real_after_tax_33_6m_pct"]

    windows = [
        ("19 years, 2007-2026", "2007-09-01", "2026-09-01", 19.0, "Longest available QV window"),
        ("15 years, post-GFC", "2011-09-01", "2026-09-01", 15.0, "From the post-GFC trough year"),
        ("10 years", "2016-09-01", "2026-09-01", 10.0, "Ten-year window"),
        ("5 years", "2021-09-01", "2026-09-01", 5.0, "Five-year window through the downturn"),
        ("Peak to 2026", "2022-01-01", "2026-09-01", 4.67, "Nominal peak to latest month"),
        ("GFC drop", "2007-09-01", "2009-02-01", 1.42, "Auckland nominal peak to GFC trough"),
    ]
    round_trip_cost = 5.0
    rows = []
    for label, start, end, years, note in windows:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        nominal_total = (nominal.loc[end_ts] / nominal.loc[start_ts] - 1) * 100
        real_total = (real.loc[end_ts] / real.loc[start_ts] - 1) * 100
        real_annualised = ((1 + real_total / 100) ** (1 / years) - 1) * 100
        net_real_total = ((1 + real_total / 100) * (1 - round_trip_cost / 100) - 1) * 100
        net_real_annualised = ((1 + net_real_total / 100) ** (1 / years) - 1) * 100
        cash_window = cash.loc[start_ts:end_ts]
        cash_real = cash_window.mean() if len(cash_window) else float("nan")
        cpi_total = (cpi.loc[end_ts] / cpi.loc[start_ts] - 1) * 100
        rows.append(
            {
                "window": label,
                "start": start,
                "end": end,
                "years": years,
                "housing_nominal_total_pct": nominal_total,
                "housing_real_total_pct": real_total,
                "housing_real_annualised_pct": real_annualised,
                "round_trip_cost_pct": round_trip_cost,
                "housing_net_real_total_pct": net_real_total,
                "housing_net_real_annualised_pct": net_real_annualised,
                "cash_real_annualised_pct": cash_real,
                "cpi_total_pct": cpi_total,
                "note": note,
            }
        )
    frame = pd.DataFrame(rows)
    frame["source_ids"] = "S_PRICE_QV_HPI_API;S_PRICE_STATS_CPI_SERIES;S_CASH_002;S_CASH_004"
    columns = [
        "window",
        "start",
        "end",
        "years",
        "housing_nominal_total_pct",
        "housing_real_total_pct",
        "housing_real_annualised_pct",
        "round_trip_cost_pct",
        "housing_net_real_total_pct",
        "housing_net_real_annualised_pct",
        "cash_real_annualised_pct",
        "cpi_total_pct",
        "source_ids",
        "note",
    ]
    write(frame, "real_returns.csv", columns)
    return frame


# ---------------------------------------------------------------------------
# 4. Ownership by age and Auckland household tenure
# ---------------------------------------------------------------------------
def build_ownership() -> pd.DataFrame:
    ownership = read("census/ownership_by_age.csv")
    age_bands = ["25-29", "30-34", "35-39", "40-44"]
    holder = ownership[
        (ownership["measure"] == "individual_home_ownership_tenure_holder")
        & (ownership["geography"] == "New Zealand")
        & (ownership["census_year"].isin([2006, 2013]))
        & (ownership["age_band"].isin(age_bands))
    ].copy()
    holder["measure_used"] = "individual home ownership (tenure holder)"
    individual = ownership[
        (ownership["measure"] == "individual_home_ownership")
        & (ownership["geography"] == "New Zealand")
        & (ownership["census_year"].isin([2018, 2023]))
        & (ownership["age_band"].isin(age_bands))
    ].copy()
    individual["measure_used"] = "individual home ownership"
    auckland = ownership[
        (ownership["measure"] == "household_tenure")
        & (ownership["geography"] == "Auckland Region")
    ].copy()
    auckland["age_band"] = "Total"
    auckland["measure_used"] = "household tenure (Auckland region)"

    combined = pd.concat([holder, individual, auckland], ignore_index=True)
    combined = combined[
        [
            "census_year",
            "geography",
            "age_band",
            "measure_used",
            "tenure_status",
            "rate_percent",
            "source_id",
            "notes",
        ]
    ].rename(columns={"notes": "note"})
    combined = combined.sort_values(["geography", "age_band", "census_year"])
    write(combined, "ownership_cohorts.csv")
    return combined


# ---------------------------------------------------------------------------
# 5. Migration
# ---------------------------------------------------------------------------
def build_migration() -> pd.DataFrame:
    migration = read("census/migration.csv")
    rolling = migration[migration["period_type"] == "rolling_year_ended"].copy()
    pivot = rolling.pivot_table(
        index=["period", "status", "geography", "source_id"],
        columns="measure",
        values="value",
        aggfunc="first",
    ).reset_index()
    pivot["year_ended"] = pd.to_datetime(pivot["period"], format="%b-%Y")
    pivot = pivot.sort_values("year_ended")
    pivot["net_migration"] = pivot["net_migration"].astype("Int64")
    frame = pivot.rename(columns={"period": "period_label"})
    columns = [
        "year_ended",
        "period_label",
        "status",
        "geography",
        "migrant_arrivals",
        "migrant_departures",
        "net_migration",
        "source_id",
    ]
    write(frame, "migration.csv", columns)
    return frame


# ---------------------------------------------------------------------------
# 6. Cash returns
# ---------------------------------------------------------------------------
def build_cash() -> pd.DataFrame:
    cash = read("cash/cash_returns.csv")
    frame = cash[
        [
            "month",
            "td_6m_pct",
            "cpi_yoy_pct",
            "real_pre_tax_6m_pct",
            "real_after_tax_175_6m_pct",
            "real_after_tax_30_6m_pct",
            "real_after_tax_33_6m_pct",
            "real_after_tax_39_6m_pct",
            "source_id",
        ]
    ].rename(columns={"source_id": "source_ids"})
    write(frame, "cash_returns.csv")
    return frame


# ---------------------------------------------------------------------------
# 7. Credit and household stress indicators
# ---------------------------------------------------------------------------
def build_credit_stress() -> pd.DataFrame:
    rates = read("credit/mortgage_rates.csv")
    rates["quarter"] = pd.PeriodIndex(
        pd.to_datetime(rates["month"]).dt.to_period("Q").astype(str), freq="Q"
    )
    rates = rates.groupby("quarter").agg(
        mortgage_2yr_pct=("two_year_standard_b20_percent", "last"),
        mortgage_floating_pct=("floating_standard_b20_percent", "last"),
        ocr_pct=("ocr_percent", "last"),
    )
    debt = read("credit/household_debt.csv")
    debt["quarter"] = pd.PeriodIndex(debt["quarter"], freq="Q")
    debt = debt.set_index("quarter")[
        [
            "debt_to_disposable_income_percent",
            "interest_payments_percent_of_disposable_income",
            "investor_share_new_mortgage_lending_percent",
        ]
    ]
    bank = read("credit/arrears_bank.csv")
    bank["quarter"] = pd.PeriodIndex(bank["quarter"], freq="Q")
    bank = bank.set_index("quarter")[
        [
            "housing_npl_ratio_percent",
            "housing_npl_ratio_longrun_percent",
            "tier1_capital_ratio_percent",
            "core_funding_ratio_percent",
            "offshore_funding_share_percent",
        ]
    ]
    frame = rates.join(debt, how="outer").join(bank, how="outer").sort_index()
    frame = frame.loc[pd.Period("2008Q4") :].reset_index()
    frame["quarter"] = frame["quarter"].astype(str)
    frame["source_ids"] = (
        "S_CREDIT_RBNZ_B20_20261022;S_CREDIT_RBNZ_C21_20261022;"
        "S_CREDIT_RBNZ_C22_20261022;S_CREDIT_RBNZ_C31_20261022;"
        "S_CREDIT_RBNZ_S50_20261022;S_CREDIT_RBNZ_S20_20261022;"
        "S_CREDIT_RBNZ_L2_20261022;S_CREDIT_RBNZ_L3_20261022"
    )
    write(frame, "credit_stress.csv")
    return frame


# ---------------------------------------------------------------------------
# 7b. Policy timeline
# ---------------------------------------------------------------------------
def build_policy() -> pd.DataFrame:
    policy = read("credit/policy_timeline.csv")
    frame = policy[
        ["date", "policy_name", "setting_value", "expected_direction", "source_id", "exact_locator"]
    ].rename(columns={"expected_direction": "labelled_expectation"})
    write(frame, "policy_timeline.csv")
    return frame


# ---------------------------------------------------------------------------
# 8. AI capital cycle
# ---------------------------------------------------------------------------
def build_ai_cycle() -> pd.DataFrame:
    capex = read("ai/ai_capex.csv")
    capex["period_end"] = pd.to_datetime(capex["period_end"])
    quarterly = capex[capex["period_type"] == "quarterly"].copy()
    quarterly["year"] = quarterly["period_end"].dt.year
    annual = capex[capex["period_type"] == "annual"].copy()
    annual["year"] = annual["period_end"].dt.year

    big_four = ["MSFT", "GOOGL", "AMZN", "META"]
    annual_fy = (
        annual[annual["ticker"].isin(big_four)]
        .groupby("year")["value_usd"]
        .sum()
        .reset_index()
    )
    annual_fy = annual_fy[annual_fy["year"].between(2015, 2025)]
    quarterly_fy = (
        quarterly[quarterly["ticker"].isin(big_four)]
        .groupby("year")["value_usd"]
        .sum()
        .reset_index()
    )
    quarterly_fy = quarterly_fy[quarterly_fy["year"].between(2019, 2025)]

    rows = []
    for _, row in annual_fy.iterrows():
        rows.append(
            {
                "panel": "AI capital expenditure",
                "period": str(int(row["year"])),
                "series": "Big four hyperscaler capex, fiscal year",
                "value": round(row["value_usd"] / 1e9, 1),
                "unit": "USD billion",
                "source_id": "S_AI_SEC_MSFT;S_AI_SEC_GOOGL;S_AI_SEC_AMZN;S_AI_SEC_META",
            }
        )
    for _, row in quarterly_fy.iterrows():
        rows.append(
            {
                "panel": "AI capital expenditure",
                "period": f"{int(row['year'])} (calendar quarters)",
                "series": "Big four hyperscaler capex, calendar-year sum",
                "value": round(row["value_usd"] / 1e9, 1),
                "unit": "USD billion",
                "source_id": "S_AI_SEC_MSFT;S_AI_SEC_GOOGL;S_AI_SEC_AMZN;S_AI_SEC_META",
            }
        )

    concentration = read("ai/market_concentration.csv")
    for _, row in concentration.iterrows():
        rows.append(
            {
                "panel": "Valuation and concentration",
                "period": str(row["period"]),
                "series": str(row["indicator"]),
                "value": row["value"],
                "unit": str(row["unit"]),
                "source_id": str(row["source_id"]),
            }
        )

    credit = read("ai/ai_credit.csv")

    def credit_label(indicator: str) -> str:
        text = str(indicator).lower()
        if "private credit share of ai investment" in text and "2024" in text:
            return "private credit share of AI investment, 2024"
        if "private credit share of ai investment" in text and "2025" in text:
            return "private credit share of AI investment, 2025"
        if "non-refinance us high-yield issuance" in text:
            return "AI issuers' share of non-refinance US high-yield issuance, 2026 to date"
        if "jpm us high-yield bond index" in text:
            return "AI issuers' share of JPM US high-yield bond index, end-2025"
        if "us ig debt issuance" in text:
            return "Five AI hyperscalers' share of US IG debt issuance, 2026"
        if "outstanding us ig debt" in text:
            return "Five AI hyperscalers' share of outstanding US IG debt, end-2025"
        return ""

    for _, row in credit.iterrows():
        label = credit_label(row["indicator"])
        if label:
            rows.append(
                {
                    "panel": "AI-related credit",
                    "period": str(row["date"]),
                    "series": label,
                    "value": row["value"],
                    "unit": str(row["unit"]),
                    "source_id": str(row["source_id"]),
                }
            )
    imf = credit[credit["indicator"].str.contains("Projected AI-related capital expenditure")]
    for _, row in imf.iterrows():
        rows.append(
            {
                "panel": "AI-related credit",
                "period": "2025-2029",
                "series": "IMF projected AI capex",
                "value": row["value"],
                "unit": str(row["unit"]),
                "source_id": str(row["source_id"]),
            }
        )

    frame = pd.DataFrame(rows)
    write(frame, "ai_capital_cycle.csv")
    return frame


# ---------------------------------------------------------------------------
# 9. NZ transmission indicators
# ---------------------------------------------------------------------------
def build_transmission() -> pd.DataFrame:
    raw = read("ai/nz_transmission.csv")
    frame = raw[["period", "indicator", "value", "unit", "change", "source_id", "note"]].copy()
    write(frame, "nz_transmission.csv")
    return frame


# ---------------------------------------------------------------------------
# 10. Stress anchors
# ---------------------------------------------------------------------------
def build_stress_anchors() -> pd.DataFrame:
    stress = read("cash/stress_tests.csv")
    keep = [
        "RBNZ 2025 solvency stress test",
        "2020 COVID-19 Very Severe Scenario",
        "2024 Reverse Stress Test",
        "IMF FSAP 2017",
    ]
    rows = []
    for _, row in stress.iterrows():
        label = str(row["test_name"])
        if not any(term in label for term in keep):
            continue
        rows.append(
            {
                "exercise": label,
                "publication_date": str(row["publication_date"]),
                "unemployment_peak_pct": row["unemployment_peak_pct"],
                "house_price_decline_pct": row["house_price_decline_pct"],
                "cpi_peak_pct": row["cpi_peak_pct"],
                "cash_rate_peak_pct": row["cash_rate_peak_pct"],
                "credit_loss_pct": row["cumulative_credit_loss_pct"],
                "capital_result": str(row["capital_result"]),
                "source_id": str(row["source_id"]),
                "note": str(row["notes"]),
            }
        )
    historical = read("cash/historical_episodes.csv")
    for _, row in historical.iterrows():
        variable = str(row["variable"])
        if variable not in {
            "unemployment_rate_peak_pct",
            "cpi_yoy_peak_pct",
            "term_deposit_6m_peak_pct",
            "real_after_tax_33_pct_at_cpi_peak",
        }:
            continue
        rows.append(
            {
                "exercise": f"Historical episode {row['episode']}",
                "publication_date": str(row["period"]),
                "unemployment_peak_pct": row["value"] if variable == "unemployment_rate_peak_pct" else "",
                "house_price_decline_pct": "",
                "cpi_peak_pct": row["value"] if variable == "cpi_yoy_peak_pct" else "",
                "cash_rate_peak_pct": row["value"] if variable == "term_deposit_6m_peak_pct" else "",
                "credit_loss_pct": row["value"] if variable == "real_after_tax_33_pct_at_cpi_peak" else "",
                "capital_result": "",
                "source_id": str(row["source_id"]),
                "note": str(row["notes"]),
            }
        )
    frame = pd.DataFrame(rows)
    write(frame, "stress_anchors.csv")
    return frame


# ---------------------------------------------------------------------------
# 11. Housing user cost (analytical, assumptions stated)
# ---------------------------------------------------------------------------
def build_user_cost(affordability: pd.DataFrame) -> pd.DataFrame:
    latest = affordability.dropna(subset=["gross_yield_pct"]).iloc[-1]
    value = float(latest["qv_avg_equalised_value_nzd"])
    weekly_rent = float(latest["mbie_bond_auckland_weekly_rent_nzd"])
    rent_annual = weekly_rent * 52
    gross_yield = rent_annual / value * 100

    rates_pct = 0.35
    insurance_pct = 0.30
    maintenance_pct = 0.85
    ownership_cost_pct = rates_pct + insurance_pct + maintenance_pct
    net_shelter_pct = gross_yield - ownership_cost_pct
    cash_rate = 4.02
    tax_rate = 33.0
    cash_after_tax = cash_rate * (1 - tax_rate / 100)
    cpi = 3.7
    cash_real = ((1 + cash_after_tax / 100) / (1 + cpi / 100) - 1) * 100
    hurdle_current = cash_real - net_shelter_pct
    hurdle_longrun = 0.46 - net_shelter_pct
    round_trip = 5.0
    rows = [
        ("Average equalised Auckland dwelling value", "QV, September 2026", value, 100.0, "Sourced: QV HPI average equalised value"),
        ("Gross rent avoided (median new bond rent x 52)", "MBIE, August 2026", rent_annual, gross_yield, "Sourced: MBIE bond median rent"),
        ("Gross rental yield", "rent avoided / value", gross_yield, gross_yield, "Sourced ratio"),
        ("Council rates (assumed)", "0.35% of value", value * rates_pct / 100, rates_pct, "Assumption within a 0.25%-0.50% range"),
        ("Dwelling insurance (assumed)", "0.30% of value", value * insurance_pct / 100, insurance_pct, "Assumption within a 0.15%-0.50% range"),
        ("Maintenance and repairs (assumed)", "0.85% of value", value * maintenance_pct / 100, maintenance_pct, "Assumption within a 0.50%-1.50% range"),
        ("Total ownership costs (assumed)", "sum of the three items", value * ownership_cost_pct / 100, ownership_cost_pct, "Analytical assumption, not an observed Auckland series"),
        ("Net shelter return before capital change", "gross yield minus ownership costs", value * net_shelter_pct / 100, net_shelter_pct, "Analytical: rent avoided minus costs, as % of value"),
        ("Cash after tax (1-year term deposit, 33% rate)", "4.02% x (1-0.33)", cash_after_tax, cash_after_tax, "Sourced rate; tax rate sourced"),
        ("Cash real return after tax", "(1+2.69%)/(1+3.7%)-1", cash_real, cash_real, "Current CPI applied; sourced"),
        ("Owning-versus-renting break-even rate, current cash return", "cash real return - net shelter return", hurdle_current, hurdle_current, "Owning wins if real house price growth exceeds this"),
        ("Owning-versus-renting break-even rate, long-run cash return", "0.46% - net shelter return", hurdle_longrun, hurdle_longrun, "Long-run cash real return from 2000-2026 evidence"),
        ("Round-trip transaction cost (assumed)", "2% buy plus 3% sell", round_trip, round_trip, "Assumption; sensitivity 3%-7%"),
    ]
    frame = pd.DataFrame(
        rows,
        columns=["item", "basis", "annual_nzd", "percent_of_value", "assumption_or_source"],
    )
    write(frame, "housing_user_cost.csv")
    return frame


# ---------------------------------------------------------------------------
# 12. Scenario assumptions and outcomes (analytical, labelled)
# ---------------------------------------------------------------------------
def build_scenarios(user_cost: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    net_shelter = float(
        user_cost.loc[
            user_cost["item"] == "Net shelter return before capital change", "percent_of_value"
        ].iloc[0]
    )
    rent_yield = float(
        user_cost.loc[user_cost["item"] == "Gross rent avoided (median new bond rent x 52)", "percent_of_value"].iloc[0]
    )

    scenarios = [
        # id, severity, regime, global equity, AI capex, NZ unemployment, cumulative CPI, nominal Auckland price change, rents, cash rate, deposit access, anchor
        ("A1", "AI correction", "Disinflationary", -25, 0, 5.5, 2.0, -5, 2, 4.5, "Normal", "Dot-com analogue: equity reset, no NZ credit event"),
        ("A2", "AI correction", "Inflationary", -25, 0, 5.5, 5.5, -3, 7, 7.0, "Normal", "Equity reset with currency and energy inflation"),
        ("B1", "AI credit bust", "Disinflationary", -40, -25, 8.5, 1.0, -20, -2, 5.0, "Stressed", "GFC-style credit event without a funding freeze"),
        ("B2", "AI credit bust", "Inflationary", -40, -25, 8.5, 7.0, -12, 10, 9.0, "Stressed", "Credit event plus imported inflation and higher mortgage rates"),
        ("C1", "Systemic AI unwind", "Disinflationary", -65, -60, 15.0, -1.0, -45, -8, 4.0, "Impaired", "Beyond the RBNZ 2020 very severe scenario; deposit access delayed"),
        ("C2", "Systemic AI unwind", "Inflationary", -65, -60, 15.0, 9.0, -25, 15, 11.0, "Impaired", "Systemic funding closure with a currency and inflation crisis"),
        ("R0", "Reference: no unwind", "Reference", 0, 10, 4.5, 2.5, 1.0, 3, 3.5, "Normal", "Base case, not a forecast: prices broadly flat in real terms"),
    ]

    assumption_rows = []
    for sid, severity, regime, equity, capex, unemployment, cpi, price, rents, cash_rate, access, anchor in scenarios:
        for channel, value, unit in (
            ("global_equity_change_pct", equity, "percent"),
            ("ai_capex_change_pct", capex, "percent"),
            ("nz_unemployment_peak_pct", unemployment, "percent"),
            ("cumulative_cpi_change_pct", cpi, "percent"),
            ("auckland_house_price_change_pct", price, "percent"),
            ("rents_change_pct", rents, "percent"),
            ("term_deposit_rate_pct", cash_rate, "percent"),
        ):
            assumption_rows.append(
                {
                    "scenario_id": sid,
                    "severity": severity,
                    "regime": regime,
                    "channel": channel,
                    "assumed_value": value,
                    "unit": unit,
                    "anchor_or_reason": anchor,
                    "uncertainty": "Author judgement, not a forecast; see stress anchors",
                }
            )
        assumption_rows.append(
            {
                "scenario_id": sid,
                "severity": severity,
                "regime": regime,
                "channel": "deposit_access",
                "assumed_value": access,
                "unit": "category",
                "anchor_or_reason": anchor,
                "uncertainty": "Qualitative assumption",
            }
        )
    assumptions = pd.DataFrame(assumption_rows)
    write(assumptions, "scenario_assumptions.csv")

    outcome_rows = []
    for sid, severity, regime, equity, capex, unemployment, cpi, price, rents, cash_rate, access, anchor in scenarios:
        cpi_factor = 1 + cpi / 100
        house_real = ((1 + price / 100) / cpi_factor - 1) * 100
        cash_after_tax = cash_rate * 0.67
        cash_real = ((1 + cash_after_tax / 100) / cpi_factor - 1) * 100
        owner_two_year = house_real + net_shelter * 2
        renter_two_year = cash_real * 2 - rent_yield * 0
        # Renter total return over two years: cash real return, with rent paid from income.
        renter_two_year = cash_real * 2
        verdict = "Owning better" if owner_two_year > renter_two_year else "Renting and cash better"
        outcome_rows.append(
            {
                "scenario_id": sid,
                "severity": severity,
                "regime": regime,
                "global_equity_change_pct": equity,
                "auckland_nominal_price_change_pct": price,
                "auckland_real_price_change_pct": house_real,
                "cumulative_cpi_change_pct": cpi,
                "unemployment_peak_pct": unemployment,
                "cash_after_tax_real_change_pct": cash_real,
                "owner_real_position_change_pct": owner_two_year,
                "renter_cash_real_return_pct": renter_two_year,
                "two_year_verdict": verdict,
                "deposit_access": access,
                "note": anchor,
            }
        )
    outcomes = pd.DataFrame(outcome_rows)
    write(outcomes, "scenario_outcomes.csv")
    return assumptions, outcomes


# ---------------------------------------------------------------------------
# 13. Transmission map and decision tests
# ---------------------------------------------------------------------------
def build_transmission_map() -> pd.DataFrame:
    rows = [
        ("Global equity and AI valuation reset", "NZ household wealth via KiwiSaver and Super Fund", "Indirect", "KiwiSaver $138.8b; Super Fund 57% listed equities", "Wealth effect on spending and housing confidence, not a direct house-price channel"),
        ("AI capital expenditure reversal", "NZ exports, terms of trade, growth", "Indirect", "NZ is a small open economy; AI capex is not a large direct NZ export", "Second-round demand effects"),
        ("AI-related credit losses", "Global bank and private-credit funding costs", "Direct for funding, indirect for housing", "NZ banks fund offshore; core funding ratio 89.5%", "Transmission via wholesale spreads and deposit competition"),
        ("Global funding market closure", "NZ bank offshore funding rollover", "Direct", "Offshore funding about 16.5% of total funding", "Mortgage repricing and credit rationing"),
        ("NZ unemployment", "Household arrears and forced sales", "Direct", "Mortgage NPL 0.56% in 2026; capacity to absorb", "The main domestic amplification channel"),
        ("Migration and exchange rate", "Auckland rents and demand", "Direct", "Net migration +20,500 in the year to August 2026; peak +133,700", "A migration reversal would weaken rents and prices"),
        ("Official cash rate response", "Mortgage rates and cash returns", "Direct", "OCR 2.75%; 2-year mortgage 5.89%", "The direction depends on the inflation regime"),
        ("Deposit compensation scheme", "Cash safety above $100,000", "Direct", "$100,000 cap per depositor per deposit taker from July 2025", "A failed bank imposes losses above the cap and delays access"),
    ]
    frame = pd.DataFrame(rows, columns=["origin", "transmission", "link_type", "evidence", "note"])
    write(frame, "transmission_channels.csv")
    return frame


def build_decision_tests() -> pd.DataFrame:
    rows = [
        ("Shelter or investment", "Is the purchase mainly a home to live in, or a return-seeking investment?", "Housing user cost and real return tables", "Pass as shelter if the home fits a 10-year living plan", "Fails as an investment if the return depends on capital gain"),
        ("Holding horizon", "Can I hold without selling for at least 10 years?", "Transaction cost and real return windows", "Pass if 10 years or more and cash flows are safe", "Fails if a sale within 5 years is likely"),
        ("Crisis survivability", "Would a 35-50% nominal price fall, a 10-15% unemployment rate and 12-24 months of illiquidity force a sale?", "Scenario matrix and stress anchors", "Pass if the answer is no and reserves cover 2 years of costs", "Fails if the purchase relies on selling or refinancing"),
        ("Real return break-even test", "Is real house price growth likely to exceed the break-even rate over my horizon?", "Housing user cost and real returns", "Pass if expected real growth is above the break-even rate", "Fails if you expect a sustained real decline"),
        ("Cash safety", "Is my cash below $100,000 per depositor per deposit taker and enough for liquidity?", "Deposit protection and cash returns", "Pass if insured, diversified and sufficient", "Fails if all cash sits with one bank or in one asset"),
        ("Liquidity", "Do I keep 12-24 months of spending outside the home?", "Cash and deposit evidence", "Pass if yes", "Fails if all capital goes into the property"),
        ("Alternatives", "Have I compared the home decision with renting plus a diversified portfolio?", "Cash, real returns and user cost", "Pass if the alternative is explicitly costed", "Fails if cash versus house is treated as the only choice"),
        ("Leverage", "If I used a mortgage, would the yield cover the interest?", "Mortgage rates and gross yield", "Not applicable for a cash buyer", "A 2.92% gross yield against a 5.89% mortgage does not cover interest before costs"),
    ]
    frame = pd.DataFrame(rows, columns=["test", "question", "evidence", "pass_condition", "fail_condition"])
    write(frame, "decision_tests.csv")
    return frame


# ---------------------------------------------------------------------------
# 14. Analysis statistics used by the report and summary
# ---------------------------------------------------------------------------
def build_statistics(
    price_index: pd.DataFrame,
    real_returns: pd.DataFrame,
    affordability: pd.DataFrame,
) -> pd.DataFrame:
    latest = price_index.iloc[-1]
    nominal_peak = price_index.loc[price_index["nominal_index"].idxmax()]
    real_peak = price_index.loc[price_index["real_index"].idxmax()]
    window = real_returns.set_index("window")
    latest_aff = affordability.dropna(subset=["gross_yield_pct"]).iloc[-1]
    rows = [
        ("latest_month", str(latest["month"]), "", "QV Auckland HPI"),
        ("nominal_peak_month", str(nominal_peak["month"]), "", "QV nominal peak"),
        ("nominal_peak_index", float(nominal_peak["nominal_index"]), "index", "Jan 2007 = 1000"),
        ("real_peak_month", str(real_peak["month"]), "", "QV real peak"),
        ("nominal_decline_from_peak_pct", float(latest["pct_from_nominal_peak"]), "percent", "Peak to September 2026"),
        ("real_decline_from_peak_pct", float(latest["pct_from_real_peak"]), "percent", "Real peak to September 2026"),
        ("real_5y_total_pct", float(window.loc["5 years", "housing_real_total_pct"]), "percent", ""),
        ("real_10y_total_pct", float(window.loc["10 years", "housing_real_total_pct"]), "percent", ""),
        ("real_15y_total_pct", float(window.loc["15 years, post-GFC", "housing_real_total_pct"]), "percent", ""),
        ("real_19y_total_pct", float(window.loc["19 years, 2007-2026", "housing_real_total_pct"]), "percent", ""),
        ("real_19y_annualised_pct", float(window.loc["19 years, 2007-2026", "housing_real_annualised_pct"]), "percent", ""),
        ("real_5y_annualised_pct", float(window.loc["5 years", "housing_real_annualised_pct"]), "percent", ""),
        ("net_real_19y_annualised_pct", float(window.loc["19 years, 2007-2026", "housing_net_real_annualised_pct"]), "percent", "After 5% round-trip cost"),
        ("cash_longrun_real_after_tax_pct", 0.46, "percent", "2000-2026 mean, 33% tax"),
        ("gross_yield_pct", float(latest_aff["gross_yield_pct"]), "percent", "September 2026"),
        ("price_to_income_2025", 9.14, "ratio", "Average value / median gross household income"),
        ("price_to_income_2023", 10.70, "ratio", "IDI income denominator"),
        ("median_rent_weekly_nzd", float(latest_aff["mbie_bond_auckland_weekly_rent_nzd"]), "NZD per week", "August 2026"),
        ("cpi_latest_index", float(latest["cpi_index"]), "index", "June 2017 quarter = 1000"),
    ]
    frame = pd.DataFrame(rows, columns=["statistic", "value", "unit", "note"])
    frame["value"] = frame["value"].astype(str)
    write(frame, "analysis_statistics.csv")
    return frame


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    price_index = build_price_index()
    affordability = build_affordability()
    real_returns = build_real_returns(price_index)
    build_ownership()
    build_migration()
    build_cash()
    build_credit_stress()
    build_policy()
    build_ai_cycle()
    build_transmission()
    build_stress_anchors()
    user_cost = build_user_cost(affordability)
    build_scenarios(user_cost)
    build_transmission_map()
    build_decision_tests()
    stats = build_statistics(price_index, real_returns, affordability)
    print("\nKey statistics")
    print(stats.to_string(index=False))


if __name__ == "__main__":
    main()
