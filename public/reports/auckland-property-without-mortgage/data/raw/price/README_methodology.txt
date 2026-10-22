AUCKLAND PRICE, RENT AND INCOME EVIDENCE STREAM - DATA AND METHODOLOGY
Project: auckland-property-without-mortgage
Stream: price-evidence (dimensions 1-2: real prices and real returns; affordability, rent and cost of owning)
Access date for every source below: 2026-10-22 (Pacific/Auckland). Data frequencies and last observations are stated per file.

------------------------------------------------------------------
1. FILES IN THIS DIRECTORY
------------------------------------------------------------------
national_cpi.csv
  Quarterly national consumers price index, 2000Q1 to 2026Q3 (107 observations).
  Columns:
    period                    quarter label, e.g. 2000Q1
    period_end_quarter        Stats NZ period key (YYYY.MM, month = last month of quarter)
    cpi_index_all_groups_base_jun2017_1000
    series_id                 CPIQ.SE9A
    source_id                 S_PRICE_STATS_CPI_SERIES
    note
  Use: deflator for all real values in this stream. Base: June 2017 quarter = 1000.
  STATUS in source file: FINAL for every observation used.

auckland_qv_hpi.csv
  Monthly QV House Price Index for the Auckland Region, January 2007 to September 2026 (237 observations).
  Columns:
    month
    qv_hpi_index_base_2007_01_1000     QV index, January 2007 = 1000
    qv_avg_equalised_value_nzd         QV "average equalised value" (AVERAGE, not median sale price)
    qv_lower_quartile_index/value_nzd
    qv_upper_quartile_index/value_nzd
    qv_one_month_change_pct            published one-month change
    source_id                          S_PRICE_QV_HPI_API
  Use: the continuous Auckland price series for real returns and peak-to-trough work.
  IMPORTANT: this is a NON-OFFICIAL index (Quotable Value Ltd, a state-owned valuation
  company). It is used because the REINZ HPI history is paywalled (see section 5).

auckland_hpi.csv
  Sparse REINZ observations (July 2021, July 2022, September 2026). REINZ publishes a free
  monthly media release with national levels and can publish Auckland levels only inside the
  member-gated Monthly Property Report; one public 2022-vintage PDF was retrievable.
  Columns:
    month, reinz_hpi_auckland_index, reinz_median_price_nzd, reinz_sales_count,
    reinz_median_days_to_sell, reinz_median_price_yoy_pct, reinz_hpi_yoy_pct, source_id, note
  Blank cells mean "not published in the free source", not zero.
  IMPORTANT: 2022-vintage REINZ HPI levels are not directly comparable with current REINZ
  HPI values (re-basing/revision since 2022). The 2021-07 DTS value (32) is derived from the
  published "13 days more than the same month last year" comparison and is flagged.

auckland_rents.csv
  Monthly panel, February 1993 to September 2026 (404 rows; each column is populated only
  where its source covers the month).
  Columns:
    month
    mbie_bond_auckland_median_weekly_rent_nzd   MBIE Tenancy Services bond data, Auckland Region
    mbie_bond_auckland_lodged_bonds
    mbie_bond_auckland_active_bonds
    statsnz_cpi_auckland_rent_index_flow        Stats NZ CPIM.SE1041F (Nov 2006 = 1000)
    statsnz_cpi_national_rent_index_flow        Stats NZ CPIM.SE9041F (Nov 2006 = 1000)
    statsnz_cpi_national_rent_index_stock       Stats NZ CPIM.SE9041S (Dec 2006 = 1000)
  Coverage: MBIE bond medians 1993-02 to 2026-08; Stats NZ rent indexes 2006-11 to 2026-09.

household_income.csv
  Long-format income and housing-cost observations (9 rows): HILS year ended June 2025
  (Auckland region and New Zealand medians/averages), IDI 2023 Auckland median household
  income, 2023 Census Auckland median personal income and median household rent.
  Columns: year, measure, geography, value_nzd, unit, statistical_note, source_id
  WARNING: the three income families (HILS, IDI, Census) are NOT mutually comparable.

ownership_cost_indicators.csv
  Quarterly national CPI class indexes used as ownership-cost indicators, 2000Q1 to 2026Q3.
  Columns: period + cpi_local_authority_rates (CPIQ.SE904403), cpi_dwelling_insurance
  (CPIQ.SE911402), cpi_property_maintenance_services (CPIQ.SE904302),
  cpi_actual_rentals_housing (CPIQ.SE904101); base June 2017 quarter = 1000; national only.
  These are national price indexes for the relevant classes, not Auckland Council rate
  assessments or insurer premiums.

derived_affordability_yield.csv
  DERIVED FILE (author calculations), not a source series:
    period, qv_avg_equalised_value_nzd, mbie_bond_auckland_weekly_rent_nzd,
    gross_yield_pct, median_household_income_nzd, price_to_income_ratio,
    computation, source_ids
  Rows are September snapshots 2007-2026 for gross yield, plus price-to-income rows for
  2023, 2025 and 2026.

------------------------------------------------------------------
2. DEFINITIONS AND FORMULAS
------------------------------------------------------------------
Nominal: as published, current NZ dollars or index points.
Real: nominal divided by the national CPI all groups index of the same quarter
      (CPIQ.SE9A, June 2017 quarter = 1000). CPI is quarterly, so each month is assigned to
      the quarter containing it; the deflator is that quarter's index.
Real value of an index: real_t = index_t / CPI(q(t))
Real change over a window: (real_T / real_t0 - 1) x 100

Peak-to-trough: the peak is the maximum of the observed series (or of the stated sub-window
for an episode); the trough is the minimum after that peak within the stated episode window.
Peak and trough months are reported explicitly in the claim ledger. No window was chosen
after seeing a preferred result.

Gross rental yield:  (weekly median rent x 52) / average dwelling value x 100
  Numerator: MBIE Tenancy Services median rent for NEW bonds in the Auckland Region, August
  of the reference year. Denominator: QV average equalised value for September of the same
  year. Gross yield excludes rates, insurance, maintenance, vacancy and tax; it mixes a
  new-tenancy median rent with an average stock value.

Price-to-income:  average dwelling value / median annual household income, both nominal.
  2023 uses QV September 2023 value over the IDI 2023 Auckland median gross household income.
  2025 uses QV September 2025 value over the HILS year-ended-June-2025 Auckland median gross
  household income.
  2026 uses the QV September 2026 value over the same 2025 HILS income (no 2026 income
  observation exists). This is labelled in the computation column.

Real house-price growth windows to September 2026: 5 years (Sep 2021), 10 years (Sep 2016),
15 years (Sep 2011, labelled post-GFC episode), and 19 years (Sep 2007). A 20-year window is
not computable because the QV series starts in January 2007.

------------------------------------------------------------------
3. SOURCE IDs, ACCESS AND ARCHIVING
------------------------------------------------------------------
S_PRICE_STATS_CPI_SEP2026    Stats NZ, "Consumers price index: September 2026 quarter", 2026-10-22
S_PRICE_STATS_CPI_SERIES     Stats NZ CPI index-numbers CSV (Infoshare long format), 2.94 MB
S_PRICE_STATS_SPI_SEP2026    Stats NZ, "Selected price indexes: September 2026", 2026-10-16
S_PRICE_MBIE_BOND_REGION     MBIE Tenancy Services, rental bond data by region, updated 2026-10-13
S_PRICE_QV_HPI_API           QV House Price Index public JSON API, Auckland Region
S_PRICE_QV_HPI_PAGE          QV House Price Index public page, September 2026 quarter
S_PRICE_REINZ_RELEASE_SEP2026 REINZ September 2026 property report media release, 2026-10-14
S_PRICE_REINZ_REPORT_JUL2022  REINZ Monthly Property Report, July 2022 (public legacy PDF)
S_PRICE_STATS_HILS_2025      Stats NZ, "Household income and housing-cost statistics: YE June 2025"
S_PRICE_KA_IDI_INCOME_2024   Auckland Council (Knowledge Auckland), "Household income in Auckland", Nov 2024
S_PRICE_STATS_CENSUS_AKL_2023 Stats NZ, "Our region: Auckland", 2023 Census infographic page

Every source is archived under evidence/snapshots/price/ as
<source_id>_<YYYYMMDD>.<ext>. Raw HTML, raw CSV and the QV JSON payload (converted to a tidy
CSV) are stored as downloaded. The REINZ July 2022 report is an 11.9 MB PDF; its text
transcription (pdftotext -layout) is archived instead of the PDF, because the report is
copyrighted and the project rule is to store locators and permitted transcriptions, not
re-published documents.
The Stats NZ "selected price indexes" raw CSV is 10.8 MB; the three rent series used are
archived as a filtered extract and the locator records the full file URL.

------------------------------------------------------------------
4. ACCESS ARROWS AND NON-BYPASS DECLARATION
------------------------------------------------------------------
- No login, paywall, CAPTCHA or rate limit was bypassed for any source in this stream.
- REINZ: the free media release and one public legacy PDF were used. The member-gated
  Monthly Property Report library and the Statistics Portal were NOT accessed.
- RBNZ pages returned HTTP 403 to this client and were not used.
- QV API and page are public and unauthenticated.
- Stats NZ pages render their content as an embedded JSON payload (div#pageViewData); the
  page HTML was retrieved and parsed. No browser automation, credentials or cookie tricks
  were used beyond a standard browser user-agent.

------------------------------------------------------------------
5. KNOWN GAPS, REVISIONS AND CAVEATS
------------------------------------------------------------------
a) No free continuous REINZ Auckland HPI series exists. REINZ publishes national levels in
   its free monthly release but regional levels only in the member-gated report. The REINZ
   observations retained here are July 2021, July 2022 and the September 2026 year-on-year
   percentage change. The continuous series therefore uses the QV index, which is labelled
   non-official throughout.
b) The QV index starts January 2007. The 2000-2006 part of the project evidence window is
   NOT covered by any free price series located in this stream. A 20-year real-growth window
   to 2026 is therefore not computable; 19 years (Sep 2007 to Sep 2026) is the longest.
c) National CPI is not an Auckland-specific deflator. Auckland housing costs (rates,
   insurance, construction) have run above national CPI at times.
d) QV values are average equalised values, not median sale prices. REINZ medians and QV
   averages are different measures and must not be substituted for each other. In July 2022
   the REINZ Auckland median was $1,100,000 while the QV average equalised value was
   $1,410,163 - a 28.2% gap that reflects definition (average vs median), not a data error.
e) The HILS release for the year ended June 2025 carries a Stats NZ correction notice
   (29 September 2026): household-income measures for that year are affected by errors and
   corrected figures are due with the year-ended-June-2026 release in 2027. The Auckland
   income levels used here are the published provisional values.
f) MBIE states that bond data migration since 2020 leaves recent data provisional and that
   recent periods may not be directly comparable with earlier ones.
g) Rents from MBIE bonds are new-bond medians; the Stats NZ monthly rent index is a
   broad-region index with separate flow (new tenancies and changes) and stock measures.
   Neither is an Auckland-wide average rent for all tenancies.
h) QV's nominal peak is January 2022; REINZ's national peak is November 2021 (per the REINZ
   July 2022 report). Peak dating differs by index and by region; each peak used here is
   stated with its month and source.
i) Council rates and insurance indicators here are national CPI class indexes, not Auckland
   Council rate schedules or insurer premiums. They show price movements for those classes.
j) All REINZ and QV recent months are provisional and subject to revision.
k) A consistent 2000-2026 census/HES median HOUSEHOLD income series for Auckland was not
   retrievable from free sources in this stream: the income observations available are 2023
   (IDI), 2023 (Census, personal income and rent) and 2025 (HILS). Price-to-income over time
   is therefore thin; the current ratio is well founded but the historical path is not.

------------------------------------------------------------------
6. REPRODUCTION
------------------------------------------------------------------
Every derived number in evidence/streams/price/claims.csv states its numerator, denominator,
deflator and window in the computation column, and can be recomputed from the files in this
directory with plain arithmetic (no modelling):
  real index        = qv index / CPI of the month's quarter
  real change       = real_T / real_t0 - 1
  gross yield       = bond median rent x 52 / qv average value
  price-to-income   = qv average value / median household income
  nominal change    = index_T / index_t0 - 1
