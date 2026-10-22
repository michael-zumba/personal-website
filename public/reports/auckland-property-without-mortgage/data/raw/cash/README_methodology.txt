# Cash, inflation and safe-asset data: methodology note

Project: auckland-property-without-mortgage (evidence stream: cash)
Author of stream: cash-evidence (research support for Dr Yuqian Zhang)
Access date: 2026-10-22 (Pacific/Auckland)
Output location: `data/raw/cash/`

This note documents every compiled series, its exact source and series ID, the transformations
applied, and the known gaps. It is written so the Python replication script can rebuild every
derived number from the published CSVs without re-downloading anything.

## 1. Files

| File | Contents | Frequency | Coverage |
| --- | --- | --- | --- |
| `cash_rates.csv` | OCR, 90-day bank bill, weighted-average 6-month term deposit rate, 1-year term deposit rate | monthly | 2000-01 to 2026-09 |
| `inflation.csv` | CPI all groups index, quarterly and annual percentage change | quarterly | 2000-Q1 to 2026-Q3 |
| `cash_returns.csv` | After-tax real returns on 6-month and 1-year term deposits at four marginal rates | monthly | 2000-01 to 2026-08 |
| `deposit_protection.csv` | Depositor Compensation Scheme: start date, cap, coverage | event | 2025-07-01 |
| `historical_episodes.csv` | Official series values for 1987-91, 1997-98, 2008-11 and 2020, plus after-tax real returns | event | 1986-2026 |
| `stress_tests.csv` | RBNZ and IMF stress-test scenarios and results used as scenario anchors | publication | 2017-2025 |
| `tax_rates.csv` | Personal marginal income tax brackets, 2024-25 to 2026-27 | tax year | 2024-2027 |
| `README_raw.txt` | Inventory of raw downloaded files retained in `raw/` | - | - |

## 2. Sources and access route

### 2.1 RBNZ statistics (S_CASH_001, S_CASH_002, S_CASH_003)

Direct requests to `www.rbnz.govt.nz` from this host return **HTTP 403** (both `curl` with a browser
user agent and `web_fetch`). The blocking page states that access has been restricted. No login,
paywall or access control was bypassed. Instead, the official data files were retrieved from
**Internet Archive Wayback Machine captures of the exact official URLs**:

| Source | Official data file | Wayback capture (UTC) |
| --- | --- | --- |
| S_CASH_001 Wholesale interest rates (B2) | `.../statistics/series/b/b2/hb2-monthly-close.xlsx` (published 2026-10-01) | 2026-10-15T09:28:31Z |
| S_CASH_001 (pre-2018 history) | `.../statistics/series/b/b2/hb2-daily-close-1985-2017.xlsx` | 2026-09-28T18:32:19Z |
| S_CASH_002 Retail interest rates (B3) | `.../statistics/series/b/b3/hb3.xlsx` (published 2026-09-07) | 2026-09-30T02:08:21Z |
| S_CASH_003 Term deposit rates (B26) | `.../statistics/series/b/b26/hb26.xlsx` (published 2026-10-07) | 2026-10-15T09:26:47Z |

Exact series IDs (as printed in the `Series Id` row of each workbook's `Data` sheet):

- OCR: `INM.MP1.N.nae` (monthly, 2018-01 to 2026-09) and `INM.DP1.N` (daily, 1999-03 to 2017-12).
- 90-day bank bill: `INM.MB03.NZZF` (monthly, 2018-01 to 2026-09) and `INM.DB03.NZZV` (daily,
  2009-01 to 2017-12).
- Six-month term deposit rate: `INR.MBI05.T07` (monthly, 1965-03 to 2026-08). RBNZ definition:
  weighted-average rate on new term deposits (B3 retail interest rate survey).
- One-year term deposit rate: `INRD.MAD52.D1` (monthly, 2017-01 to 2026-09). RBNZ definition:
  simple average of new term deposits of $10,000 or more with a maturity greater than one day.

Daily observations are converted to month-end by taking the **last available observation in each
calendar month**; no averaging or interpolation is used. Merging of the 1999-2017 daily file and the
2018-2026 monthly file is a documented splice at December 2017 / January 2018; both are the same
official series (OCR and 90-day bank bill) for the same instrument.

### 2.2 Stats NZ (S_CASH_004, S_CASH_005, S_CASH_013)

Direct downloads (HTTP 200), no access restriction.

- CPI: release "Consumers price index: September 2026 quarter", data file
  `consumers-price-index-september-2026-quarter-index-numbers.csv`, series **`CPIQ.SE9A`**
  ("CPI All Groups for New Zealand", Index, quarterly, national). The release page (S_CASH_013)
  reports the headline: **+0.7 percent in the September 2026 quarter and +3.7 percent in the
  12 months to September 2026**, released 2026-10-22; next update 2027-01-27.
- Unemployment: release "Labour market statistics: June 2026 quarter" (published 2026-08-05),
  series **`HLFQ.SEFS`** (seasonally adjusted unemployment rate, total, both sexes, quarterly,
  1986Q1 to 2026Q2). Extracted from the 423 MB release CSV; only the 162-quarter series is retained.

### 2.3 Inland Revenue (S_CASH_006)

Direct fetch of the IRD "Tax rates for individuals" page. The page lists the schedule **"From
1 April 2025"** and the transitional schedule **"From 1 April 2024 to 31 March 2025"**. The page
also lists interest from a bank account or investment as income that is taxed at the progressive
personal rates. The page shows only the current and one prior tax year; earlier schedules are not
compiled in this stream.

### 2.4 Reserve Bank and IMF stress-test publications (S_CASH_007 to S_CASH_012)

All retrieved from Internet Archive captures because direct access returns HTTP 403
(imf.org also returns 403). Capture timestamps are recorded in `evidence/streams/cash/sources.csv`.

- S_CASH_007: RBNZ briefing "Update: Depositor Compensation Scheme Implementation", dated 12 June
  2025, released under the Official Information Act. States: scheme under Part 6 of the Deposit
  Takers Act; compensation **up to $100,000 per deposit taker**; implementation **1 July 2025**;
  funded by levies on deposit takers; RBNZ administers.
- S_CASH_008: RBNZ Financial Stability Report, November 2024, Chapter 2 Special Topic 1
  (2024 Reverse Stress Test) and footnote 18 (2020 COVID-19 Very Severe Scenario).
- S_CASH_009: RBNZ Bulletin Vol. 88, No. 3 (May 2025), 2025 bank industry solvency stress test
  scenarios; Table 2 (scenario paths) and Table A1 (severity benchmarks).
- S_CASH_010: RBNZ Bulletin Vol. 88, No. 11 (3 November 2025), 2025 stress test results.
- S_CASH_011: IMF Country Report No. 17/119 (May 2017), FSAP Technical Note: Stress Testing the
  Banking Sector and Systemic Risk Analysis.
- S_CASH_012: RBNZ Financial Stability Report, May 2026, presentation slides (qualitative only).

## 3. Derivations

### 3.1 Real returns (Fisher relation, exact form)

For a nominal annual rate `i` (percent per annum) and annual CPI inflation `pi` (percent):

```
real_pre_tax      = ((1 + i/100) / (1 + pi/100) - 1) * 100
after_tax_nominal = i * (1 - t)                      # t = marginal tax rate, decimal
real_after_tax    = ((1 + after_tax_nominal/100) / (1 + pi/100) - 1) * 100
```

`cash_returns.csv` reports the real return before tax and at marginal rates of **17.5, 30, 33 and
39 percent**. The inflation deflator is the **CPI all groups annual percentage change** for the
quarter containing the month (national CPI, `CPIQ.SE9A`). The nominal rate is the six-month
weighted-average term deposit rate (`INR.MBI05.T07`); the 1-year series (`INRD.MAD52.D1`) is
provided as extra columns.

The tax treatment assumed is NZ resident withholding tax at the investor's marginal rate applied to
the **nominal** interest amount; there is no inflation indexation of interest income. The marginal
rates are the current (2025-26 / 2026-27) statutory rates. **No claim is made that these were the
applicable marginal rates in every earlier year**; the historical series is an "as if current
schedule applied" calculation and is labelled as such wherever it is used.

### 3.2 CPI percentage changes

Quarterly change = index(t)/index(t-1) - 1; annual change = index(t)/index(t-4) - 1, using
`CPIQ.SE9A` index numbers. The index is published to one decimal place, so derived changes can
differ from Stats NZ's published rounded figures in the second decimal (e.g. computed 0.66 vs
published 0.7 percent q/q for September 2026).

### 3.3 Historical episodes

For each episode window the table reports the peak (or trough) of each official series within the
window, the quarter or month of that peak, and two after-tax real return calculations for the
six-month term deposit rate: one at the term-deposit-rate peak and one at the CPI peak. The exact
members and formulas are in the `notes` column of `historical_episodes.csv`. Episode windows:
1987-1991, 1997-1998, 2008-2011 and 2020. Windows are pre-specified (contract annex), not chosen
after seeing the numbers. Where an unemployment peak recurs (6.8 percent in both 2009Q4 and
2010Q2), the last occurrence is shown and the tie is stated in the notes.

### 3.4 Stress-test table

`stress_tests.csv` records, for each published RBNZ or IMF exercise: publication date, institution,
test name, scenario label, the scenario's unemployment peak, house-price and commercial-property
declines, GDP decline, CPI and cash-rate peaks, cumulative credit-loss measure, capital results and
other reported results, with the source ID and locator notes. Values are transcribed from the
publications; no scenario values are invented or extrapolated. Ranges are reported as ranges.

## 4. Known gaps and limitations

1. **RBNZ direct access blocked.** All RBNZ material was retrieved from Internet Archive captures of
   official URLs. Captures are recent (September-October 2026) but each series ends at the
   publication vintage shown above.
2. **90-day bank bill missing 2000-2008.** The archived RBNZ B2 daily file contains bank bill yields
   only from January 2009; the earlier file has no bank bill columns. No other official 90-day bank
   bill series was verified in this stream, so the 90-day bill column is blank before 2009-01. OCR is
   available continuously from 1999.
3. **1-year term deposit rate only from 2017.** The B26 table begins January 2017. The 6-month rate
   (B3) is available from 1965 and is the series used for the long-run comparisons.
4. **Tax history not compiled.** Only the 2024-25, 2025-26 and 2026-27 schedules are recorded. The
   after-tax historical series applies current marginal rates as a constant assumption; it is not a
   reconstruction of each year's statutory schedule.
5. **Deflator is national, not Auckland-specific.** The contract specifies the national CPI as the
   deflator; Auckland housing costs (rates, insurance, construction) are not represented in it.
6. **House price change is not in this stream.** Historical house-price falls for the 1987-91,
   1997-98, 2008-11 and 2020 episodes are owned by the real-prices evidence stream (REINZ HPI).
   This stream did not verify an official historical house-price series and does not report one.
7. **Deposit insurance detail.** The RBNZ briefing states the $100,000 cap and start date but does
   not itemise every eligibility exclusion. The report must not describe the scheme as covering all
   deposits or all institutions, and must not call cash risk-free.
8. **Stress scenarios are hypothetical, not forecasts.** The RBNZ and IMF scenarios are labelled
   stress tests; the 2025 RBNZ test covers the five largest banks and reports results before
   mitigating actions. The IMF FSAP is a 2017 vintage that pre-dates current NZ capital settings.
9. **Vintage/revision risk.** Stats NZ series are revised; snapshots are the June 2026 (HLFS) and
   September 2026 (CPI) quarter release vintages. RBNZ series are as published on the dates shown.

## 5. Reproduction

Every derived column can be rebuilt from the CSVs: `inflation.csv` supplies the deflator,
`cash_rates.csv` the nominal rates, `cash_returns.csv` the computed real returns, and
`historical_episodes.csv` the episode peaks and after-tax returns (with the formula recorded in the
`notes` column). The raw downloaded source files are retained in `raw/` for traceability.
