CREDIT / LEVERAGE / POLICY DATA - METHODOLOGY
Project: auckland-property-without-mortgage
Stream: credit-evidence (task-2). Data accessed 2026-10-22 (Pacific/Auckland).
All currency is NZD; percentages are % pa for rates and % for shares/ratios; differences are
percentage points (pp). Sources are identified by source_id; see evidence/streams/credit/sources.csv.

ACCESS NOTE
rbnz.govt.nz returns HTTP 403 to this network. All RBNZ tables below were retrieved from Internet
Archive captures of the exact official URLs (web.archive.org/web/20261022id_/<official-url>) and saved
as CSV transcriptions of the published XLSX 'Data' sheet under evidence/snapshots/credit/. The XLSX
originals are in data/raw/credit/raw/. Bank GDS PDFs, IRD, legislation.govt.nz and HUD were fetched directly.

FILE SUMMARIES
1. mortgage_rates.csv (monthly, 2000-01 to 2026-08)
   month: YYYY-MM (month end).
   ocr_percent: OCR in effect at month end. Source S_CREDIT_RBNZ_B2_20261022 where available (Jan 2018-Sep
     2026 series INM.MP1.N.nae); earlier months from the RBNZ 'Past monetary policy decisions' table
     (S_CREDIT_RBNZ_OCR_DECISIONS_20261022) = level after the last decision on or before month end.
     Cross-check: B2 monthly OCR equals the decisions-derived value for every month both cover.
   floating_standard_b20_percent / one_year_standard_b20_percent / two_year_standard_b20_percent /
     five_year_standard_b20_percent: B20 advertised ('carded') standard new-customer rates, simple average
     across banks, % pa, end of month. Series MTGE.MBI.F, MTGE.MBI.T09, MTGE.MBI.T10, MTGE.MBI.T13.
     Available Dec 2004 onward; blank before that.
   floating_new_customer_b3_percent: B3 weighted advertised floating first-mortgage new-customer housing rate
     (INR.MBI06.F); six_month_term_deposit_b3_percent: B3 six-month term deposit rate (INR.MBI05.T07).
   weighted_new_floating/1yr/2yr_b30_percent: B30 weighted-average interest rates on NEW residential mortgage
     lending (NCFA.MAM1PR.A/.D1/.D2), Apr 2021-Nov 2025 only.
   source_ids: semicolon-separated source IDs used for the row.

2. household_debt.csv (quarterly, 1998Q4 to 2026Q2)
   All stocks NZD million; ratios %.
   household_financial_liabilities_nzd_m: C21 HHAL.QB (fallback C22 HHAL.QB).
   housing_loans_nzd_m: C21 HHAL.QB11 (fallback C22 HHAL.QB11).
   household_disposable_income_quarter_nzd_m: C21 HHAL.QC4; annual: C21 HHAL.QC4rt12 (year-ended).
   debt_to_disposable_income_percent: C21 HHAL.QR2 AS PUBLISHED by RBNZ (household financial liabilities as a
     percentage of household disposable income). Discontinued after 2021Q2 - blank thereafter. This is the
     RBNZ definition in the C21 table, not the current RBNZ household debt-to-income (HHDTI) series.
   interest_payments_nzd_m / housing_interest_payments_nzd_m: C21 HHAL.QD2.ZZH / HHAL.QD2.ZZH1.
   interest_payments_percent_of_disposable_income: C21 HHAL.QR7.ZZH as published. Discontinued 2021Q2.
   net_wealth_percent_of_disposable_income: C21 HHAL.QR6.
   investor_share_new_mortgage_lending_percent: C31 investors / all borrower types x 100, using the month
     that ends the quarter (LVRN.MMB1.AN / LVRN.MMB1.AA).
   bank_housing_loans_s50_nzd_m: S50 BSAQS.MPA6A4.P1 at the quarter-end month (2018-2025).
   Note: C21/C22 were discontinued by RBNZ in Dec 2021 and replaced by Stats NZ institutional-sector accounts.

3. arrears_bank.csv (quarterly, 2008Q4 to 2026Q2)
   Housing loan figures from S50 at the quarter-end month unless noted.
   housing_loans_total/90d_past_due/impaired/npl_nzd_m and housing_npl_ratio_percent: S50 series
     BSAQS.MPA6A4.P1, BSAQS.MPA4A4.P1, BSAQS.MPA5A4.P1, BSAQS.MPR1A4.P1, BSAQS.MPR2A4.P1 (published ratio).
   housing_npl_ratio_longrun_percent, total_npl_ratio_percent: S50 long-run BSAQS.MAR2A4.P1 / BSAQS.MAR2A4.P
     (monthly, Dec 2008-Nov 2025; included for GFC comparison).
   tier1_capital_ratio_percent: FSR May 2026 Table 4.1, end-March values 2022-2026 (only Q1 rows populated).
   core_funding_ratio_percent: L2 LIQ.MBA7.ZZZZZR4 at quarter-end month (2010-2025), or FSR Table 4.1 for
     March years 2022-2026 (FSR value used where both exist).
   offshore_funding_share_percent: L3 offshore market funding LIQ.MBF212 / total funding LIQ.MBF x 100.
   one_month_mismatch_ratio_percent: FSR Table 4.1.
   ocr_percent, ninety_day_bank_bill_percent, bank_bill_over_ocr_spread_bp: B2, month-end; spread =
     (bill - OCR) x 100, basis points.
   PRE-2018 GAP: S50 starts Mar 2018. The long-run file supplies NPL RATIOS only from Dec 2008; dollar
   arrears, capital and funding ratios are blank before the series start.

4. bank_margins.csv (long format: period, period_end, institution, metric, value, unit, computation, source_id)
   net_interest_margin: RBNZ S20 ISSR.QAQC, quarterly 2000Q1-2025Q3. Definition D3 = net interest income /
     interest-earning assets. This is an accounting spread, NOT excess profit.
   net_interest_margin_12m_running, return_on_assets, return_on_equity: FSR May 2026 Table 4.1, end-March
     2022-2026.
   Bank-level (ANZ, BNZ, Westpac NZ) at 31 March 2026 from GDS: net_interest_income (6 months, NZDm);
     nii_to_average_total_assets_proxy = NII x 2 / average(total assets 31 Mar 2026, 30 Sep 2025) x 100,
     an author proxy because GDS do not publish NIM and total assets are not interest-earning assets;
     cet1_capital_ratio = GDS capital adequacy (banking group). Kiwibank/ASB were not extracted (time cap).
   housing_loan_yield: B6 INRY.MAA145, quarterly average of monthly values; housing_yield_minus_deposit_cost:
     B6 INRY.MAA145 - B7 INRY.MAB11 (quarterly averages; months may not coincide at the end of the B7 series).
   two_year_standard_mortgage_minus_2y_swap / floating_standard_mortgage_minus_90day_bill: B20-B2 same
     month-end; indicative gross spreads between advertised rates and wholesale benchmarks, not profit.

5. policy_timeline.csv
   date (effective date unless stated), policy_name, setting_value, expected_direction (EXPECTATION ONLY,
     not an estimated effect), source_id, exact_locator, notes. Settings are as stated by the cited source;
   no causal attribution is made. Gaps: CCCFA, earlier bright-line periods, 2015-2016 investor LVR specifics,
   Auckland Council rates/insurance context (see NOTES.md).
