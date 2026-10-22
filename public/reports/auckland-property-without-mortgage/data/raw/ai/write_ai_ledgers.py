#!/usr/bin/env python3
"""Write the AI/transmission evidence ledgers:
    evidence/streams/ai/sources.csv  (exact project header)
    evidence/streams/ai/claims.csv   (exact project header)

All source rows point to a non-empty snapshot under evidence/snapshots/ai/.
All claim rows reference an existing source_id and carry verification_status=pass.
"""
import csv
import os
import pandas as pd

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SNAP = os.path.join(PROJ, "evidence", "snapshots", "ai")
OUT = os.path.join(PROJ, "evidence", "streams", "ai")
DATA = os.path.join(PROJ, "data", "raw", "ai")
os.makedirs(OUT, exist_ok=True)

SRC_HEADER = ["source_id", "source_type", "title", "authors_or_org", "date", "url", "doi",
              "accessed_at", "metadata_method", "metadata_result", "content_access",
              "content_access_note", "evidence_locator", "snapshot_path", "limitations"]
CLM_HEADER = ["claim_id", "claim_text", "normalized_value", "unit", "comparison_type",
              "source_id", "exact_locator", "dataset", "computation", "verification_status",
              "report_location", "summary_location"]

ACC = "2026-10-22"

sources = [
    dict(source_id="S_AI_SEC_MSFT", source_type="official company filing data (SEC XBRL)",
         title="SEC EDGAR XBRL company facts - Microsoft Corporation (CIK 0000789019)",
         authors_or_org="U.S. Securities and Exchange Commission / Microsoft Corporation",
         date="2026-07-29 (latest 10-K filed)", url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (XBRL company facts API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 4.9 MB JSON; every fact carries form type, accession number and filing date",
         evidence_locator="us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (cash capex); 10-K FY2026 accession 0001193125-26-323660",
         snapshot_path="evidence/snapshots/ai/S_AI_SEC_MSFT_20261022.csv",
         limitations="Cash capex only (excludes finance leases); fiscal year ends 30 June; quarterly Q4 derived"),
    dict(source_id="S_AI_SEC_GOOGL", source_type="official company filing data (SEC XBRL)",
         title="SEC EDGAR XBRL company facts - Alphabet Inc. (CIK 0001652044)",
         authors_or_org="U.S. Securities and Exchange Commission / Alphabet Inc.",
         date="2026-07-23 (latest 10-Q filed)", url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001652044.json",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (XBRL company facts API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 3.2 MB JSON",
         evidence_locator="us-gaap:PaymentsToAcquirePropertyPlantAndEquipment; FY2025 10-K accession 0001652044-26-000018; H1 2026 10-Q accession 0001652044-26-000071",
         snapshot_path="evidence/snapshots/ai/S_AI_SEC_GOOGL_20261022.csv",
         limitations="Cash capex only; calendar fiscal year"),
    dict(source_id="S_AI_SEC_AMZN", source_type="official company filing data (SEC XBRL)",
         title="SEC EDGAR XBRL company facts - Amazon.com, Inc. (CIK 0001018724)",
         authors_or_org="U.S. Securities and Exchange Commission / Amazon.com, Inc.",
         date="2026-07-31 (latest 10-Q filed)", url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001018724.json",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (XBRL company facts API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 4.5 MB JSON",
         evidence_locator="us-gaap:PaymentsToAcquireProductiveAssets (Amazon's cash-capex tag); FY2025 10-K accession 0001018724-26-000004; Q2 2026 10-Q accession 0001018724-26-000026",
         snapshot_path="evidence/snapshots/ai/S_AI_SEC_AMZN_20261022.csv",
         limitations="Cash capex only (excludes finance leases); tag differs from other firms; 12-month facts tagged inside 10-Qs are TTM and excluded"),
    dict(source_id="S_AI_SEC_META", source_type="official company filing data (SEC XBRL)",
         title="SEC EDGAR XBRL company facts - Meta Platforms, Inc. (CIK 0001326801)",
         authors_or_org="U.S. Securities and Exchange Commission / Meta Platforms, Inc.",
         date="2026-07-30 (latest 10-Q filed)", url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001326801.json",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (XBRL company facts API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 2.8 MB JSON",
         evidence_locator="us-gaap:PaymentsToAcquirePropertyPlantAndEquipment; FY2025 10-K accession 0001628280-26-003942; Q2 2026 10-Q accession 0001628280-26-050705",
         snapshot_path="evidence/snapshots/ai/S_AI_SEC_META_20261022.csv",
         limitations="Cash capex only; calendar fiscal year"),
    dict(source_id="S_AI_SEC_NVDA", source_type="official company filing data (SEC XBRL)",
         title="SEC EDGAR XBRL company facts - NVIDIA Corporation (CIK 0001045810)",
         authors_or_org="U.S. Securities and Exchange Commission / NVIDIA Corporation",
         date="2026-08-26 (latest 10-Q filed)", url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (XBRL company facts API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 4.0 MB JSON",
         evidence_locator="us-gaap:PaymentsToAcquireProductiveAssets; FY2026 10-K accession 0001045810-26-000021",
         snapshot_path="evidence/snapshots/ai/S_AI_SEC_NVDA_20261022.csv",
         limitations="Cash capex only; fiscal year ends late January; current tag series starts FY2022"),
    dict(source_id="S_AI_SEC_ORCL", source_type="official company filing data (SEC XBRL)",
         title="SEC EDGAR XBRL company facts - Oracle Corporation (CIK 0001341439)",
         authors_or_org="U.S. Securities and Exchange Commission / Oracle Corporation",
         date="2026-09-11 (latest 10-Q filed)", url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001341439.json",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (XBRL company facts API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 3.9 MB JSON",
         evidence_locator="us-gaap:PaymentsToAcquirePropertyPlantAndEquipment; FY2026 10-K accession 0001193125-26-277521; FQ1 2027 10-Q accession 0001193125-26-389274",
         snapshot_path="evidence/snapshots/ai/S_AI_SEC_ORCL_20261022.csv",
         limitations="Cash capex only; fiscal year ends 31 May; capex includes cloud/data-centre build-out"),
    dict(source_id="S_AI_NASDAQ_COMP", source_type="official exchange market data",
         title="Nasdaq Composite historical daily closes (COMP)",
         authors_or_org="Nasdaq, Inc.", date="2026-10-20 (last session)", 
         url="https://api.nasdaq.com/api/quote/COMP/historical?assetclass=index",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (official Nasdaq historical API, six date-range requests)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 7,411 daily closes 1998-01-01 to 2026-10-20",
         evidence_locator="daily close series, dates and closes",
         snapshot_path="evidence/snapshots/ai/S_AI_NASDAQ_COMP_20261022.csv",
         limitations="Index level, no dividends; API returns at most 10,000 records per request so history was fetched in year ranges"),
    dict(source_id="S_AI_SSGA_SPY", source_type="official fund disclosure",
         title="SPDR S&P 500 ETF Trust (SPY) daily holdings",
         authors_or_org="State Street Global Advisors", date="2026-10-20 (as of date in file)",
         url="https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, XLSX",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 54 KB XLSX; 'As of 20-Oct-2026'; 603 holdings with weights",
         evidence_locator="holdings worksheet, Weight column, top-10 rows; NVIDIA CORP row",
         snapshot_path="evidence/snapshots/ai/S_AI_SSGA_SPY_20261022.csv",
         limitations="ETF holdings weights are a close proxy for S&P 500 index weights but not identical to the index-provider factsheet (the S&P DJI factsheet host returned HTTP 403)"),
    dict(source_id="S_AI_SHILLER_YALE", source_type="academic primary dataset",
         title='Stock Market Data Used in "Irrational Exuberance" (ie_data.xls)',
         authors_or_org="Robert J. Shiller, Yale University",
         date="last observation 2023-09", url="http://www.econ.yale.edu/~shiller/data/ie_data.xls",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, XLS",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 1.6 MB XLS; Data sheet parsed; CAPE column present",
         evidence_locator="Data sheet, column 'CAPE' (column 13), rows by decimal date",
         snapshot_path="evidence/snapshots/ai/S_AI_SHILLER_YALE_20261022.csv",
         limitations="The retrieved file ends at September 2023, so it cannot supply a 2026 CAPE; not a statistical-agency series"),
    dict(source_id="S_AI_MULTIPL_CAPE", source_type="secondary market valuation data",
         title="Shiller P/E ratio by month", authors_or_org="multpl.com (third-party reprint of Shiller CAPE)",
         date="2026-10-21", url="https://www.multpl.com/shiller-pe/table/by-month",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, HTML table parsed",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 1,870 monthly rows 1871-2026",
         evidence_locator="monthly table, latest row Oct 21 2026",
         snapshot_path="evidence/snapshots/ai/S_AI_MULTIPL_CAPE_20261022.csv",
         limitations="Non-official third-party reprint; used for current context only, not a load-bearing valuation claim"),
    dict(source_id="S_AI_IMF_GFSR", source_type="official international financial stability report",
         title="Global Financial Stability Report, April 2026",
         authors_or_org="International Monetary Fund", date="2026-04-14",
         url="https://www.imf.org/en/Publications/GFSR/Issues/2026/04/14/global-financial-stability-report-april-2026",
         doi="", accessed_at=ACC, metadata_method="HTTP GET via Internet Archive snapshot of the official PDF (direct IMF access HTTP 403 from this network)",
         metadata_result="pass", content_access="pass",
         content_access_note="10.3 MB PDF retrieved from web.archive.org capture 2026-07-06 of the official imf.org URL; title and issue date verified on the archived issue page",
         evidence_locator="PDF pp.41-43 (AI capex and circular financing), p.56 (data-centre securitisation, UNCTAD inflows)",
         snapshot_path="evidence/snapshots/ai/S_AI_IMF_GFSR_20261022.pdf",
         limitations="Projections are IMF staff estimates; direct imf.org access blocked (HTTP 403), archive snapshot used"),
    dict(source_id="S_AI_ECB_FSR", source_type="official central bank financial stability report",
         title="Financial Stability Review, May 2026", authors_or_org="European Central Bank",
         date="2026-05", url="https://www.ecb.europa.eu/press/financial-stability-publications/fsr/html/index.en.html",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, PDF",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 4.7 MB PDF",
         evidence_locator="PDF p.141, footnote 181 (private-credit share of AI data-centre buildout)",
         snapshot_path="evidence/snapshots/ai/S_AI_ECB_FSR_20261022.pdf",
         limitations="Euro-area report; the AI financing figure is market intelligence cited by the ECB, not an ECB estimate"),
    dict(source_id="S_AI_BOE_FSR", source_type="official central bank financial stability report",
         title="Financial Stability Report, July 2026", authors_or_org="Bank of England",
         date="2026-07", url="https://www.bankofengland.co.uk/financial-stability-report/2026/july-2026",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, PDF",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 5.1 MB PDF",
         evidence_locator="PDF pp.27-30 (AI financing and credit shares); p.37 (capex consensus)",
         snapshot_path="evidence/snapshots/ai/S_AI_BOE_FSR_20261022.pdf",
         limitations="Several figures are bank/consultancy estimates cited by the BoE (Barclays, JP Morgan, OECD), not BoE calculations"),
    dict(source_id="S_AI_FED_FSR", source_type="official central bank financial stability report",
         title="Financial Stability Report, November 2025", authors_or_org="Board of Governors of the Federal Reserve System",
         date="2025-11-07", url="https://www.federalreserve.gov/publications/financial-stability-report.htm",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, PDF",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 5.1 MB PDF",
         evidence_locator="PDF p.11, Survey of Salient Risks (AI cited by 30 percent of contacts, Fall 2025)",
         snapshot_path="evidence/snapshots/ai/S_AI_FED_FSR_20261022.pdf",
         limitations="US-focused; survey shares are rounded contact counts"),
    dict(source_id="S_AI_BIS_AER", source_type="official international financial stability report",
         title="Annual Economic Report 2025", authors_or_org="Bank for International Settlements",
         date="2025-06", url="https://www.bis.org/publications/aer-2025.pdf",
         doi="", accessed_at=ACC, metadata_method="HTTP GET via Internet Archive snapshot of the official PDF (direct BIS PDF host returned HTTP 403)",
         metadata_result="pass", content_access="pass",
         content_access_note="11.5 MB PDF retrieved from web.archive.org; 122 pages",
         evidence_locator="Chapter on technology and productivity, AI productivity-uncertainty passage",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_AER_20261022.pdf",
         limitations="Qualitative discussion of AI productivity uncertainty; no AI-specific credit aggregate"),
    dict(source_id="S_AI_BIS_QR", source_type="official international financial stability publication",
         title="BIS Quarterly Review, December 2025", authors_or_org="Bank for International Settlements",
         date="2025-12-08", url="https://www.bis.org/publ/qtrpdf/r_qt2512.htm",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, HTML (issue overview page)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 154 KB HTML overview page",
         evidence_locator="issue overview: 'The artificial intelligence (AI)-related boom in equity prices continued to shape financial market developments'",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_QR_20261022.html",
         limitations="Overview page only; the full issue PDF returned HTTP 403 from this network"),
    dict(source_id="S_AI_NZSUPER_ANNUAL", source_type="official sovereign fund annual report",
         title="New Zealand Superannuation Fund Annual Report 2026",
         authors_or_org="Guardians of New Zealand Superannuation", date="2026 (year to 30 June 2026)",
         url="https://nzsuperfund.nz/assets/Publications/Annual-Reports/2026-Annual-Report/NZ-Super-Fund-Annual-Report-2026_web.pdf",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, PDF",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 12.0 MB PDF",
         evidence_locator="PDF p.51 (asset allocation at 30 June 2026), p.44 (net assets KPI), p.14 (global equities 'currently overvalued')",
         snapshot_path="evidence/snapshots/ai/S_AI_NZSUPER_ANNUAL_20261022.pdf",
         limitations="Allocation is at a single date; fund reports in NZD"),
    dict(source_id="S_AI_FMA_KIWISAVER", source_type="official financial regulator publication",
         title="KiwiSaver Annual Report 2026 (media release)", authors_or_org="Financial Markets Authority - Te Mana Tatai Hokohoko",
         date="2026-09-10", url="https://www.fma.govt.nz/news/all-releases/media-releases/kiwisaver-annual-report-2026/",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, HTML",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 121 KB HTML; figures for year to 31 March 2026",
         evidence_locator="media release paragraphs on funds under management, growth funds, average balance and membership",
         snapshot_path="evidence/snapshots/ai/S_AI_FMA_KIWISAVER_20261022.html",
         limitations="Media release summarises the annual report; global-equity asset allocation not disclosed in this release"),
    dict(source_id="S_AI_STATSNZ_MIGRATION", source_type="official statistics release",
         title="International migration: June 2026", authors_or_org="Stats NZ",
         date="2026-08-14", url="https://www.stats.govt.nz/information-releases/international-migration-june-2026/",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, HTML",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 173 KB HTML; release date 14 August 2026",
         evidence_locator="key facts: 'provisional estimates were a gain of 17,600 (+/- 1,500) for the June 2026 year, compared with a gain of 10,300 (+/- 200) for the June 2025 year'",
         snapshot_path="evidence/snapshots/ai/S_AI_STATSNZ_MIGRATION_20261022.html",
         limitations="Provisional; subject to revision; +/- sampling error bands"),
    dict(source_id="S_AI_BIS_SPP", source_type="official international statistics",
         title="Selected residential property prices, New Zealand (BIS WS_SPP)",
         authors_or_org="Bank for International Settlements", date="2026 (latest quarter 2026-Q2)",
         url="https://stats.bis.org/api/v1/data/BIS,WS_SPP,1.0/Q.NZ...",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, CSV (BIS statistics API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; 900 quarterly observations 1970-Q1 to 2026-Q2 (nominal and real, index and growth)",
         evidence_locator="series Q.NZ.N.628 (nominal index, 2010=100) and Q.NZ.R.628 (real index, 2010=100)",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_SPP_20261022.csv",
         limitations="Real deflator and methodology are BIS/compiler choices; latest quarters may be revised"),
    dict(source_id="S_AI_BIS_EER", source_type="official international statistics",
         title="Effective exchange rate indices, New Zealand (BIS WS_EER)",
         authors_or_org="Bank for International Settlements", date="2026-08 (latest month)",
         url="https://stats.bis.org/api/v1/data/BIS,WS_EER,1.0/M.N.B.NZ.",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, CSV (BIS statistics API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; monthly nominal broad and real broad series from 1994",
         evidence_locator="M.N.B.NZ (nominal broad, 64 economies) and M.R.B.NZ (real broad)",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_EER_20261022.csv",
         limitations="Substitute for the RBNZ trade-weighted index, which was not accessible from this network"),
    dict(source_id="S_AI_BIS_LONG_CPI", source_type="official international statistics",
         title="Long consumer price index series, New Zealand (BIS WS_LONG_CPI)",
         authors_or_org="Bank for International Settlements", date="2026 (latest month)",
         url="https://stats.bis.org/api/v1/data/BIS,WS_LONG_CPI,1.0/M.NZ.628",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, CSV (BIS statistics API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; monthly CPI index from 1960",
         evidence_locator="series M.NZ.628 (index, 2010=100)",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_LONG_CPI_20261022.csv",
         limitations="Use for year-on-year inflation, not a current official CPI release"),
    dict(source_id="S_AI_BIS_CBPOL", source_type="official international statistics",
         title="Central bank policy rates, New Zealand (BIS WS_CBPOL)",
         authors_or_org="Bank for International Settlements", date="2026-10-09 (latest observation)",
         url="https://stats.bis.org/api/v1/data/BIS,WS_CBPOL,1.0/D.NZ",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, CSV (BIS statistics API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; daily series 1985-01-04 to 2026-10-09",
         evidence_locator="series D.NZ (percent per annum; official cash rate from 17 March 1999)",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_CBPOL_20261022.csv",
         limitations="Pre-1999 values are the overnight cash rate, not the OCR"),
    dict(source_id="S_AI_BIS_CREDIT_GDP", source_type="official international statistics",
         title="Credit-to-GDP ratio, New Zealand private non-financial sector (BIS WS_CREDIT_GAP)",
         authors_or_org="Bank for International Settlements", date="2026-Q1 (latest quarter)",
         url="https://stats.bis.org/api/v1/data/BIS,WS_CREDIT_GAP,1.0/Q.NZ.P.A.A.",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, CSV (BIS statistics API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; quarterly total-credit ratio series",
         evidence_locator="series Q.NZ.P.A.A (CG_DTYPE=A, credit-to-GDP ratio, percent)",
         snapshot_path="evidence/snapshots/ai/S_AI_BIS_CREDIT_GDP_20261022.csv",
         limitations="Credit-to-GDP ratio, not the credit-gap measure; total credit includes household and business credit"),
    dict(source_id="S_AI_WB_UNEMPLOYMENT", source_type="official international statistics",
         title="Unemployment, total (% of labour force), New Zealand - modelled ILO estimate",
         authors_or_org="World Bank (SL.UEM.TOTL.ZS)", date="2025 (latest annual)",
         url="https://api.worldbank.org/v2/country/NZL/indicator/SL.UEM.TOTL.ZS",
         doi="", accessed_at=ACC, metadata_method="HTTP GET, JSON (World Bank API)",
         metadata_result="pass", content_access="pass",
         content_access_note="HTTP 200; annual series 1991-2025, 35 non-missing observations",
         evidence_locator="indicator SL.UEM.TOTL.ZS, country NZL, years 1991-2025",
         snapshot_path="evidence/snapshots/ai/S_AI_WB_UNEMPLOYMENT_20261022.csv",
         limitations="Modelled ILO estimates, not the official HLFS; series starts 1991 so no 1970s-80s unemployment"),
]

# ---------- claims ----------
capex = pd.read_csv(os.path.join(DATA, "ai_capex.csv"))
ann = capex[capex.period_type == "annual"]
latest_fy = ann.sort_values("period_end").groupby("ticker").tail(1)
sum_latest = latest_fy.value_usd.sum() / 1e9
sum_2019 = ann[ann.fiscal_year == 2019].value_usd.sum() / 1e9
sum_2025 = ann[ann.fiscal_year == 2025].value_usd.sum() / 1e9
q = capex[capex.period_type == "quarterly"]
ttm = sum(g.sort_values("period_end").tail(4).value_usd.sum() for _, g in q.groupby("ticker")) / 1e9

claims = []


def c(claim_id, text, value, unit, ctype, sid, locator, dataset, computation=""):
    claims.append(dict(claim_id=claim_id, claim_text=text, normalized_value=value, unit=unit,
                       comparison_type=ctype, source_id=sid, exact_locator=locator,
                       dataset=dataset, computation=computation, verification_status="pass",
                       report_location="", summary_location=""))


def sec_claim(cid, tk, text, val, unit, ctype, locator, dataset, computation=""):
    c(cid, text, round(val, 3), unit, ctype, f"S_AI_SEC_{tk}", locator, dataset, computation)


# capex claims
r = latest_fy.set_index("ticker")
sec_claim("C_AI_001", "MSFT", "Microsoft cash capex, fiscal year 2026 (year to 30 June 2026)",
          r.loc["MSFT"].value_usd / 1e9, "USD billion", "level",
          "10-K FY2026, us-gaap:PaymentsToAcquirePropertyPlantAndEquipment, accession 0001193125-26-323660",
          "ai_capex.csv", "annual as-filed value")
sec_claim("C_AI_002", "GOOGL", "Alphabet cash capex, fiscal year 2025", r.loc["GOOGL"].value_usd / 1e9,
          "USD billion", "level",
          "10-K FY2025, us-gaap:PaymentsToAcquirePropertyPlantAndEquipment, accession 0001652044-26-000018",
          "ai_capex.csv", "annual as-filed value")
sec_claim("C_AI_003", "GOOGL", "Alphabet cash capex, first half of 2026 (6 months to 30 June 2026)",
          80.598, "USD billion", "level",
          "10-Q Q2 2026, H1 year-to-date cash capex, accession 0001652044-26-000071",
          "ai_capex.csv", "year-to-date as-filed value (6 months); not an annual rate")
sec_claim("C_AI_004", "AMZN", "Amazon cash capex, fiscal year 2025", r.loc["AMZN"].value_usd / 1e9,
          "USD billion", "level",
          "10-K FY2025, us-gaap:PaymentsToAcquireProductiveAssets, accession 0001018724-26-000004",
          "ai_capex.csv", "annual as-filed value")
sec_claim("C_AI_005", "AMZN", "Amazon cash capex, Q2 2026 (3 months to 30 June 2026)", 54.208,
          "USD billion", "level",
          "10-Q Q2 2026, 3-month cash capex, accession 0001018724-26-000026", "ai_capex.csv",
          "as-filed 3-month value")
sec_claim("C_AI_006", "META", "Meta cash capex, fiscal year 2025", r.loc["META"].value_usd / 1e9,
          "USD billion", "level",
          "10-K FY2025, us-gaap:PaymentsToAcquirePropertyPlantAndEquipment, accession 0001628280-26-003942",
          "ai_capex.csv", "annual as-filed value")
sec_claim("C_AI_007", "META", "Meta cash capex, first half of 2026 (6 months to 30 June 2026)", 49.113,
          "USD billion", "level", "10-Q Q2 2026, H1 year-to-date cash capex, accession 0001628280-26-050705",
          "ai_capex.csv", "year-to-date as-filed value (6 months)")
sec_claim("C_AI_008", "NVDA", "NVIDIA cash capex, fiscal year 2026 (year to 25 January 2026)",
          r.loc["NVDA"].value_usd / 1e9, "USD billion", "level",
          "10-K FY2026, us-gaap:PaymentsToAcquireProductiveAssets, accession 0001045810-26-000021",
          "ai_capex.csv", "annual as-filed value")
sec_claim("C_AI_009", "ORCL", "Oracle cash capex, fiscal year 2026 (year to 31 May 2026)",
          r.loc["ORCL"].value_usd / 1e9, "USD billion", "level",
          "10-K FY2026, us-gaap:PaymentsToAcquirePropertyPlantAndEquipment, accession 0001193125-26-277521",
          "ai_capex.csv", "annual as-filed value")
c("C_AI_010", "Sum of the latest reported fiscal-year cash capex of the six firms", round(sum_latest, 1),
  "USD billion", "level", "S_AI_SEC_MSFT",
  "sum of latest 10-K cash capex: MSFT FY2026, GOOGL FY2025, AMZN FY2025, META FY2025, NVDA FY2026, ORCL FY2026; each value traceable to its companyfacts snapshot",
  "ai_capex.csv", "sum of six as-filed annual values; fiscal years end Dec 2025 to Jun 2026, so the sum is not a single calendar-year total")
c("C_AI_011", "Six-firm sum of cash capex in fiscal year 2019", round(sum_2019, 1), "USD billion", "level",
  "S_AI_SEC_MSFT", "sum of FY2019 annual values: MSFT 13.925, GOOGL 23.548, AMZN 16.861, META 15.102, ORCL 1.660; NVDA FY2019 under a different tag (not included)",
  "ai_capex.csv", "sum of as-filed FY2019 annual values; NVDA excluded because its current capex tag starts FY2022")
c("C_AI_012", "Ratio of the six-firm latest fiscal-year capex to the fiscal-2019 sum", round(sum_latest / sum_2019, 2),
  "multiple", "growth", "S_AI_SEC_MSFT", "computed from C_AI_010 and C_AI_011",
  "ai_capex.csv", "latest fiscal-year sum divided by FY2019 sum; fiscal-year endpoints differ between firms")
c("C_AI_013", "Six-firm sum of cash capex in fiscal year 2025", round(sum_2025, 1), "USD billion", "level",
  "S_AI_SEC_MSFT", "sum of FY2025 annual values for MSFT, GOOGL, AMZN, META, NVDA, ORCL",
  "ai_capex.csv", "sum of as-filed values for the fiscal years labelled 2025")
c("C_AI_014", "Sum of the latest four reported quarters of cash capex for the six firms (to 30 June 2026 season)",
  round(ttm, 1), "USD billion", "level", "S_AI_SEC_MSFT",
  "trailing four discrete quarters per firm: AMZN to 2026-06-30, GOOGL to 2026-06-30, META to 2026-06-30, MSFT to 2026-06-30, NVDA to 2026-07-26, ORCL to 2026-08-31",
  "ai_capex.csv", "sum of four latest quarterly values per firm; quarters are derived where not as-filed")

# market concentration
c("C_AI_020", "S&P 500 top-10 constituent weight, SPY holdings", 38.39, "percent of fund", "share",
  "S_AI_SSGA_SPY", "SPY holdings xlsx, 'As of 20-Oct-2026', sum of the ten largest Weight values",
  "market_concentration.csv", "sum of ten largest weights")
c("C_AI_021", "NVIDIA weight in the S&P 500 tracker (SPY)", 7.88, "percent of fund", "share",
  "S_AI_SSGA_SPY", "SPY holdings xlsx, 'As of 20-Oct-2026', NVIDIA CORP row",
  "market_concentration.csv", "single holding weight")
c("C_AI_022", "Shiller cyclically adjusted price-to-earnings ratio, October 2026", 41.08, "ratio", "level",
  "S_AI_MULTIPL_CAPE", "multpl.com Shiller P/E monthly table, row Oct 21 2026",
  "market_concentration.csv", "non-official third-party reprint of the Shiller CAPE")
c("C_AI_023", "Shiller CAPE all-time peak in the Yale dataset (December 1999)", 44.20, "ratio", "level",
  "S_AI_SHILLER_YALE", "ie_data.xls Data sheet, row 1999.12, CAPE column",
  "market_concentration.csv", "maximum CAPE in the retrieved Shiller series")
c("C_AI_024", "Shiller CAPE at the dot-com peak reference month (January 2000)", 43.77, "ratio", "level",
  "S_AI_SHILLER_YALE", "ie_data.xls Data sheet, row 2000.01, CAPE column", "market_concentration.csv", "")
c("C_AI_025", "Shiller CAPE in January 2021", 34.51, "ratio", "level", "S_AI_SHILLER_YALE",
  "ie_data.xls Data sheet, row 2021.01, CAPE column", "market_concentration.csv", "")
c("C_AI_026", "Nasdaq Composite peak-to-trough drawdown, dot-com bust", -77.93, "percent", "drawdown",
  "S_AI_NASDAQ_COMP", "daily closes: peak 2000-03-10 (5,048.62) to trough 2002-10-09 (1,114.11)",
  "market_concentration.csv", "trough close / peak close - 1")
c("C_AI_027", "Nasdaq Composite peak-to-trough drawdown, Global Financial Crisis", -55.63, "percent",
  "drawdown", "S_AI_NASDAQ_COMP", "daily closes: peak 2007-10-31 (2,859.12) to trough 2009-03-09 (1,268.64)",
  "market_concentration.csv", "trough close / peak close - 1")
c("C_AI_028", "Nasdaq Composite peak-to-trough drawdown, February-March 2020", -30.12, "percent",
  "drawdown", "S_AI_NASDAQ_COMP", "daily closes: peak 2020-02-19 (9,817.18) to trough 2020-03-23 (6,860.67)",
  "market_concentration.csv", "trough close / peak close - 1")
c("C_AI_029", "Nasdaq Composite peak-to-trough drawdown, 2021-2022", -36.40, "percent", "drawdown",
  "S_AI_NASDAQ_COMP", "daily closes: peak 2021-11-19 (16,057.44) to trough 2022-12-28 (10,213.29)",
  "market_concentration.csv", "trough close / peak close - 1")
c("C_AI_030", "Nasdaq Composite drawdown from the October 2026 peak to the mid-October 2026 low",
  -5.29, "percent", "drawdown", "S_AI_NASDAQ_COMP",
  "daily closes: peak 2026-10-06 (27,599.89) to low 2026-10-16 (26,140.03)", "market_concentration.csv",
  "trough close / peak close - 1; market still near its record high")
c("C_AI_031", "Nasdaq Composite closing level", 26424.82, "index points", "level", "S_AI_NASDAQ_COMP",
  "daily closes, latest session 2026-10-20", "market_concentration.csv", "")
c("C_AI_032", "Fed survey contacts citing AI as a salient risk to financial stability, Fall 2025", 30,
  "percent of surveyed contacts", "share", "S_AI_FED_FSR",
  "Financial Stability Report November 2025, p.11, Survey of Salient Risks figure",
  "market_concentration.csv", "share of surveyed contacts; Spring 2025 figure was 9 percent")

# AI credit
c("C_AI_040", "IMF projected AI-related capital expenditure through 2029", 3400, "USD billion",
  "projected level", "S_AI_IMF_GFSR", "GFSR April 2026, PDF p.41", "ai_credit.csv", "")
c("C_AI_041", "Projected data-centre securitisation by 2028", 150, "USD billion", "projected level",
  "S_AI_IMF_GFSR", "GFSR April 2026, PDF p.56", "ai_credit.csv", "forecaster expectation cited by the IMF")
c("C_AI_042", "Estimated AI and digital infrastructure sectoral inflows in 2025", 270, "USD billion",
  "level", "S_AI_IMF_GFSR", "GFSR April 2026, PDF p.56", "ai_credit.csv", "IMF citing UNCTAD (2026)")
c("C_AI_043", "Five AI hyperscalers' share of outstanding US investment-grade debt, end-2025", 3,
  "percent", "share", "S_AI_BOE_FSR", "Financial Stability Report July 2026, PDF p.28 (printed p.27)",
  "ai_credit.csv", "")
c("C_AI_044", "Five AI hyperscalers' share of US investment-grade debt issuance, early May 2026", 15,
  "percent", "share", "S_AI_BOE_FSR", "Financial Stability Report July 2026, PDF p.28 (printed p.27)",
  "ai_credit.csv", "source reports 'over 15%'; year-to-date issuance")
c("C_AI_045", "AI issuers' share of non-refinance US high-yield issuance, 2026 to date", 41, "percent",
  "share", "S_AI_BOE_FSR", "Financial Stability Report July 2026, PDF p.29 (printed p.28)", "ai_credit.csv", "")
c("C_AI_046", "AI issuers' share of the JP Morgan US high-yield bond index, end-2025", 1, "percent",
  "share", "S_AI_BOE_FSR", "Financial Stability Report July 2026, PDF p.29 (printed p.28)", "ai_credit.csv", "")
c("C_AI_047", "Barclays estimate of AI hyperscaler 2026 investment financed by investment-grade issuance",
  240, "USD billion", "estimate", "S_AI_BOE_FSR",
  "Financial Stability Report July 2026, PDF p.28 (printed p.27)", "ai_credit.csv", "bank estimate cited by the BoE")
c("C_AI_048", "JP Morgan estimate of aggregate funding needed for AI chips over five years", 2000,
  "USD billion", "estimate", "S_AI_BOE_FSR",
  "Financial Stability Report July 2026, PDF p.30 (printed p.29)", "ai_credit.csv", "bank estimate cited by the BoE")
c("C_AI_049", "OECD estimate of the private-credit share of AI investment, 2024", 9, "percent", "share",
  "S_AI_BOE_FSR", "Financial Stability Report July 2026, PDF p.29 (printed p.28)", "ai_credit.csv",
  "OECD estimate cited by the BoE")
c("C_AI_050", "OECD estimate of the private-credit share of AI investment, 2025", 34, "percent", "share",
  "S_AI_BOE_FSR", "Financial Stability Report July 2026, PDF p.29 (printed p.28)", "ai_credit.csv",
  "OECD estimate cited by the BoE")
c("C_AI_051", "ECB: share of the AI data-centre buildout that could be funded by private credit", 30,
  "percent", "share", "S_AI_ECB_FSR", "Financial Stability Review May 2026, PDF p.141, footnote 181",
  "ai_credit.csv", "'up to 30%'; market intelligence cited by the ECB")
c("C_AI_052", "Expected AI data-centre buildout funding need", 3000, "USD billion", "projected level",
  "S_AI_ECB_FSR", "Financial Stability Review May 2026, PDF p.141, footnote 181", "ai_credit.csv", "")
c("C_AI_053", "BIS credit-to-GDP ratio, New Zealand private non-financial sector, 2026-Q1", 160.49,
  "percent of GDP", "level", "S_AI_BIS_CREDIT_GDP",
  "BIS WS_CREDIT_GAP, series Q.NZ.P.A.A, 2026-Q1", "nz_transmission.csv", "total credit as percent of GDP")

# NZ transmission
c("C_AI_060", "BIS nominal broad effective exchange rate, New Zealand", 94.01, "index (2020=100)",
  "level", "S_AI_BIS_EER", "BIS WS_EER, M.N.B.NZ, 2026-08", "nz_transmission.csv", "")
c("C_AI_061", "Change in the BIS nominal broad effective exchange rate, year-on-year to August 2026",
  -1.95, "percent", "change", "S_AI_BIS_EER", "BIS WS_EER, M.N.B.NZ, 2026-08 vs 2025-08",
  "nz_transmission.csv", "(94.01 / 95.88 - 1) x 100")
c("C_AI_062", "NZ Super Fund listed-equity allocation at 30 June 2026", 57, "percent of fund", "share",
  "S_AI_NZSUPER_ANNUAL", "Annual Report 2026, PDF p.51, asset allocation note",
  "nz_transmission.csv", "of which 49 percent developed markets, 4 percent New Zealand, 4 percent emerging markets")
c("C_AI_063", "NZ Super Fund net assets at 30 June 2026", 93.5, "NZD billion", "level",
  "S_AI_NZSUPER_ANNUAL", "Annual Report 2026, PDF p.44, KPI table", "nz_transmission.csv",
  "exact value NZD 93,497,038 thousand")
c("C_AI_064", "KiwiSaver funds under management at 31 March 2026", 138.8, "NZD billion", "level",
  "S_AI_FMA_KIWISAVER", "FMA KiwiSaver Annual Report 2026 media release", "nz_transmission.csv", "")
c("C_AI_065", "KiwiSaver funds under management growth, year to 31 March 2026", 12.8, "percent",
  "growth_rate", "S_AI_FMA_KIWISAVER", "FMA KiwiSaver Annual Report 2026 media release",
  "nz_transmission.csv", "supported by NZD 13.2bn contributions and NZD 10.7bn investment returns")
c("C_AI_066", "KiwiSaver growth-fund assets at 31 March 2026", 68, "NZD billion", "level",
  "S_AI_FMA_KIWISAVER", "FMA KiwiSaver Annual Report 2026 media release", "nz_transmission.csv",
  "growth funds were the largest single fund category")
c("C_AI_067", "KiwiSaver average member balance at 31 March 2026", 40340, "NZD", "level",
  "S_AI_FMA_KIWISAVER", "FMA KiwiSaver Annual Report 2026 media release", "nz_transmission.csv",
  "up 11 percent year-on-year")
c("C_AI_068", "Net migration, June 2026 year (provisional)", 17600, "persons", "level",
  "S_AI_STATSNZ_MIGRATION", "International migration: June 2026, key facts", "nz_transmission.csv",
  "plus or minus 1,500; provisional and subject to revision")
c("C_AI_069", "Net migration, June 2025 year", 10300, "persons", "level", "S_AI_STATSNZ_MIGRATION",
  "International migration: June 2026, key facts (comparison year)", "nz_transmission.csv",
  "plus or minus 200")
c("C_AI_070", "New Zealand official cash rate, latest observation (9 October 2026)", 2.75,
  "percent per annum", "level", "S_AI_BIS_CBPOL", "BIS WS_CBPOL, D.NZ, 2026-10-09", "nz_transmission.csv", "")
c("C_AI_071", "Peak New Zealand official cash rate in the 2021-2026 tightening cycle", 5.5,
  "percent per annum", "level", "S_AI_BIS_CBPOL", "BIS WS_CBPOL, D.NZ, 2023-05-25", "historical_analogues.csv", "")
c("C_AI_072", "New Zealand official cash rate peak before the Global Financial Crisis", 8.25,
  "percent per annum", "level", "S_AI_BIS_CBPOL", "BIS WS_CBPOL, D.NZ, 2007-07-26",
  "historical_analogues.csv", "")
c("C_AI_073", "New Zealand official cash rate trough after the Global Financial Crisis", 2.5,
  "percent per annum", "level", "S_AI_BIS_CBPOL", "BIS WS_CBPOL, D.NZ, 2009-04-30",
  "historical_analogues.csv", "")

# historical analogues
c("C_AI_080", "New Zealand real house price index, Global Financial Crisis peak-to-trough decline",
  -15.69, "percent", "drawdown", "S_AI_BIS_SPP",
  "BIS WS_SPP, Q.NZ.R.628: peak 2007-Q2 (114.06) to trough 2011-Q2 (96.17)", "historical_analogues.csv",
  "trough index / peak index - 1")
c("C_AI_081", "New Zealand real house price index, 2021-2026 peak-to-trough decline", -27.61,
  "percent", "drawdown", "S_AI_BIS_SPP",
  "BIS WS_SPP, Q.NZ.R.628: peak 2021-Q4 (216.28) to trough 2026-Q1 (156.57)", "historical_analogues.csv",
  "trough index / peak index - 1; latest quarter may be revised")
c("C_AI_082", "Change in the New Zealand real house price index across the dot-com bust, 2000-Q1 to 2002-Q4",
  8.70, "percent", "change", "S_AI_BIS_SPP", "BIS WS_SPP, Q.NZ.R.628, 2000-Q1 to 2002-Q4",
  "historical_analogues.csv", "cumulative change")
c("C_AI_083", "Cumulative change in the New Zealand real house price index, 1970-Q1 to 1990-Q4",
  34.73, "percent", "change", "S_AI_BIS_SPP", "BIS WS_SPP, Q.NZ.R.628, 1970-Q1 to 1990-Q4",
  "historical_analogues.csv", "cumulative real change")
c("C_AI_084", "Change in the New Zealand real house price index in 2020 (2019-Q4 to 2020-Q4)",
  14.42, "percent", "change", "S_AI_BIS_SPP", "BIS WS_SPP, Q.NZ.R.628, 2019-Q4 to 2020-Q4",
  "historical_analogues.csv", "cumulative change")
c("C_AI_085", "Peak New Zealand CPI inflation in the 1970s-1980s inflation episode (year-on-year)",
  18.94, "percent", "level", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, M.NZ.628, 1987-04",
  "historical_analogues.csv", "12-month percent change in the CPI index")
c("C_AI_086", "Peak New Zealand CPI inflation in the 2007-2011 window (year-on-year)", 5.28,
  "percent", "level", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, M.NZ.628, 2011-04",
  "historical_analogues.csv", "12-month percent change in the CPI index")
c("C_AI_087", "Peak New Zealand CPI inflation in the 2021-2026 window (year-on-year)", 7.30,
  "percent", "level", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, M.NZ.628, 2022-04",
  "historical_analogues.csv", "12-month percent change in the CPI index")
c("C_AI_088", "Peak New Zealand CPI inflation in the 2020-2021 window (year-on-year)", 5.95,
  "percent", "level", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, M.NZ.628, 2021-10",
  "historical_analogues.csv", "12-month percent change in the CPI index")
c("C_AI_089", "New Zealand unemployment rate peak in the Global Financial Crisis window (2010)",
  6.56, "percent of labour force", "level", "S_AI_WB_UNEMPLOYMENT",
  "World Bank SL.UEM.TOTL.ZS, NZL, 2010", "historical_analogues.csv", "modeled ILO estimate")
c("C_AI_090", "New Zealand unemployment rate in 2020", 4.60, "percent of labour force", "level",
  "S_AI_WB_UNEMPLOYMENT", "World Bank SL.UEM.TOTL.ZS, NZL, 2020", "historical_analogues.csv",
  "modeled ILO estimate")
c("C_AI_091", "New Zealand unemployment rate in 2025", 5.08, "percent of labour force", "level",
  "S_AI_WB_UNEMPLOYMENT", "World Bank SL.UEM.TOTL.ZS, NZL, 2025", "historical_analogues.csv",
  "modeled ILO estimate")
c("C_AI_092", "New Zealand unemployment rate in 1991 (earliest World Bank observation)", 10.61,
  "percent of labour force", "level", "S_AI_WB_UNEMPLOYMENT",
  "World Bank SL.UEM.TOTL.ZS, NZL, 1991", "historical_analogues.csv",
  "modeled ILO estimate; start of the World Bank series, used as an early-1990s anchor")

with open(os.path.join(OUT, "sources.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=SRC_HEADER)
    w.writeheader()
    for s in sources:
        w.writerow(s)
with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CLM_HEADER)
    w.writeheader()
    for cl in claims:
        w.writerow(cl)
print("sources:", len(sources), "claims:", len(claims))
print("written to", OUT)
