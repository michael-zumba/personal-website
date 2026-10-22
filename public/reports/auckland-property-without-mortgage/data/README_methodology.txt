Auckland Property, Cash and the AI Bubble

Methodology note and codebook
Author: Dr Yuqian Zhang
Access date: 22 October 2026 (Pacific/Auckland)
Project: research-briefs/auckland-property-without-mortgage
Data release: public/reports/auckland-property-without-mortgage/data/

1. Purpose

This note documents how the datasets behind the research brief were compiled, what
each variable means, how author calculations were made, and where the evidence stops.
It is a methods record, not a second report. The brief is research and not financial,
investment, legal or tax advice. It does not recommend that any reader buy, rent or
hold any asset.

2. Core definitions

Unleveraged buyer: a buyer who pays for a home without a mortgage.
Cash: New Zealand dollar deposits and cash-like instruments, not physical currency.
Real: adjusted for the consumers price index (CPI), all groups, national series.
Extreme scenario: a labelled stress test. It is not a forecast, a probability or a
prediction that the AI-capital boom will burst in 2027.
AI-capital boom: the rapid increase since 2022 in computing, data-centre, semiconductor
and related investment, with the equity valuations and debt financing attached to it.
Owning-versus-renting break-even rate: the real house-price growth rate at which an
owning position without a mortgage equals a renting position with the capital in cash.
It is derived in section 8.

3. Source hierarchy

Primary and operational sources are used first: SEC XBRL company facts and filings;
Stats NZ releases and series (CPI CPIQ.SE9A, census tenure tables, HILS, migration);
RBNZ statistics and Monetary Policy Statements accessed through Internet Archive
captures of the official URLs; MBIE Tenancy Services bond data; IRD tax schedules;
Quotable Value (QV) public HPI API; Treasury, IMF, BIS, OECD, Federal Reserve, Bank of
England and ECB financial-stability publications; bank general disclosure statements;
New Zealand Super Fund and FMA KiwiSaver releases. Non-official sources are labelled
where used: the QV index (a state-owned valuer, not the REINZ official statistic), the
Shiller CAPE reprint, Cotality first-home-buyer commentary, and market-implied values in
official reports. No login, paywall or access control was bypassed.

Every source is recorded in evidence/sources.csv with a stable ID, exact title,
organisation, date, URL, DOI where present, access date, verification method, exact
locator, archived snapshot path and limitations. Every material number is recorded in
evidence/claims.csv with the source, exact locator, unit, comparison type and any
computation. Archived snapshots live under evidence/snapshots/ and are hashed in
evidence/reference-check.json.

4. Price, rent and affordability data

4.1 Price levels. The continuous Auckland price series is the QV House Price Index
(API: qv.co.nz/api/hpi_data/AUCKLAND REGION), monthly, January 2007 to September 2026,
base January 2007 = 1000. It measures an average equalised residential value for the
Auckland region, not a median sale price. It is labelled non-official throughout. The
REINZ monthly property report and statistics portal were not freely available; the REINZ
September 2026 media release and one public July 2022 report are used as cross-reference
only and are never spliced onto the QV series.
The nominal peak is January 2022 (index 2,996.489). The CPI-deflated real peak is
December 2021 (real index 2,646.275). The September 2026 values are 2,254.2 nominal and
1,647.8 real. Peak-to-trough changes are measured from those observed peaks.

4.2 Deflator. CPI all groups, national, quarterly, base June 2017 quarter = 1000
(Stats NZ series CPIQ.SE9A). Monthly prices are deflated with the CPI for the quarter
that contains the month: real index = nominal index / CPI x 1000. The national CPI is
not an Auckland-specific deflator and its basket has changed over time.

4.3 Rent. MBIE Tenancy Services bond data, Auckland region, median weekly rent for
newly lodged bonds (August 2026: $650). The real rent change is computed as
(1 + nominal rent change) / (1 + CPI change) - 1. Between August 2021 and August 2026
the median bond rent rose 10.17 percent while consumer prices rose 23.69 percent, so
real rents fell about 10.9 percent. The Stats NZ monthly rent index (flow and stock
measures) is included for cross-reference. Bond medians since 2020 are provisional and
mix new tenancies only.

4.4 Affordability. Gross yield = (median weekly rent x 52) / average equalised value.
Price-to-income = average equalised value / median gross household income. The income
denominators are not interchangeable: the household income and housing-cost statistics release (HILS) for the year ended June 2025 ($130,595, provisional
with a Stats NZ corrections notice), the 2023 IDI estimate ($117,900), and the 2023
Census median personal income ($44,700) are different concepts. The 2026 price-to-income
ratio reuses the 2025 income because no 2026 observation exists, so it likely overstates
the ratio if incomes grew.

4.5 Ownership. Census 2006 and 2013 individual ownership rates come from the tenure-
holder table; 2018 and 2023 rates come from the individual home ownership figure data.
The 2013 rates match across both sources, which supports linking the series. Age bands
are cross-sectional, not cohorts followed over time. The 2011 Census was cancelled.
Family-trust treatment, questionnaire changes, random rounding and a 2023 derivation for
retirement villages mean small differences are not reliable. Auckland age-band tenure
is not available without an Aotearoa Data Explorer subscription key and is therefore a
documented gap, not an estimate.

5. Credit, cash and policy data

5.1 Mortgage rates. RBNZ B20 advertised standard rates, B3 weighted rates, B30 new-
credit weighted rates and the official cash rate. Series are taken from Internet Archive
captures of the official RBNZ data files because rbnz.govt.nz returned HTTP 403 to this
network. The mortgage rate is a price, not a spread or a profit measure.

5.2 Household debt and arrears. RBNZ C21/C22 household liabilities and disposable
income, C31 investor share, S50 housing loan and non-performing-loan series, S20 system
net interest margin, and L2/L3 capital and funding ratios. The official household debt-
to-disposable-income series was discontinued after 2021Q2 and is not spliced to the
Stats NZ replacement; the 2021Q2 ratio of 127 percent is a historical observation, not a
current one. Net interest margin is not excess profit. Investor share is a flow share of
new lending, not a share of the outstanding book.

5.3 Cash returns. RBNZ B3 six-month term deposit and B26 one-year rates, CPI and the
IRD marginal tax schedule. Real after-tax return =
((1 + nominal x (1 - tax)) / (1 + CPI change) - 1) x 100. The historical after-tax
series applies current marginal rates as a stated constant; it is not each year's
statutory schedule. The depositor compensation scheme pays up to $100,000 per depositor
per deposit taker from 1 July 2025; above that cap cash carries bank risk.

5.4 Policy timeline. Dated settings for the bright-line test, interest deductibility,
loan-to-value and debt-to-income limits, the foreign-buyer restriction, the First Home
Grant and the depositor compensation scheme. The expected direction column is an
expectation, not a measured effect; the report does not identify the causal effect of any
single policy.

6. AI-capital cycle data

6.1 Capex. Cash purchases of property, plant and equipment from SEC XBRL company facts
for Microsoft, Alphabet, Amazon, Meta, NVIDIA and Oracle, FY2015 to the latest reported
quarter, with the accession number and form type recorded for every value. Q4 values are
derived as the annual value minus the sum of the first three quarters and are flagged.
The chart uses the big four (Microsoft, Alphabet, Amazon, Meta) and states that fiscal
year ends differ.

6.2 Valuation and concentration. S&P 500 top-10 weight and NVIDIA weight from the
official SPY holdings file (20 October 2026); Shiller CAPE from the Yale data file and a
third-party monthly reprint; Nasdaq Composite drawdowns from the official index history.
The CAPE reprint is secondary and labelled. A forward P/E is not used because no free
official series was verified.

6.3 Credit. AI-related capital-expenditure projections, data-centre securitisation,
investment-grade and high-yield issuance shares, and private-credit shares from IMF,
BIS, Bank of England and ECB publications. Values published inside official reports but
attributed to banks or market intelligence are labelled as estimates in the claim ledger.

6.4 New Zealand transmission. BIS effective exchange rate and credit-to-GDP, KiwiSaver
and New Zealand Super Fund exposure, net migration and the official cash rate. The
report uses the latest rolling-year migration release (year to August 2026: net 20,500).
The transmission dataset separately records the June 2026 vintage obtained from the AI
evidence stream, so the two files differ by release date rather than by definition. RBNZ
offshore funding and wholesale spread data are taken from the credit stream; the AI
stream could not verify them. Terms of trade and forward P/E are documented gaps.

7. Historical and stress anchors

Historic episodes are taken from official series: BIS real residential property prices,
Stats NZ CPI and labour-market data, RBNZ rates, and World Bank modelled unemployment.
The dot-com, GFC, 1970s-80s inflation and 2020 anchors are used only to calibrate
assumption ranges, never as forecasts. RBNZ and IMF stress-test scenarios supply the
severity anchors: the RBNZ 2025 solvency stress test (unemployment 10.5 percent, house
prices -35 percent, credit losses 3.2 percent), the 2020 COVID-19 very severe scenario
(unemployment 17.7 percent, property -48 percent), the 2024 reverse stress test
(unemployment 8-18 percent, residential prices -30 to -55 percent) and the IMF 2017
FSAP adverse scenario (unemployment above 10 percent, house prices -40 percent).

8. Scenario matrix and owning-versus-renting break-even rate

The scenario matrix crosses three severities (AI correction, AI credit bust, systemic
AI unwind) with two regimes (disinflationary credit bust and inflationary funding
stress), plus a reference row for no unwind. Each cell states assumptions for global
equity change, AI capex change, New Zealand unemployment, cumulative CPI, Auckland
house-price change, rent change, term-deposit rate and deposit access. The assumptions
are author judgement anchored to the stress tests and episodes in section 7. They carry
no probabilities. Several channels cannot scale linearly: a tenfold repeat of the GFC
price fall would be a 100 percent fall, which is impossible, while unemployment and
credit losses can rise much further. The matrix therefore uses a bounded severity ladder
rather than a single multiplier.

Scenario outcomes are computed as:
- real house-price change = (1 + nominal change) / (1 + cumulative CPI) - 1.
- after-tax cash real change = (1 + deposit rate x (1 - tax)) / (1 + cumulative CPI) - 1.
- owner real position over two years = real house-price change + 2 x net shelter return.
- renter position over two years = 2 x after-tax cash real return.
The owner calculation excludes transaction costs and assumes the owner holds through the
period; a forced sale would reduce the owner position by up to the round-trip cost.

The owning-versus-renting break-even rate uses the same accounting. Net shelter return is gross
rent avoided minus ownership costs. With gross yield at 2.92 percent and assumed
ownership costs of 1.50 percent of value (rates 0.35, insurance 0.30, maintenance 0.85),
the net shelter return is about 1.42 percent of value a year. Owning beats renting plus
cash when real house-price growth exceeds:
cash real return - net shelter return + annualised transaction cost.
At the current after-tax cash return of about -0.97 percent the break-even rate is about
-2.4 percent a year before transaction costs; with a five percent round trip over ten
years it is about -1.9 percent a year, and over five years about -1.4 percent a year.
Using the long-run cash return of +0.46 percent a year, the break-even rate is about -1.0 percent
a year before costs. These values are sensitive to the ownership-cost and tax
assumptions and are presented as a framework, not a measurement.

9. Author calculations and derived datasets

All derived values are reproducible from the published CSVs:
- data/auckland_price_index.csv: real index and percentage from peak.
- data/affordability_yield.csv: gross yield and price-to-income.
- data/real_returns.csv: nominal and real totals, annualised real returns, five percent
  round-trip adjustment and window-specific mean cash real returns.
- data/cash_returns.csv: after-tax real returns at four marginal rates.
- data/credit_stress.csv: joined quarterly credit indicators.
- data/ai_capital_cycle.csv: chart-ready AI capex, valuation and credit panels.
- data/nz_transmission.csv: New Zealand exposure indicators.
- data/stress_anchors.csv: selected stress-test and historical anchor values.
- data/housing_user_cost.csv: the annual ownership cost and hurdle calculation.
- data/scenario_assumptions.csv and data/scenario_outcomes.csv: the stress matrix.
- data/transmission_channels.csv: the labelled transmission map.
- data/decision_tests.csv: the decision checklist.
- data/analysis_statistics.csv: every headline statistic printed by the replication
  script and quoted in the report.
- data/migration.csv and data/ownership_cohorts.csv: the demographic context series.
- data/affordability_yield.csv includes the raw rent and value inputs.

10. Known limitations and gaps

1. Continuous free REINZ Auckland history is paywalled. The report does not use it; the
continuous series is QV and is labelled non-official. No free series covers Auckland
prices before January 2007, so the longest price window is 19 years, not 20.
2. The QV average equalised value is not a median sale price and is not the REINZ HPI.
3. The HILS 2025 household income is provisional with a Statistics NZ corrections notice
dated 29 September 2026; corrections are due in February 2027.
4. Official household debt-to-disposable-income data stop at 2021Q2.
5. RBNZ and IMF websites returned HTTP 403; their data were retrieved through Internet
Archive captures of the exact official URLs. Capture dates are recorded per source.
6. The AI stream could not verify New Zealand bank offshore funding shares or wholesale
spreads; the credit stream's archived RBNZ data are used instead. Terms of trade and a
forward P/E are not used.
7. Census 2023 had an 87.6 percent official response rate, the lowest since 2006, and
Auckland accounted for about 42 percent of the national net undercount. Auckland age-band
tenure is unavailable, and age-band series are cross-sectional.
8. First-home-buyer shares are non-official industry estimates.
9. No representative survey of preference for owning versus renting was verified;
attitude evidence is limited to issue salience and housing-suitability preference.
10. Scenario values are assumptions, not measurements, and carry no probability.

11. Source verification and reproduction

evidence/sources.csv is merged from the five stream ledgers by
scripts/merge_streams.py. scripts/verify_primary_sources.py checks every source against
its archived snapshot (title, organisation, date and file integrity), records the
snapshot SHA-256 and writes evidence/reference-check.json. A source is included in the
final ledger only if it passes both content and metadata checks; excluded sources and
the reasons are recorded in the stream notes and in the merge script.
Run the pipeline from the project directory with:
python3 scripts/merge_streams.py
python3 scripts/verify_primary_sources.py
python3 scripts/build_analysis_data.py
python3 scripts/replicate.py
The replication script reads the data CSVs, checks the required columns, prints the statistics
quoted in the report and summary, and regenerates every chart as a PNG. It does not embed chart
data arrays.

12. Attribution and terms

Dr Yuqian Zhang, October 2026. Source documents remain subject to their publishers'
terms; the project republishes derived values, locators and permitted snapshots only.
