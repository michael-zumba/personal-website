#!/usr/bin/env python3
"""Reproduce the figures and reported statistics for the research brief.

Author: Dr Yuqian Zhang
Date: 2026-10-22
Purpose: Read the saved CSVs and regenerate all charts and key statistics.
"""

from __future__ import annotations

import html
import random
import re
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
NONRESEARCH_TITLE = re.compile(
    r"^(?:"
    r"editor(?:['\u2019])?s?\s+note\b|editorial\b|"
    r"(?:annual\s+)?editor\s+report\b|"
    r"annual\s+report\s+(?:of|and)\b|report\s+of\s+the\b|"
    r"(?:retraction|retractions|retracted)\b|"
    r"errat(?:um|a)\b|corrigend(?:um|a)\b|correction\b|"
    r"expression\s+of\s+concern\b|addendum\b|"
    r"publisher(?:['\u2019])?s?\s+(?:note|correction)\b|"
    r"book\s+reviews?\b|commentary\b|comment\s+on\b|"
    r"discussion\s+of\b|introduction\b|"
    r"issue\s+information\b|covers?\s+and\s+front\s+matter\b|"
    r"front\s+matter\b|back\s+matter\b|"
    r"cover(?:\s*$|\s+image\b)|in\s+this\s+issue\b|masthead\b|"
    r"table\s+of\s+contents\b|"
    r"announcements?\b|american\s+finance\s+association\b|"
    r"miscellanea\b|dimensional\s+fund\s+advisors\b|"
    r"brattle\s+group\b|amundi\b|"
    r"call\s+for\s+papers?\b|forthcoming\s+articles?\b|"
    r"preliminary\s+program\b|participant\s+schedule\b|"
    r"afa\s+\d{4}\b|index\s+to\s+volume\b|"
    r"acknowledg(?:e)?ments?\b|in\s+memoriam\b|minutes\s+of\b|"
    r"obituary\b|preface\b|foreward\b|foreword\b|"
    r"list\s+of\s+(?:reviewers|referees)\b|ad\s+hoc\s+reviewers\b|"
    r"\d{4}\s+excellence\s+in\s+refereeing\b|"
    r"jfq\b|car\b|abstracts/|oup\s+accepted\s+manuscript\b|"
    r"sfs\s+statement\b|aaa\b|biblioscene\b|"
    r"be\s+the\s+thought\s+leaders\b"
    r")",
    re.IGNORECASE,
)
NONRESEARCH_ANYWHERE = re.compile(r"\bplacement\s+ads?\b", re.IGNORECASE)


def _clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value or ""))).strip()


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


def validate_inputs() -> None:
    articles = read("crossref_articles.csv")
    counts = read("crossref_article_counts.csv")
    attention = read("openalex_attention_articles.csv")
    cohorts = read("attention_cohorts.csv")
    attention_summary = read("attention_journal_summary.csv")
    submissions = read("submissions_outputs.csv")
    policy = read("ai_policy_latest.csv")
    priorities = read("editorial_priorities.csv")

    if not articles["doi"].is_unique:
        raise ValueError("Crossref article DOIs are not unique.")
    titles = articles["title"].fillna("").map(_clean_title)
    if titles.str.contains(NONRESEARCH_TITLE, na=False).any() or titles.str.contains(
        NONRESEARCH_ANYWHERE, na=False
    ).any():
        raise ValueError("Nonresearch Crossref titles remain in the article data.")
    grouped = (
        articles.groupby(["journal", "field", "publication_year"])
        .size()
        .rename("observed")
        .reset_index()
    )
    merged = counts.merge(
        grouped,
        left_on=["journal", "field", "year"],
        right_on=["journal", "field", "publication_year"],
        how="outer",
        indicator=True,
    )
    if not merged["_merge"].eq("both").all():
        raise ValueError("Crossref article counts do not match article records.")
    if not merged["crossref_research_articles"].eq(merged["observed"]).all():
        raise ValueError("Crossref journal-year totals are inconsistent.")

    if not attention["doi"].is_unique:
        raise ValueError("OpenAlex DOIs are not unique.")
    titles = attention["title"].fillna("").map(_clean_title)
    if titles.str.contains(NONRESEARCH_TITLE, na=False).any() or titles.str.contains(
        NONRESEARCH_ANYWHERE, na=False
    ).any():
        raise ValueError("Nonresearch OpenAlex titles remain in the attention data.")
    if not attention["zero_citations_first_3y"].isin([0, 1]).all():
        raise ValueError("Attention flag must be binary.")
    cohort_totals = (
        cohorts.groupby(["journal", "field"])[["zero_citations_articles", "articles"]]
        .sum()
        .reset_index()
    )
    comparison = attention_summary.merge(
        cohort_totals,
        on=["journal", "field"],
        suffixes=("_summary", "_cohort"),
        how="outer",
        indicator=True,
    )
    if not comparison["_merge"].eq("both").all():
        raise ValueError("Attention summary does not match article cohorts.")
    if not comparison["zero_citations_articles_summary"].eq(
        comparison["zero_citations_articles_cohort"]
    ).all():
        raise ValueError("Zero-citation totals are inconsistent.")
    if not comparison["articles_summary"].eq(comparison["articles_cohort"]).all():
        raise ValueError("Attention denominators are inconsistent.")

    if (submissions["total_submissions"] <= 0).any():
        raise ValueError("Submission totals must be positive.")
    if policy["journal"].duplicated().any():
        raise ValueError("Latest policy table must contain one row per journal.")
    allowed_status = {
        "Explicit AI guidance",
        "No visible AI guidance",
    }
    if not set(policy["policy_status"]).issubset(allowed_status):
        raise ValueError("Unknown policy status.")
    if not priorities["present"].isin([0, 1]).all():
        raise ValueError("Editorial-priority values must be binary.")


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
        "Submission trends differ at the two journals with public data",
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
    count_2015 = int(data.loc[data["year"] == 2015, "crossref_research_articles"].sum())
    count_2025 = int(data.loc[data["year"] == 2025, "crossref_research_articles"].sum())
    change = (count_2025 / count_2015 - 1) * 100
    fig, axis = plt.subplots(figsize=(10, 5.8), facecolor=BG)
    style_axis(axis)
    for field, group in data.groupby("field"):
        group = group.sort_values("year")
        color = PINE if field == "Accounting" else SLATE
        axis.plot(
            group["year"],
            group["crossref_research_articles"],
            marker="o",
            linewidth=2.2,
            markersize=4.5,
            color=color,
            label=field,
        )
        last = group.iloc[-1]
        axis.annotate(
            f"{field} {int(last['crossref_research_articles'])}",
            (last["year"], last["crossref_research_articles"]),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=8,
            color=color,
            weight="bold",
        )
    axis.set_title(
        f"Crossref research article counts rose {change:.1f}% from 2015 to 2025",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_ylabel("Crossref research articles", color=MUTED)
    axis.set_xlabel("Publication year", color=MUTED)
    axis.legend(frameon=False, loc="upper left", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: Crossref research article queries for 11 selected journals. "
        "Editorial, front-matter, announcement and other nonresearch titles are excluded.",
    )
    fig.savefig(CHARTS / "fig2_article_output.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_four() -> None:
    data = read("review_workload.csv")
    data["end_year"] = pd.to_datetime(data["reporting_period_end"]).dt.year
    all_years = pd.Series(range(2015, 2027))
    fig, axis = plt.subplots(figsize=(10, 5.8), facecolor=BG)
    style_axis(axis)
    colors = {
        "The Journal of Finance": PINE,
        "The Review of Financial Studies": OCHRE,
    }
    for journal, color in colors.items():
        group = data[
            (data["journal"] == journal) & data["median_turnaround_days"].notna()
        ].sort_values("end_year")
        values = (
            group.set_index("end_year")["median_turnaround_days"]
            .reindex(all_years)
            .tolist()
        )
        axis.plot(
            all_years,
            values,
            marker="o",
            linewidth=2.2,
            markersize=5,
            color=color,
            label=journal,
        )
        last = group.iloc[-1]
        axis.annotate(
            short_journal(journal),
            (last["end_year"], last["median_turnaround_days"]),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=8,
            weight="bold",
            color=color,
        )
    axis.set_title(
        (
            "Median time to an editorial decision ranged from "
            f"{int(data['median_turnaround_days'].min())} to "
            f"{int(data['median_turnaround_days'].max())} days"
        ),
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_ylabel("Median days", color=MUTED)
    axis.set_xlabel("Reporting period ending year", color=MUTED)
    axis.set_xticks(range(2015, 2026, 2))
    axis.set_ylim(20, 60)
    axis.legend(frameon=False, loc="upper left", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Sources: Journal of Finance editor reports; Review of Financial Studies statistics. "
        "Missing years are not interpolated.",
    )
    fig.savefig(CHARTS / "fig3_review_capacity.png", dpi=190, facecolor=BG)
    plt.close(fig)


def figure_five() -> None:
    data = read("ai_policy_latest.csv").sort_values("journal", ascending=True)
    explicit = int((data["policy_status"] == "Explicit AI guidance").sum())
    total = len(data)
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
        f"{explicit} of {total} official journal pages showed explicit AI guidance",
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
    fig.savefig(CHARTS / "fig4_ai_guidance.png", dpi=190, facecolor=BG)
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
        "Author guidance states few research criteria explicitly",
        loc="left",
        fontsize=14,
        color=INK,
        pad=14,
    )
    axis.set_xlabel("Journals stating the criterion", color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    add_source(
        fig,
        "Source: coded latest author-guidance pages. Keyword presence is not an "
        "editorial decision rule.",
    )
    fig.savefig(CHARTS / "fig5_editorial_priorities.png", dpi=190, facecolor=BG)
    plt.close(fig)


def print_statistics() -> None:
    stats = read("analysis_statistics.csv").set_index("statistic_id")["value"]
    fields = read("field_article_counts.csv")
    crossref = read("crossref_articles.csv")
    crossref_counts = read("crossref_article_counts.csv")
    submissions = read("submissions_outputs.csv")
    submission_index = read("submission_index.csv")
    review = read("review_workload.csv")
    corrections = read("corrections_retractions.csv")
    article_2015 = int(
        fields[fields["year"] == 2015]["crossref_research_articles"].sum()
    )
    article_2025 = int(
        fields[fields["year"] == 2025]["crossref_research_articles"].sum()
    )
    attention = read("attention_journal_summary.csv")
    zeros = int(attention["zero_citations_articles"].sum())
    articles = int(attention["articles"].sum())
    policy = read("ai_policy_latest.csv")
    priorities = read("editorial_priority_summary.csv").set_index("category")
    print(f"Crossref records: {len(crossref)}")
    for year, count in (
        crossref_counts.groupby("year")["crossref_research_articles"].sum().items()
    ):
        print(f"Crossref article total, {int(year)}: {int(count)}")
    print(f"Crossref research articles, 2015: {article_2015}")
    print(f"Crossref research articles, 2025: {article_2025}")
    print(f"Article-count change, 2015-2025: {article_2025 / article_2015 - 1:.6f}")
    pivot = crossref_counts.pivot(
        index="journal",
        columns="year",
        values="crossref_research_articles",
    )
    print(
        "Journals with fewer Crossref articles in 2025 than 2015: "
        f"{int((pivot[2025] < pivot[2015]).sum())}"
    )
    for _, row in submissions.iterrows():
        print(
            "Submissions: "
            f"{row['journal']}, {row['reporting_period_start']} to "
            f"{row['reporting_period_end']}: {int(row['total_submissions'])}"
        )
    for _, row in submission_index.iterrows():
        print(
            "Submission index: "
            f"{row['journal']}, {row['reporting_period_end']}: "
            f"{float(row['submission_index']):.6f}"
        )
    print(f"OpenAlex research articles, 2020-2022: {articles}")
    print(f"Zero-citation articles, first three years: {zeros}")
    print(f"Pooled zero-citation share: {zeros / articles:.6f}")
    for _, row in attention.sort_values("journal").iterrows():
        print(
            "Zero-citation share: "
            f"{row['journal']}: "
            f"{int(row['zero_citations_articles'])} of {int(row['articles'])}, "
            f"{float(row['zero_citation_share']):.6f}"
        )
    for _, row in review.iterrows():
        print(
            "Review metrics: "
            f"{row['journal']}, {row['reporting_period_start']} to "
            f"{row['reporting_period_end']}: "
            f"median={row['median_turnaround_days']}, "
            f"acceptance={row['acceptance_rate']}, "
            f"desk_rejection={row['desk_rejection_rate']}, "
            f"decisions={row['decisions']}"
        )
    print(
        "Latest author pages with explicit AI guidance: "
        f"{sum(policy['policy_status'] == 'Explicit AI guidance')} of {len(policy)}"
    )
    print(
        "Latest author pages without visible AI guidance: "
        f"{sum(policy['policy_status'] == 'No visible AI guidance')} of {len(policy)}"
    )
    for _, row in policy.sort_values("journal").iterrows():
        print(
            f"AI guidance: {row['journal']}, {row['snapshot_date']}: "
            f"{row['policy_status']}"
        )
    for category, row in priorities.iterrows():
        print(
            f"{category}: {int(row['journals_with_explicit_mention'])} "
            f"of {int(row['journals_observed'])}"
        )
    print(
        "Crossref retraction-update records: "
        f"{int(corrections['retraction_update_records'].sum())}"
    )
    print(
        "Crossref erratum-update records: "
        f"{int(corrections['erratum_update_records'].sum())}"
    )
    print(
        "Crossref correction-update records: "
        f"{int(corrections['correction_update_records'].sum())}"
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
    validate_inputs()
    print("Input validation: pass")
    figure_one()
    figure_two()
    figure_four()
    figure_five()
    figure_six()
    print_statistics()
    print("Generated 5 PNG figures from CSV inputs.")


if __name__ == "__main__":
    main()
