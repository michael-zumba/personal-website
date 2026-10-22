AI-capital boom, global transmission and historical analogues - data methodology
Project: research-briefs/auckland-property-without-mortgage
Stream: ai-evidence. Access date for all sources: 2026-10-22 (Pacific/Auckland).
Author: evidence stream (no report prose). Units are stated in every file; "USD bn" means
billions of US dollars, "NZD bn" means billions of New Zealand dollars.

FILES
  ai_capex.csv             cash capex by firm, annual FY2015-FY2026 and quarterly 2019Q1-2026Q2
  market_concentration.csv S&P 500 concentration, Shiller CAPE, Nasdaq drawdowns, Fed AI-risk survey
  ai_credit.csv            AI-related capex projections and credit/private-credit shares
  nz_transmission.csv      NZ exchange rate, Super Fund, KiwiSaver, migration, credit-to-GDP, OCR
  historical_analogues.csv episode anchors: dot-com 2000-02, GFC 2007-11, 1970s-80s inflation,
                           2020 pandemic, 2021-2026 housing downturn
  build_ai_capex.py        downloads SEC XBRL company facts and writes ai_capex.csv + SEC snapshots
  build_ai_panels.py       downloads BIS/World Bank/Nasdaq/SPY/Shiller/multpl sources, archives
                           snapshots, and writes the four other tidy CSVs
  write_ai_ledgers.py      writes evidence/streams/ai/sources.csv and claims.csv
  build_ai_capex.py --snapshot-dir ../../../evidence/snapshots/ai
  build_ai_panels.py --snapshot-dir ../../../evidence/snapshots/ai --out-dir .
  write_ai_ledgers.py

CAPEX METHOD
  Source: SEC EDGAR XBRL company facts API (https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json).
  Concept: us-gaap:PaymentsToAcquirePropertyPlantAndEquipment, except Amazon and NVIDIA whose
  current cash-capex tag is us-gaap:PaymentsToAcquireProductiveAssets (the PP&E tag has no
  entries after 2017 for Amazon and after 2020 for NVIDIA). Older-tag 10-K annual values are
  used as a fallback only where the current tag has no annual value (Amazon FY2015).
  Facts are deduplicated by (start,end), keeping the latest-filed value. Each value carries
  the accession number and form type of the filing.
  Annual values: as-filed 10-K 12-month facts only. 12-month facts tagged inside 10-Qs are
  trailing-twelve-month figures and are excluded.
  Quarterly values: as-filed 3-month facts (Q1-Q3), Q4 = FY annual minus sum of Q1-Q3. The
  note column records whether a quarter is as-filed or derived.
  Fiscal years follow each company's own year: Microsoft ends 30 June, Oracle 31 May, NVIDIA
  late January, the others 31 December. Fiscal-year labels are the calendar year in which the
  fiscal year ends. The six-firm sums are therefore not single-calendar-year totals; this is
  stated wherever a sum is used.
  Validation: Q1+Q2+Q3+Q4 equals the as-filed annual value for every firm-year with four
  reported quarters (checked in build; zero mismatches).

MARKET DATA METHOD
  Nasdaq Composite: official Nasdaq historical API, six date-range requests, 1998-01-01 to
  2026-10-20; drawdowns are trough close / peak close - 1 within the stated dates.
  S&P 500 concentration: State Street SPY daily holdings XLSX, "As of 20-Oct-2026"; the top-10
  weight is the sum of the ten largest constituent weights; NVIDIA weight is the single row
  weight. The S&P DJI factsheet host returned HTTP 403, so the ETF holdings file is the official
  substitute (documented limitation).
  Shiller CAPE: Yale ie_data.xls (last observation 2023-09 in the retrieved file) plus the
  multpl.com monthly table for the current reading (non-official reprint; not load-bearing).
  Federal Reserve survey: share of surveyed contacts citing AI as a salient risk, FSR Nov 2025 p.11.

AI CREDIT, NZ TRANSMISSION AND PUBLICATION FIGURES
  Values taken from PDF/HTML publications are transcribed by hand from the stated page or
  section and recorded in claims.csv with the exact locator. Estimates produced by banks or
  consultancies and quoted inside official reports (Barclays, JP Morgan, OECD) are labelled
  as estimates in the ai_credit.csv note column. No paywalled or login-protected source was
  used. IMF and BIS AER PDFs were retrieved via Internet Archive snapshots of the official
  URLs because direct access returned HTTP 403; this is recorded in sources.csv.

BIS SERIES (official statistics API, free)
  WS_SPP Q.NZ...             residential property prices, quarterly 1970-Q1 to 2026-Q2
                             nominal (VALUE=N) and real (VALUE=R), index 2010=100 (UNIT=628)
  WS_EER M.N.B.NZ / M.R.B.NZ effective exchange rates, monthly, nominal/real broad
  WS_LONG_CPI M.NZ.628       consumer price index, monthly from 1960
  WS_CBPOL D.NZ              central bank policy rate, daily 1985-01-04 to 2026-10-09
  WS_CREDIT_GAP Q.NZ.P.A.A   credit-to-GDP ratio, NZ private non-financial sector, quarterly
  World Bank SL.UEM.TOTL.ZS  unemployment, annual 1991-2025, modelled ILO estimate

DEFLATORS, WINDOWS AND COMPUTATIONS
  Real house prices use the BIS real index (VALUE=R), so no separate deflator is applied in
  this stream. Peak-to-trough windows are stated in the data and claim rows. CPI inflation is
  the 12-month percent change of the BIS long CPI index. The policy rate path uses the BIS
  central bank policy rate (OCR from 17 March 1999; overnight cash rate before that).
  No missing observation is filled or replaced with zero.

KNOWN LIMITATIONS AND GAPS (see evidence/streams/ai/NOTES.md)
  RBNZ FSR/statistics and TWI inaccessible (HTTP 403); NZ bank offshore funding share and
  wholesale spreads therefore not verified. Stats NZ terms-of-trade release not located;
  recorded as a gap. Forward P/E not available from a free official source. AI capex as a
  share of GDP/investment not compiled (US national accounts hosts unreachable). World Bank
  unemployment starts 1991, so no 1970s-80s unemployment anchor.
