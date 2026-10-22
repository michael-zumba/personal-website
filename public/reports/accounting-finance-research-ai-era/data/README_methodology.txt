What Is Accounting and Finance Research For in the AI Era?

Author: Dr Yuqian Zhang
Access date: 22 October 2026
Evidence window: 2015-2025, with selected 2026 operational and policy observations

Purpose

This research brief asks what becomes scarce and valuable in accounting and finance research when AI makes some parts of writing, coding, modelling and literature work cheaper. The analysis separates six things that are often combined:

1. Research production.
2. Citation attention.
3. Editorial gatekeeping and review time.
4. AI rules and visible author guidance.
5. Stated criteria for valuable research.
6. Corrections and retractions.

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

The issue-year hierarchy was published-print, then published-online, then issued. One fixed, documented title rule excluded nonresearch records: editor and editorial matter, front and back matter, issue information, announcements and society business, prize notices, conference programmes, participant schedules, reviewer lists, placement advertisements, corrections, retractions, corrigenda, book reviews, discussion pieces, issue introductions, obituaries and obituary-adjacent notices. Titles were normalised (HTML tags and entities removed) before matching. The resulting 9,044 unique Crossref research article records are stored in crossref_articles.csv. Journal-year counts are stored in crossref_article_counts.csv, and field totals are in field_article_counts.csv. Counts are 718 in 2015 and 918 in 2025 (+27.9%); at the 2024 endpoint the count is 887 (+23.5%).

Crossref article typing is not the same as a journal's internal definition of a research paper, and some residual miscellany may remain. The 2025 endpoint is provisional: Journal of Accounting and Economics records show a one-year fall that is more consistent with a deposit gap than with a publication decision. The counts therefore describe cleaned Crossref-indexed journal articles, not all research activity.

Journal submissions

Only two journals exposed comparable public operational data during the evidence collection.

The American Finance Association publishes Journal of Finance annual and monthly submission totals. Complete calendar years 2015 through 2024 are used. The 2025 table was incomplete at the access date and is excluded from the annual series.

The Society for Financial Studies publishes Review of Financial Studies submissions in rolling May-to-May periods. Those periods exclude resubmissions. The 2023 through 2026 entries are used and are not treated as calendar years.

The two journals use different definitions and reporting periods. They are not pooled. The indexed chart sets each journal's first observed period equal to 100.

No missing submission count was inferred from article output, acceptance rates or issue size.

Citation attention

Citation attention was tested but is not used as a comparative measure. The cohort is the set of Crossref research articles with 2020, 2021 and 2022 issue years (2,655 articles across 11 journals). Each DOI was matched to OpenAlex [8] in batches of up to 50 via the works API; all request URLs and raw responses are cached in the project evidence folder (attention_rebuild/). Of 2,655 articles, 2,578 (97.1%) were matched. The 68 unmatched records are OpenAlex redirects to SSRN versions, 67 of them in The Accounting Review, which explains that journal's lower match rate. Nine non-article records were excluded.

Citations were summed over the three calendar years starting with the Crossref issue year (not the OpenAlex year, which differs for 63% of records). Twenty-six matched articles (1.0%) had no recorded citation in the window. Journal shares ranged from 0.0% to 3.1%, with no more than five zero-citation articles in any journal and overlapping confidence intervals. The differences are not statistically distinguishable. An earlier version of the analysis used an OpenAlex online-first cohort that retained front matter and mis-dated records; it is withdrawn and the rebuild is documented in the project evidence folder (attention_rebuild/NOTES.md).

A citation is not a reader. Automated access, citation lag, incomplete indexing and differences in citation cultures all affect counts. The measure can show visible scholarly use; it cannot establish that human readers have disappeared, and it does not support a cross-journal ranking.

Review and gatekeeping

Journal of Finance editor reports provide annual acceptance rates, desk-rejection rates, decision counts and median turnaround times. The values used in review_workload.csv come from the 2015 through 2021 reports and the 2023 report, which also contains 2022 comparison values. The 2021 report PDF is image-only: its values (submissions 1,298; 1,301 decisions; median 48 days; acceptance 7.5%; desk rejection 31.9%) were transcribed from pages 1413-1416 by OCR and visual check. The 2022 report's Figure 1 annotates a different 2021 median (46 days); the 2021 report's own Table II value of 48 days is used. The 2024 and 2025 editor reports are published (DOIs 10.1111/jofi.13435 and 10.1111/jofi.70061) but could not be accessed, so the series stops in 2023.

The Review of Financial Studies statistics page provides rolling-period submission counts, acceptance rates and median turnaround times.

Missing years were retained as missing. Reporting definitions differ. A 43-day median decision time is not a peer-review quality score.

AI guidance snapshots

The analysis uses the latest usable official journal guidance or editorial-policy page for each journal. Nine pages were captured live on 22 October 2026 with a desktop browser user agent; The Review of Financial Studies and Review of Finance use the latest usable Internet Archive captures (30 April 2025 and 23 June 2024) because their live pages blocked automated access. The Journal of Finance is coded from the American Finance Association editorial-policies page because the Wiley author page was blocked and no later archived capture exists. Contemporary Accounting Research's publisher page now directs authors to the CAAA author-information page; the linked CAAA statement on the use of generative AI supplies the explicit terms.

The code searched visible page text for generative AI, generative artificial intelligence, artificial intelligence, AI-assisted, large language model, LLM and ChatGPT. An observation is coded as "Explicit AI guidance" when at least one AI term and at least one policy term are visible. Policy terms include disclose, disclosure, must not, cannot, not permitted, authorship, confidential, accountable, responsibility and responsible. Otherwise the observation is "No visible AI guidance".

Eight of the 11 journals show explicit AI guidance on the latest usable page. The three without visible guidance are The Review of Financial Studies (archived 2025), Journal of Financial and Quantitative Analysis (live 2026) and Review of Finance (archived 2024). Capture dates differ, and a missing page statement does not prove that a linked publisher policy is absent. The report does not describe page visibility as policy effectiveness, compliance or research quality.

Editorial priorities

The six-category matrix was recoded by hand from the extracted visible guidance text of each journal's latest usable page. A criterion counts only where the page states it as an author requirement or an editorial expectation, with a quotable sentence. Site navigation, JEL browse lists, copyright and cookie boilerplate, proof-stage notices and shared publisher template paragraphs are excluded; only journal-specific and society-or-publisher-policy statements count. Every present cell and its excerpt are stored in the project evidence folder (editorial_recode.csv).

The codebook is:

Contribution: contribution, novelty, significance or importance stated as an acceptance criterion.
Research design: research design, identification or rigour stated as an evaluation criterion.
Data transparency: data availability, sharing or access stated as an author requirement.
Reproducibility: replication, reproducibility or code sharing stated as a requirement.
Decision relevance: relevance to practitioners, policymakers or practice stated as a criterion.
Integrity and accountability: research integrity, plagiarism, misconduct or accountability stated as a requirement.

The counts are data transparency 5, integrity and accountability 4, reproducibility 3, contribution 2, research design 1 and decision relevance 0, out of 11 journals. They are lower bounds: two captured pages carry no substantive guidance and three journals hold policy in linked files. An earlier version used mechanical keyword matches; navigation menus and boilerplate inflated those counts and they are withdrawn. This matrix is not an editorial ranking and cannot show how editors weight criteria or whether decisions match the stated guidance.

Corrections and retractions

Crossref works were filtered separately by journal ISSN and update type: retraction, erratum and correction for 2015 through 2025. Counts are reported in corrections_retractions.csv.

Crossref update records are not a clean count of research errors. A single event can appear as an original record and a notice. The records do not share a common denominator. The brief therefore reports the filtered record counts and does not call them retraction rates.

External research evidence

Three research studies are used only for bounded evidence about what AI changes:

- Noy and Zhang examine mid-level professional writing tasks.
- Doshi and Hauser examine short-story creativity and collective similarity.
- Si, Yang and Hashimoto examine research-idea generation among NLP researchers.
- Gardner, Krupa and Mammadov measure AI-associated vocabulary in accounting papers and abstracts.
- Kobak and coauthors estimate a lower bound on LLM-processed biomedical abstracts.

None of these studies estimates the long-run value of accounting and finance research. They are not treated as direct evidence about accounting or finance research quality.

Evidence verification

DOI-bearing papers and reports have Crossref metadata checks. Journal reports, official guidance pages, live statistics pages and API-derived datasets were retrieved to local snapshots or cached API responses. The source ledger records exact locators, access dates and limitations. Numeric claims in the report and summary are recomputed from the published CSV files by scripts/replicate.py, and qualitative claims were checked against their source snapshots. The source and claim ledgers describe the verification method per record.

Interpretive material

The capability matrix, contribution scorecard and 2030 scenarios are labelled analytical proposals. They are not observed outcomes.

Scope note: the approved contract anticipated coding official journal editorials as well as author guidance, and corrections from Retraction Watch as well as Crossref. The delivered measures are narrower: six criteria are coded from author-guidance pages, and correction counts come from Crossref update records only. The report labels both measures by what they actually cover.

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

The script reads the CSV files, prints the statistics used in the report and summary, and regenerates all five charts.

Supporting re-runs:

- python3 scripts/code_editorial_priorities.py rebuilds the editorial-priority table from the manual coding file.
- python3 scripts/build_analysis_data.py rebuilds derived tables.
- python3 scripts/build_evidence_ledgers.py rebuilds the source, claim and figure ledgers.
- evidence/expansion/attention_rebuild/attention_rebuild.py rebuilds the Crossref-matched citation windows (network; cached responses included).
- scripts/collect_crossref.py rebuilds the cleaned Crossref article set (network); scripts/collect_corrections.py reproduces the correction and retraction record counts (network).
