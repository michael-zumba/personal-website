#!/usr/bin/env python3
"""Reproduce the figures and reported statistics for the research brief.

Reads the published CSV datasets and regenerates all six PNG charts. It prints
the values quoted in the report and the one-page summary so a reader can audit
them without reading the HTML.

Author: Dr Yuqian Zhang
Date: 2026-10-22
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
CHARTS = PROJECT / "charts"

PINE = "#1f4d3f"
PINE_LIGHT = "#6a9c8b"
OCHRE = "#a86b2d"
SLATE = "#60758a"
INK = "#23241f"
MUTED = "#6a685e"
GRID = "#ded8ca"
BG = "#fffdf8"
RED = "#a23b32"

plt.rcParams.update(
    {
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.family": "sans-serif",
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

PCT = FuncFormatter(lambda value, position: f"{value:.0f}%")


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


def ensure_charts_dir() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)


def print_statistics() -> None:
    price = read("auckland_price_index.csv")
    returns = read("real_returns.csv")
    affordability = read("affordability_yield.csv")
    ownership = read("ownership_cohorts.csv")
    ai = read("ai_capital_cycle.csv")
    scenarios = read("scenario_outcomes.csv")
    user_cost = read("housing_user_cost.csv")
    cash = read("cash_returns.csv")

    latest = price.iloc[-1]
    nominal_peak = price.loc[price["nominal_index"].idxmax()]
    real_peak = price.loc[price["real_index"].idxmax()]
    print("=== Price index (QV, non-official) ===")
    print(f"Latest month: {latest['month']}")
    print(f"Nominal peak month: {nominal_peak['month']}")
    print(f"Real peak month: {real_peak['month']}")
    print(f"Nominal decline from peak: {latest['pct_from_nominal_peak']:.2f}%")
    print(f"Real decline from real peak: {latest['pct_from_real_peak']:.2f}%")

    print("=== Real returns by window ===")
    for _, row in returns.iterrows():
        print(
            f"{row['window']}: nominal {row['housing_nominal_total_pct']:.2f}%, "
            f"real {row['housing_real_total_pct']:.2f}%, "
            f"real annualised {row['housing_real_annualised_pct']:.2f}%, "
            f"net real annualised {row['housing_net_real_annualised_pct']:.2f}%, "
            f"cash real annualised {row['cash_real_annualised_pct']:.2f}%"
        )

    print("=== Affordability ===")
    latest_aff = affordability.dropna(subset=["gross_yield_pct"]).iloc[-1]
    print(f"Latest gross yield: {latest_aff['gross_yield_pct']:.2f}%")
    pi = affordability.dropna(subset=["price_to_income_ratio"])
    for _, row in pi.iterrows():
        print(f"Price-to-income {row['year']}: {row['price_to_income_ratio']:.2f}")

    print("=== Ownership ===")
    auckland = ownership[
        (ownership["geography"] == "Auckland Region")
        & (ownership["measure_used"] == "household tenure (Auckland region)")
    ]
    for _, row in auckland.iterrows():
        print(f"Auckland household ownership {row['census_year']}: {row['rate_percent']:.1f}%")

    print("=== AI capital cycle ===")
    capex = ai[(ai["panel"] == "AI capital expenditure") & (ai["series"].str.contains("fiscal year"))]
    if not capex.empty:
        print(f"Big-four capex first year: {capex.iloc[0]['value']:.1f} bn USD")
        print(f"Big-four capex latest year: {capex.iloc[-1]['value']:.1f} bn USD")
    for _, row in ai[ai["panel"] == "Valuation and concentration"].iterrows():
        if "CAPE" in str(row["series"]) or "weight" in str(row["series"]):
            print(f"{row['period']} {row['series']}: {row['value']}")
    for _, row in ai[ai["panel"] == "AI-related credit"].iterrows():
        print(f"{row['period']} {row['series']}: {row['value']}")

    print("=== Scenario outcomes ===")
    for _, row in scenarios.iterrows():
        print(
            f"{row['scenario_id']} ({row['severity']}, {row['regime']}): "
            f"house real {row['auckland_real_price_change_pct']:.2f}%, "
            f"cash real {row['cash_after_tax_real_change_pct']:.2f}%, "
            f"owner {row['owner_real_position_change_pct']:.2f}%, "
            f"renter {row['renter_cash_real_return_pct']:.2f}%, verdict: {row['two_year_verdict']}"
        )

    print("=== Housing user cost ===")
    for _, row in user_cost.iterrows():
        print(f"{row['item']}: {row['percent_of_value']:.2f}%")

    print("=== Cash ===")
    latest_cash = cash.dropna(subset=["real_after_tax_33_6m_pct"]).iloc[-1]
    print(f"Latest six-month term deposit real after tax at 33%: {latest_cash['real_after_tax_33_6m_pct']:.2f}%")
    print(f"Mean six-month term deposit real after tax at 33% since 2000: {cash['real_after_tax_33_6m_pct'].mean():.2f}%")
    share_negative = (cash["real_after_tax_33_6m_pct"] < 0).mean() * 100
    print(f"Share of months with negative after-tax real return at 33%: {share_negative:.1f}%")


def chart_price() -> None:
    price = read("auckland_price_index.csv")
    months = pd.to_datetime(price["month"])
    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=160)
    ax.plot(months, price["nominal_index"], color=OCHRE, linewidth=2.0, label="Nominal index")
    ax.plot(months, price["real_index"], color=PINE, linewidth=2.2, label="Real index (CPI-deflated)")
    ax.fill_between(months, price["real_index"], price["real_index"].min() * 0.92, color=PINE, alpha=0.06)
    nominal_peak = price.loc[price["nominal_index"].idxmax()]
    real_peak = price.loc[price["real_index"].idxmax()]
    ax.scatter([pd.Timestamp(nominal_peak["month"])], [nominal_peak["nominal_index"]], color=OCHRE, zorder=5)
    ax.scatter([pd.Timestamp(real_peak["month"])], [real_peak["real_index"]], color=PINE, zorder=5)
    ax.annotate("Nominal peak\nJan 2022", xy=(pd.Timestamp(nominal_peak["month"]), nominal_peak["nominal_index"]),
                xytext=(pd.Timestamp("2023-08-01"), nominal_peak["nominal_index"]), fontsize=8, color=OCHRE)
    ax.annotate("Real peak\nDec 2021", xy=(pd.Timestamp(real_peak["month"]), real_peak["real_index"]),
                xytext=(pd.Timestamp("2017-06-01"), real_peak["real_index"] * 0.96), fontsize=8, color=PINE)
    ax.set_title("Auckland house prices rose, peaked and fell sharply in real terms")
    ax.set_ylabel("Nominal base Jan 2007 = 1000; real CPI-adjusted")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color=GRID, alpha=0.6)
    fig.text(0.01, 0.01, "QV Auckland HPI and Stats NZ CPI. QV is a non-official average equalised index.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHARTS / "fig1_price_index.png", facecolor=BG)
    plt.close(fig)


def chart_affordability() -> None:
    data = read("affordability_yield.csv")
    yields = data.dropna(subset=["gross_yield_pct"])
    ratios = data.dropna(subset=["price_to_income_ratio"])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160)
    axes[0].plot(yields["year"].astype(int), yields["gross_yield_pct"], color=PINE, linewidth=2.2, marker="o", markersize=3)
    axes[0].axhline(2.92, color=OCHRE, linestyle="--", linewidth=1)
    axes[0].set_title("Gross rental yield")
    axes[0].set_ylabel("% of value")
    axes[0].grid(axis="y", color=GRID, alpha=0.6)
    axes[1].bar(ratios["year"].astype(str), ratios["price_to_income_ratio"], color=OCHRE, width=0.5)
    for index, row in ratios.iterrows():
        axes[1].text(str(int(row["year"])), row["price_to_income_ratio"] + 0.2,
                     f"{row['price_to_income_ratio']:.2f}", ha="center", fontsize=8, color=OCHRE)
    axes[1].set_title("Price-to-income")
    axes[1].set_ylabel("Average value / median income")
    axes[1].set_ylim(0, 12)
    axes[1].grid(axis="y", color=GRID, alpha=0.6)
    fig.suptitle("Gross yield has recovered only slightly while price-to-income remains high", fontweight="bold")
    fig.text(0.01, 0.01, "Sources: QV; MBIE Tenancy Services; Stats NZ HILS; Auckland Council IDI estimate.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(CHARTS / "fig2_affordability_yield.png", facecolor=BG)
    plt.close(fig)


def chart_returns() -> None:
    data = read("real_returns.csv")
    order = ["5 years", "10 years", "15 years, post-GFC", "19 years, 2007-2026"]
    labels = ["5 years", "10 years", "15 years", "19 years"]
    rows = data.set_index("window").loc[order]
    positions = range(len(order))
    width = 0.26
    fig, ax = plt.subplots(figsize=(10, 4.3), dpi=160)
    ax.bar([p - width for p in positions], rows["housing_real_annualised_pct"], width=width, color=PINE, label="Housing, gross of costs")
    ax.bar(list(positions), rows["housing_net_real_annualised_pct"], width=width, color=SLATE, label="Housing, net of 5% round trip")
    ax.bar([p + width for p in positions], rows["cash_real_annualised_pct"], width=width, color=OCHRE, label="Cash after tax")
    ax.axhline(0, color=INK, linewidth=0.8)
    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Real return (% a year)")
    ax.set_title("Real returns depend heavily on the holding window and on transaction costs")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y", color=GRID, alpha=0.6)
    ax.yaxis.set_major_formatter(PCT)
    fig.text(0.01, 0.01, "Sources: QV; Stats NZ CPI; RBNZ B3; author calculations. Cash after 33% tax.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHARTS / "fig3_real_returns.png", facecolor=BG)
    plt.close(fig)


def chart_ownership() -> None:
    data = read("ownership_cohorts.csv")
    individual = data[(data["geography"] == "New Zealand") & (data["age_band"].isin(["25-29", "30-34", "35-39", "40-44"]))]
    auckland = data[data["geography"] == "Auckland Region"].sort_values("census_year")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160)
    colours = {"25-29": PINE_LIGHT, "30-34": PINE, "35-39": OCHRE, "40-44": SLATE}
    for band in ["25-29", "30-34", "35-39", "40-44"]:
        subset = individual[individual["age_band"] == band].sort_values("census_year")
        axes[0].plot(subset["census_year"].astype(int), subset["rate_percent"], marker="o", markersize=4,
                     linewidth=2, color=colours[band], label=band)
    axes[0].set_title("Individual ownership by age, New Zealand")
    axes[0].set_ylabel("% who own or partly own")
    axes[0].set_ylim(0, 75)
    axes[0].legend(frameon=False, fontsize=8, ncol=2)
    axes[0].grid(axis="y", color=GRID, alpha=0.6)
    axes[1].plot(auckland["census_year"].astype(int), auckland["rate_percent"], marker="o", markersize=4,
                 linewidth=2.4, color=PINE)
    axes[1].set_title("Household ownership, Auckland")
    axes[1].set_ylabel("% of households")
    axes[1].set_ylim(50, 80)
    axes[1].grid(axis="y", color=GRID, alpha=0.6)
    fig.suptitle("Younger cohorts own less, and Auckland ownership has drifted down since the 1980s", fontweight="bold")
    fig.text(0.01, 0.01, "Source: Stats NZ Census tenure tables and 2023 Census figure data.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(CHARTS / "fig4_ownership.png", facecolor=BG)
    plt.close(fig)


def chart_ai() -> None:
    data = read("ai_capital_cycle.csv")
    capex = data[(data["panel"] == "AI capital expenditure") & (data["series"].str.contains("fiscal year"))]
    concentration = data[data["panel"] == "Valuation and concentration"]
    credit = data[data["panel"] == "AI-related credit"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 7.0), dpi=160)
    axes[0, 0].bar(capex["period"], capex["value"], color=PINE)
    axes[0, 0].set_title("Big-four capex, US$ billion")
    axes[0, 0].grid(axis="y", color=GRID, alpha=0.6)

    cape_rows = concentration[concentration["series"] == "Shiller CAPE"]
    cape_labels = ["2000-01", "2021-01", "2026-10-21"]
    cape_values = []
    for label in cape_labels:
        match = cape_rows[cape_rows["period"] == label]
        cape_values.append(float(match.iloc[0]["value"]) if not match.empty else 0.0)
    axes[0, 1].bar(["2000", "2021", "2026"], cape_values, color=OCHRE, width=0.55)
    axes[0, 1].set_title("Shiller CAPE")
    axes[0, 1].set_ylim(30, 46)
    axes[0, 1].grid(axis="y", color=GRID, alpha=0.6)
    for index, value in enumerate(cape_values):
        axes[0, 1].text(index, value + 0.3, f"{value:.1f}", ha="center", fontsize=8, color=OCHRE)

    weights = concentration[concentration["series"].str.contains("weight")].head(2)
    axes[1, 0].bar(["Top 10 weight", "NVIDIA weight"], weights["value"].reset_index(drop=True), color=SLATE, width=0.45)
    axes[1, 0].set_title("Concentration, October 2026 (%)")
    axes[1, 0].set_ylim(0, 45)
    axes[1, 0].grid(axis="y", color=GRID, alpha=0.6)
    for index, value in enumerate(weights["value"].reset_index(drop=True)):
        axes[1, 0].text(index, value + 0.8, f"{value:.1f}", ha="center", fontsize=8, color=SLATE)

    credit_map = dict(zip(credit["series"], credit["value"]))
    credit_labels = ["Private credit 2024", "Private credit 2025", "HY issuance 2026", "HY index 2025"]
    credit_keys = [
        "private credit share of AI investment, 2024",
        "private credit share of AI investment, 2025",
        "AI issuers' share of non-refinance US high-yield issuance, 2026 to date",
        "AI issuers' share of JPM US high-yield bond index, end-2025",
    ]
    credit_values = [float(credit_map.get(key, 0)) for key in credit_keys]
    axes[1, 1].bar(credit_labels, credit_values, color=PINE_LIGHT, width=0.55)
    axes[1, 1].set_title("AI-related credit shares (%)")
    axes[1, 1].tick_params(axis="x", labelsize=7, rotation=15)
    axes[1, 1].set_ylim(0, 45)
    axes[1, 1].grid(axis="y", color=GRID, alpha=0.6)
    for index, value in enumerate(credit_values):
        axes[1, 1].text(index, value + 0.8, f"{value:.0f}", ha="center", fontsize=8, color=PINE)

    fig.suptitle("The AI capital boom is large, concentrated and increasingly financed with credit", fontweight="bold")
    fig.text(0.01, 0.01, "Sources: SEC XBRL company facts; SPY holdings; Yale Shiller data and a third-party reprint; Bank of England and IMF publications.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(CHARTS / "fig5_ai_capital_cycle.png", facecolor=BG)
    plt.close(fig)


def chart_scenario() -> None:
    data = read("scenario_outcomes.csv").set_index("scenario_id")
    order = ["A1", "A2", "B1", "B2", "C1", "C2", "R0"]
    names = {
        "A1": "AI correction / disinflation",
        "A2": "AI correction / inflation",
        "B1": "AI credit bust / disinflation",
        "B2": "AI credit bust / inflation",
        "C1": "Systemic unwind / disinflation",
        "C2": "Systemic unwind / inflation",
        "R0": "Reference: no unwind",
    }
    metrics = [
        "auckland_real_price_change_pct",
        "cash_after_tax_real_change_pct",
        "owner_real_position_change_pct",
        "renter_cash_real_return_pct",
    ]
    metric_labels = ["House real", "Cash real", "Owner 2-year", "Renter 2-year"]
    values = data.loc[order, metrics].astype(float)
    matrix = values.to_numpy()
    colour_map = LinearSegmentedColormap.from_list("scenario", ["#a23b32", "#d9b8a7", "#fffdf8", "#c7ddd4", "#1f4d3f"])
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=160)
    image = ax.imshow(matrix, cmap=colour_map, aspect="auto", vmin=-45, vmax=8)
    ax.set_xticks(range(len(metric_labels)))
    ax.set_xticklabels(metric_labels, fontsize=8)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([names[key] for key in order], fontsize=8)
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            value = matrix[row_index, column_index]
            ax.text(column_index, row_index, f"{value:.1f}", ha="center", va="center", fontsize=7.5, color=INK)
    ax.set_title("An AI-unwind stress would hurt a buyer in every severity, but by very different amounts")
    fig.colorbar(image, ax=ax, orientation="horizontal", pad=0.16, fraction=0.04, label="Percent over two years")
    fig.text(0.01, 0.01, "Hypothetical scenarios with author assumptions anchored to RBNZ, IMF and BIS stress tests. Not forecasts; no probabilities.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHARTS / "fig6_scenario_matrix.png", facecolor=BG)
    plt.close(fig)


def main() -> None:
    ensure_charts_dir()
    print_statistics()
    chart_price()
    chart_affordability()
    chart_returns()
    chart_ownership()
    chart_ai()
    chart_scenario()
    print("Replication complete: six PNG figures regenerated from the published CSVs.")


if __name__ == "__main__":
    main()
