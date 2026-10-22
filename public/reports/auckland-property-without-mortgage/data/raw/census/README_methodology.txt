CENSUS EVIDENCE STREAM - RAW DATA METHODOLOGY
Project: auckland-property-without-mortgage
Prepared by: census-evidence (teammate)
Access date: 2026-10-22 (Pacific/Auckland)
Location: data/raw/census/

These tidy CSVs feed dimension 4 (generational tenure and preference change). Every value is either copied from a published Stats NZ table/figure or is an explicit, documented calculation. No value is estimated, interpolated or reconstructed. Missing values are left blank (never zero).

FILES

1) ownership_by_age.csv
Columns
  census_year        Census year of the observation (1991-2023; 2006/2013/2018/2023 for age bands).
  geography          "New Zealand" or "Auckland Region".
  age_band           "15-19" ... "85+", or "Total".
  measure            individual_home_ownership_tenure_holder   = person-level ownership from QuickStats Table 21 (2006, 2013; counts + rates).
                     individual_home_ownership                  = person-level ownership from HIA 2025 figure 2.7 (2013, 2018, 2023; rates only).
                     household_tenure                          = household-level tenure (QuickStats Table 13, Auckland tables Table 10, HIA figure 2.2, 2023 news release).
  tenure_status      Ownership category. For person-level series: owned_or_partly_owned_or_held_in_family_trust. For household series this is either the combined ownership category or the specific tenure class from figure 2.2.
  count              Published numerator where available (blank where the source publishes rates only).
  denominator_count  Published denominator where available.
  rate_percent       Published percentage. Where a rate would otherwise have to be recomputed from rounded counts, the published rate is used.
  denominator_definition  Exact subject population, including any exclusion of "not elsewhere included".
  source_id          Source ledger ID (evidence/streams/census/sources.csv).
  notes              Table/figure, row/filter, and any rounding or comparability note.

Coverage and filters
  - 2006 and 2013 person-level rates/counts: 2013 Census QuickStats about housing, Table 21, age groups 15-19 ... 85+, "Total people stated" excluding not-elsewhere-included (S_CENSUS_004). Counts are the "Own or Partly Own Usual Residence" counts, rates are the published percentages.
  - 2018 and 2023 person-level rates: Housing in Aotearoa New Zealand: 2025 data package, figure_2_7.csv, rows Year=2018/2023 by age group (S_CENSUS_002). Rates only. 2013 is duplicated from figure_2_7 to document that it matches Table 21 exactly.
  - Household tenure New Zealand 1991-2013: 2013 QuickStats Table 13 (S_CENSUS_004); numerator for 2006-2013 = owned households + households held in a family trust; 1991-2001 use the published rate because family-trust data did not exist before 2006.
  - Household tenure New Zealand 2018: 2018 Census totals by topic Table 56 (S_CENSUS_022); numerator = codes 10+11+12+30+31+32; denominator = "Total households stated" 1,653,060. Component sums differ from the published combined count by 3 due to fixed random rounding; the published rate 64.5% is used.
  - Household tenure New Zealand 2023 and 2018: 2023 Census news release "Home ownership increases and housing quality improves" (S_CENSUS_008), published rates.
  - Auckland region and New Zealand household rates 1986-2013: "Dwelling and tenure type tables for Auckland", Table 10 (S_CENSUS_006), published percentages and percentage-point changes.
  - Auckland 2018 and 2023 household rates: same 2023 news release (S_CENSUS_008).
  - Auckland/regional not-owned shares 2013-2023: HIA 2025 figure_2_12 (S_CENSUS_002).
  - Tenure composition 2013-2023: HIA 2025 figure_2_2 (S_CENSUS_002).
  - Household tenure detail (owned with/without mortgage, family trust with/without mortgage, not owned with/without rent payments): 2006 and 2013 counts from QuickStats Table 13 (S_CENSUS_004), 2018 counts from totals by topic Table 56 (S_CENSUS_022), with rates computed on "total households stated". These rows use measure = household_tenure_detail. Published cross-checks: 2018 owned-with-mortgage 27.8% and rent-payments-made 31.9% match the 2018 totals-by-topic text.
  - Not available: Auckland region tenure by age band (Aotearoa Data Explorer cross-tabulation requires an API subscription key; not accessed). See NOTES.md.

2) migration.csv
Columns
  period_type   rolling_year_ended or month.
  period        Rolling years labelled "Dec-2001" ... "Aug-2026" (year ended on that month); months labelled "Jan-2001" ... "Aug-2026".
  measure       migrant_arrivals, migrant_departures, net_migration.
  value         Persons.
  unit          persons.
  status        final or provisional. Outcomes-based estimates from May 2025 onward are provisional and revised monthly until finalised after 16 months.
  geography     New Zealand (no regional breakdown is published in the release).
  source_id     S_CENSUS_015 for the release page chart data.
  notes         Transcription method and figure reference.

Method
  - Values were transcribed from the machine-readable chart data embedded in the International migration: August 2026 release page: figure g1 (rolling-year arrivals/departures/net, 297 periods) and figures g4/g5 (monthly arrivals, departures, net, 308 months). These are the same estimates published in the downloadable XLSX (S_CENSUS_016); spot checks: August 2026 year net 20,503 (published rounded 20,500), August 2025 year net 9,200 (rounded), October 2023 year net 133,700 (rounded), annual arrivals peak 232,900, annual departures peak 120,500, August 2026 month arrivals 10,199/departures 8,005/net 2,193 (published rounded 10,200/8,000/2,200).
  - National only. The release and its Tables 1-8 contain no regional migration table, so there is no Auckland row; this is recorded as a gap rather than proxied.

3) first_home_buyers.csv
Columns
  period, geography, buyer_group, metric, value_numeric, value_published, unit, basis, source_id, notes.
  - Shares and ages are from Cotality (formerly CoreLogic) buyer-classification commentary, an industry source, not an official statistic and not REINZ buyer classification. Published wording such as "nearly 25" or "more than 27" is retained in value_published; value_numeric is populated only where an exact number is published.
  - REINZ buyer-classification data could not be verified from a free public source and is not used.

4) household_formation.csv
Columns
  census_year, geography, measure, value, unit, denominator_definition, source_id, notes.
  - Occupied and total private dwellings, average household size, families with adult children, growth in family counts, child-role shares at ages 18/20/25/30, crowding rates, mean years at usual residence by tenure, and households renting.
  - Child-role shares are from HIA 2025 figure_2_11 (S_CENSUS_002); years at usual residence from figure_2_19 (S_CENSUS_002); crowding, dwelling counts and the 2023 senior/rental context from the HIA 2025 report (S_CENSUS_001); household size, adult-children families and family growth from the Families, households, and housing: 2023 Census release (S_CENSUS_009); 2013 average household size from A century of censuses (S_CENSUS_014); households renting from the 2023 Census highlights (S_CENSUS_007).

5) attitudes.csv
Columns
  survey_date, survey_organisation, geography, question_wording, result_label, result_percent, sample_size, sample_description, representativeness, measure_type, source_id, notes.
  - Ipsos New Zealand Issues Monitor, 34th wave: fieldwork 3-11 September 2026, n=1,003 New Zealanders aged 18+, online sample, credibility interval +/-3.5 percentage points (S_CENSUS_020). The question asks for the three most important issues facing New Zealand; the percentages therefore do not sum to 100 and measure issue salience, not tenure preference.
  - Stats NZ General Social Survey 2023 (through HIA 2025 figure_2_22, S_CENSUS_002): satisfaction with suitability of home and location by tenure; sample size is not stated in the figure data, and published errors are +/-0.6 (owners) and +/-1.2 (not owned) percentage points. This measures preference for a more suitable home, not a preference to own versus rent.

RULES APPLIED
  - Every claim in evidence/streams/census/claims.csv cites one source and an exact locator; every percentage states or locates its numerator and denominator.
  - Published rates are preferred to recomputed rates. Where a rate is recomputed, the computation is in the claims ledger.
  - No preference change is inferred from tenure. See claims C_CENSUS_062 and the NOTES section "What this stream can and cannot settle".
  - Percentages are stored to the precision published (mostly 0.1 percentage point); counts are integers as published and may be randomly rounded to base 3.

VALIDATION PERFORMED (2026-10-22)
  - Every CSV parses with Python's csv module and has a unique header row.
  - Table 21 counts/rates checked against the published table: 2006 age 25-29 count 51,528, rate 22.9; 2013 age 30-34 count 87,165, rate 36.0; totals 1,578,081 (2006) and 1,590,546 (2013).
  - Table 13 counts checked: 2006 owned 743,952, trust 167,922; 2013 725,448, 215,280; stated 1,363,842 (2006), 1,452,837 (2013).
  - Table 10 rates checked: Auckland 2006 63.8, 2013 61.5; New Zealand 2006 66.9, 2013 64.8.
  - 2018 Table 56 counts checked: 459,414 (owned with mortgage), 527,853 (rent without trust), 87,663 (trust with mortgage); total households stated 1,653,060.
  - Figure 2.7 rates checked: 2013/2018/2023 age 30-34 = 36.0/39.0/37.4; totals 49.8/51.8/51.3.
  - Migration chart data checked: 297 rolling-year periods and 308 monthly periods per measure; Aug-2026 and Aug-2025 published values reproduced after publication rounding.
