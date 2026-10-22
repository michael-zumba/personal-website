#!/usr/bin/env python3
"""Reproduce the figures and reported statistics for the research brief.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Read the saved CSVs and regenerate all charts and key statistics.
"""

from __future__ import annotations

import random
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


random.seed(42)

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
CHARTS = PROJECT / "charts"

PINE = "#1f4d3f"
PINE_LIGHT = "#6a9c8b"
INK = "#23241f"
MUTED = "#6a685e"
OCHRE = "#a86b2d"
SLATE = "#60758a"
GRID = "#ded8ca"
BG = "#fffdf8"


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


def style_axis(axis: plt.Axes) -> None:
    axis.set_facecolor(BG)
    axis.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.7)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(GRID)
    axis.spines["bottom"].set_color(GRID)
    axis.tick_params(colors=MUTED, labelsize=9)


def add_source(fig: plt.Figure, text: str) -> None:
    fig.text(0.5, 0.01, text, ha="center", color=MUTED, fontsize=7.5)


def short_journal(value: str) -> str:
    names = {
        "The Accounting Review": "TAR",
        "Journal of Accounting Research": "JAR",
        "Journal of Accounting and Economics": "JAE",
        "Contemporary Accounting Research": "CAR",
        "Review of Accounting Studies": "RAS",
        "Accounting, Organizations and Society": "AOS",
        "The Journal of Finance": "JF",
        "Journal of Financial Economics": "JFE",
        "The Review of Financial Studies": "RFS",
        "Journal of Financial and Quantitative Analysis": "JFQA",
        "Review of Finance": "RoF",
    }
    return names.get(value, value)


def figure_one() -> None:
    data = read("submission_index.csv")
    fig, axis = plt.subplots(figsize=(10, 5.8), facecolor=BG)
    style_axis(axis)
    colors = {
        "The Journal of Finance": PINE,
        "The Review of Financial Studies": OCHRE,
    }
    for journal, group in data.groupby("journal"):
        group = group.sort_values("reporting_period_end")
        years = pd.to_datetime(group["reporting_period_end"]).dt.year
        axis.plot(
            years,
            group["submission_index"],
            marker="o",
            linewidth=2.2,
            markersize=5,
            color=colors[journal],
            label=journal,
        )
        last = group.iloc[-1]
        axis.annotate(
            f"{short_journal(journal)} {last['submission_index']:.1f}",
            (pd.to_datetime(last["reporting_period_end"]).year, last["submission_index"]),
            xytext=(7, 6),
            textcoords="offset points",
            fontsize=8,
            color=colors[journal],
            weight="bold",
        )
    axis.axhline(100, color=MUTED, linewidth=0.8, linestyle="--", alpha=0.7)
    axis.set_title(
        "Submissions rose unevenly in the two journals that disclose them",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_ylabel("Submission index (first observed period = 100)", color=MUTED)
    axis.set_xlabel("Reporting period ending year", color=MUTED)
    axis.legend(frameon=False, loc="upper left", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: American Finance Association; Society for Financial Studies. "
        "Journal-specific periods and definitions; not pooled.",
    )
    fig.savefig(CHARTS / "fig1_submissions.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_two() -> None:
    data = read("field_article_counts.csv")
    fig, axis = plt.subplots(figsize=(10, 5.8), facecolor=BG)
    style_axis(axis)
    for field, group in data.groupby("field"):
        group = group.sort_values("year")
        color = PINE if field == "Accounting" else SLATE
        axis.plot(
            group["year"],
            group["crossref_journal_articles"],
            marker="o",
            linewidth=2.2,
            markersize=4.5,
            color=color,
            label=field,
        )
        last = group.iloc[-1]
        axis.annotate(
            f"{field} {int(last['crossref_journal_articles'])}",
            (last["year"], last["crossref_journal_articles"]),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=8,
            color=color,
            weight="bold",
        )
    axis.set_title(
        "Published article output grew modestly and unevenly",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_ylabel("Crossref-indexed journal articles", color=MUTED)
    axis.set_xlabel("Publication year", color=MUTED)
    axis.legend(frameon=False, loc="upper left", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: Crossref journal-works queries for 11 selected journals. "
        "Crossref typing differs from journal-specific definitions.",
    )
    fig.savefig(CHARTS / "fig2_article_output.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_three() -> None:
    data = read("attention_journal_summary.csv").sort_values(
        "zero_citation_share", ascending=True
    )
    labels = [short_journal(value) for value in data["journal"]]
    values = data["zero_citation_share"] * 100
    fig, axis = plt.subplots(figsize=(10, 6.4), facecolor=BG)
    style_axis(axis)
    bars = axis.barh(labels, values, color=PINE_LIGHT, edgecolor=PINE, linewidth=0.6)
    for bar, value, zeros, total in zip(
        bars,
        values,
        data["zero_citations_articles"],
        data["articles"],
    ):
        axis.text(
            bar.get_width() + 0.4,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}% ({zeros}/{total})",
            va="center",
            fontsize=8,
            color=INK,
        )
    axis.set_xlim(0, max(values) * 1.28)
    axis.set_title(
        "Citation attention after three years varies sharply across journals",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_xlabel(
        "Articles with zero citations in first three calendar years (%)",
        color=MUTED,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: OpenAlex, 2020-2022 article cohorts. Citations are not readers; "
        "coverage and citation lag vary.",
    )
    fig.savefig(CHARTS / "fig3_zero_citations.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_four() -> None:
    data = read("review_workload.csv")
    data["end_year"] = pd.to_datetime(data["reporting_period_end"]).dt.year
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.4), facecolor=BG)
    panels = (
        ("The Journal of Finance", "The Journal of Finance", PINE),
        ("The Review of Financial Studies", "The Review of Financial Studies", OCHRE),
    )
    for axis, (journal, title, color) in zip(axes, panels):
        style_axis(axis)
        group = data[
            (data["journal"] == journal) & data["median_turnaround_days"].notna()
        ].sort_values("end_year")
        axis.plot(
            group["end_year"],
            group["median_turnaround_days"],
            marker="o",
            linewidth=2.2,
            markersize=5,
            color=color,
        )
        axis.set_xticks(sorted(group["end_year"].unique()))
        for _, row in group.iterrows():
            axis.annotate(
                f"{row['median_turnaround_days']:.1f}",
                (row["end_year"], row["median_turnaround_days"]),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                fontsize=7.5,
                color=color,
            )
        axis.set_title(title, loc="left", fontsize=10, color=INK)
        axis.set_ylabel("Median days", color=MUTED)
    axes[-1].set_xlabel("Reporting period ending year", color=MUTED)
    fig.suptitle(
        "Editorial decisions still take weeks",
        x=0.08,
        ha="left",
        fontsize=14,
        color=INK,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    add_source(
        fig,
        "Sources: Journal of Finance editor reports; Review of Financial Studies statistics. "
        "Missing years are not interpolated.",
    )
    fig.savefig(CHARTS / "fig4_review_capacity.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_five() -> None:
    data = read("ai_policy_latest.csv").sort_values("journal", ascending=True)
    labels = [short_journal(value) for value in data["journal"]]
    colors = [
        PINE if value == "Explicit AI guidance" else "#c7b9a7"
        for value in data["policy_status"]
    ]
    fig, axis = plt.subplots(figsize=(10, 6.2), facecolor=BG)
    style_axis(axis)
    bars = axis.barh(labels, [1] * len(data), color=colors, edgecolor=BG)
    for bar, status, date in zip(
        bars, data["policy_status"], data["snapshot_date"]
    ):
        date_text = str(date)
        axis.text(
            bar.get_width() + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{status} · {date_text[:4]}-{date_text[4:6]}-{date_text[6:]}",
            va="center",
            fontsize=7.5,
            color=INK,
        )
    axis.set_xlim(0, 2.05)
    axis.set_xticks([])
    axis.grid(False)
    axis.set_title(
        "AI guidance is visible on only four of eleven latest author pages",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: verified author-page snapshots. Missing page text does not prove "
        "that no linked publisher policy applies.",
    )
    fig.savefig(CHARTS / "fig5_ai_guidance.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_six() -> None:
    data = read("editorial_priority_summary.csv").sort_values(
        "journals_with_explicit_mention", ascending=True
    )
    fig, axis = plt.subplots(figsize=(10, 5.8), facecolor=BG)
    style_axis(axis)
    bars = axis.barh(
        data["category"],
        data["journals_with_explicit_mention"],
        color=SLATE,
        edgecolor="#44576a",
        linewidth=0.6,
    )
    for bar, count, total in zip(
        bars,
        data["journals_with_explicit_mention"],
        data["journals_observed"],
    ):
        axis.text(
            bar.get_width() + 0.12,
            bar.get_y() + bar.get_height() / 2,
            f"{count}/{total}",
            va="center",
            fontsize=8.5,
            color=INK,
        )
    axis.set_xlim(0, 10)
    axis.set_title(
        "Author guidance uses different definitions of valuable research",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_xlabel("Journals with an explicit keyword match", color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: coded latest author-guidance pages. Keyword presence is not an "
        "editorial decision rule.",
    )
    fig.savefig(CHARTS / "fig6_editorial_priorities.png", dpi=190, facecolor=BG)
    plt.close(fig)


def print_statistics() -> None:
    stats = read("analysis_statistics.csv").set_index("statistic_id")["value"]
    fields = read("field_article_counts.csv")
    article_2015 = int(
        fields[fields["year"] == 2015]["crossref_journal_articles"].sum()
    )
    article_2025 = int(
        fields[fields["year"] == 2025]["crossref_journal_articles"].sum()
    )
    attention = read("attention_journal_summary.csv")
    zeros = int(attention["zero_citations_articles"].sum())
    articles = int(attention["articles"].sum())
    policy = read("ai_policy_latest.csv")
    priorities = read("editorial_priority_summary.csv").set_index("category")
    print(f"Published articles, 2015: {article_2015}")
    print(f"Published articles, 2025: {article_2025}")
    print(f"Article-count change, 2015-2025: {article_2025 / article_2015 - 1:.6f}")
    print(f"Attention articles, 2020-2022: {articles}")
    print(f"Zero-citation articles, first three years: {zeros}")
    print(f"Pooled zero-citation share: {zeros / articles:.6f}")
    print(
        "Latest author pages with explicit AI guidance: "
        f"{sum(policy['policy_status'] == 'Explicit AI guidance')} of {len(policy)}"
    )
    for category, row in priorities.iterrows():
        print(
            f"{category}: {int(row['journals_with_explicit_mention'])} "
            f"of {int(row['journals_observed'])}"
        )
    for key in (
        "jf_submissions_2015",
        "jf_submissions_2024",
        "rfs_submissions_2023",
        "rfs_submissions_2026",
    ):
        print(f"{key}: {float(stats[key]):.0f}")


def main() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    figure_one()
    figure_two()
    figure_three()
    figure_four()
    figure_five()
    figure_six()
    print_statistics()
    print("Generated 6 PNG figures from CSV inputs.")


if __name__ == "__main__":
    main()
