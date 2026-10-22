What Is Accounting and Finance Research For in the AI Era?

Author: Dr Yuqian Zhang
Access date: 22 October 2026
Evidence window: 2015-2025, with selected 2026 operational and policy observations

Purpose

This research brief asks what becomes scarce and valuable in accounting and finance research when AI makes some parts of writing, coding, modelling and literature work cheaper. The analysis separates five things that are often combined:

1. Research production.
2. Citation attention.
3. Editorial gatekeeping and review time.
4. AI rules and visible author guidance.
5. Stated criteria for valuable research.

The report does not measure human readership directly. It also does not identify the causal effect of AI on research quality.

Journal sample

The frozen candidate sample contains 11 English-language accounting and finance journals:

The Accounting Review; Journal of Accounting Research; Journal of Accounting and Economics; Contemporary Accounting Research; Review of Accounting Studies; Accounting, Organizations and Society; The Journal of Finance; Journal of Financial Economics; The Review of Financial Studies; Journal of Financial and Quantitative Analysis; and Review of Finance.

The sample is purposeful and contains influential accounting and finance journals. It is not a census of accounting and finance research. Journal-level inclusion and exclusion decisions are recorded in journal_scope.csv.

Crossref article counts

The Crossref REST API was queried separately for each journal ISSN. The work filter used:

- type: journal-article;
- publication date from 1 January 2014 through 31 December 2026;
- issue or publication year retained only for 2015 through 2025;
- DOI de-duplication within the collected sample.

The issue-year hierarchy was published-print, then published-online, then issued. One fixed title rule excluded nonresearch records labelled as annual editor reports, editor notes, retractions, errata, corrections, book reviews, issue introductions and commentary. The resulting 10,377 unique Crossref research article records are stored in crossref_articles.csv. Journal-year counts are stored in crossref_article_counts.csv, and field totals are in field_article_counts.csv.

Crossref article typing is not the same as a journal's internal definition of a research paper. Records can include editorials, corrections, introductions or other content indexed as journal articles. The counts therefore describe Crossref-indexed journal articles, not all research activity.

Journal submissions

Only two journals exposed comparable public operational data during the evidence collection.

The American Finance Association publishes Journal of Finance annual and monthly submission totals. Complete calendar years 2015 through 2024 are used. The 2025 table was incomplete at the access date and is excluded from the annual series.

The Society for Financial Studies publishes Review of Financial Studies submissions in rolling May-to-May periods. Those periods exclude resubmissions. The 2023 through 2026 entries are used and are not treated as calendar years.

The two journals use different definitions and reporting periods. They are not pooled. The indexed chart sets each journal's first observed period equal to 100.

No missing submission count was inferred from article output, acceptance rates or issue size.

Citation attention

OpenAlex was queried by source ID for article records published in 2020, 2021 and 2022. Filters required type article and a DOI. The same fixed title rule removed editor reports, editor notes, retractions, errata, corrections, book reviews, issue introductions and commentary.

Citations in the first three calendar years were calculated by summing OpenAlex counts_by_year from the publication year through the publication year plus two. An article with no positive count in those years is classified as having zero citations in the window.

Review of Finance was excluded from the attention comparison because its OpenAlex source record was too sparse for this measure. Coverage for the other journals is documented in openalex_coverage.csv. OpenAlex coverage is incomplete even where records were available.

A citation is not a reader. A zero count can reflect a paper with no readers, a paper that is read but not cited, a paper that is cited but not indexed, or a paper that is cited outside the OpenAlex record. The measure is citation attention, not human attention.

Review and gatekeeping

Journal of Finance editor reports provide annual acceptance rates, desk-rejection rates, decision counts and median turnaround times. The values used in review_workload.csv come from the 2015 through 2020 reports and the 2023 report, which also contains 2022 comparison values.

The Review of Financial Studies statistics page provides rolling-period submission counts, acceptance rates and median turnaround times.

Missing years were retained as missing. Reporting definitions differ. A 43-day median decision time is not a peer-review quality score.

AI guidance snapshots

The Internet Archive CDX API was used to locate snapshots of official journal author-guideline pages. The analysis uses one baseline snapshot from 2021 through June 2022 where available and the latest usable snapshot from 2023 through the access date. Exact timestamps, archive URLs and local HTML snapshots are recorded in ai_policy_status.csv.

The code searched visible page text for:

- generative AI;
- generative artificial intelligence;
- artificial intelligence;
- AI-assisted;
- large language model;
- LLM;
- ChatGPT.

An observation is coded as "Explicit AI guidance" when at least one AI term and at least one policy term are visible. Examples of policy terms include disclose, authorship, confidential, accountable and responsibility. Otherwise the observation is "No visible AI guidance".

This is a measure of guidance visible on the author page. A journal or publisher may have a linked policy elsewhere. The report does not describe page visibility as policy effectiveness, compliance or research quality.

The public policy CSV contains only short evidence excerpts. Full archived HTML pages are retained in the private project evidence store for audit and are not redistributed.

Editorial priorities

The latest usable author-guidance snapshot for each journal was coded against a short codebook:

Contribution: contribution, novelty, significance or importance.
Research design: research design, identification, rigorous or rigor.
Data transparency: data availability, data sharing, data access, data policy or research data.
Reproducibility: replicate, replication, reproducible, reproducibility, code sharing or code and data.
Decision relevance: practitioner, policymaker, regulator, decision-making, real-world, policy implication, practical implication or practically relevant.
Integrity and accountability: research integrity, plagiarism, misconduct, accountability or accountable.

The first pass was generated mechanically from visible main-page text. All matches were inspected in context, and the full sample was recoded in a second deterministic pass. Ambiguities were resolved conservatively. A term is recorded as present only when it appears in visible guidance text.

This matrix is not an editorial ranking. It records explicit words. It cannot show how editors weight the criteria or whether their decisions match the stated guidance.

Corrections and retractions

Crossref works were filtered separately by journal ISSN and update type: retraction, erratum and correction for 2015 through 2025. Counts are reported in corrections_retractions.csv.

Crossref update records are not a clean count of research errors. A single event can appear as an original record and a notice. The records do not share a common denominator. The brief therefore reports the filtered record counts and does not call them retraction rates.

External research evidence

Three research studies are used only for bounded evidence about what AI changes:

- Noy and Zhang examine mid-level professional writing tasks.
- Doshi and Hauser examine short-story creativity and collective similarity.
- Si, Yang and Hashimoto examine research-idea generation among NLP researchers.

None of these studies estimates the long-run value of accounting and finance research. They are not treated as direct evidence about accounting or finance research quality.

Evidence verification

DOI-bearing papers and reports have Crossref metadata checks. Journal reports, archived author pages, live statistics pages and API-derived datasets were retrieved to local snapshots. The source ledger records exact locators, access dates and limitations. The reference-check file reports the verification result for all sources.

Interpretive material

The capability matrix, contribution scorecard and 2030 scenarios are labelled analytical proposals. They are not observed outcomes.

Files

- journal_scope.csv: journal sample and inclusion decisions.
- submissions_outputs.csv: reported submission counts.
- submission_index.csv: within-journal index for the submission chart.
- crossref_articles.csv: article-level Crossref records.
- crossref_article_counts.csv: journal-year Crossref article counts.
- field_article_counts.csv: field-year Crossref article counts.
- openalex_attention_articles.csv: article-level OpenAlex cohorts and citation windows.
- attention_cohorts.csv: journal-year attention cohorts.
- attention_journal_summary.csv: pooled journal attention measures.
- openalex_coverage.csv: Crossref-to-OpenAlex coverage checks.
- review_workload.csv: reported decision times and rates.
- ai_policy_status.csv: dated journal-page policy observations.
- ai_policy_latest.csv: latest usable policy observation per journal.
- editorial_priorities.csv: coded journal-category observations.
- editorial_priority_summary.csv: aggregate codebook counts.
- corrections_retractions.csv: Crossref update-record counts.
- capability_model.csv: analytical task and responsibility model.
- contribution_scorecard.csv: proposed contribution portfolio.
- scenario_assumptions.csv: labelled 2030 scenarios.
- analysis_statistics.csv: key derived statistics used in the report.

Replication

Run:

python3 scripts/replicate.py

The script reads the CSV files, prints the statistics used in the report and summary, and regenerates all six charts.
