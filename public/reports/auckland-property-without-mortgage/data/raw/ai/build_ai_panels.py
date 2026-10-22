#!/usr/bin/env python3
"""Fetch and archive the external sources for the AI/transmission evidence stream,
then build the tidy data panels:
    market_concentration.csv, ai_credit.csv, nz_transmission.csv, historical_analogues.csv

Sources used (all official unless flagged):
  - SEC EDGAR XBRL company facts  -> ai_capex.csv (built by build_ai_capex.py)
  - BIS statistics API (WS_SPP, WS_EER, WS_LONG_CPI, WS_CBPOL, WS_CREDIT_GAP)
  - World Bank API (SL.UEM.TOTL.ZS, New Zealand)
  - Nasdaq official historical index API (COMP)
  - State Street SPDR S&P 500 ETF (SPY) official daily holdings (S&P 500 constituents)
  - Robert Shiller (Yale) ie_data.xls, and multpl.com Shiller P/E monthly table (secondary)
  - IMF Global Financial Stability Report April 2026 (via Internet Archive snapshot)
  - ECB Financial Stability Review May 2026
  - Bank of England Financial Stability Report July 2026
  - Federal Reserve Financial Stability Report November 2025
  - BIS Annual Economic Report 2025 (via Internet Archive snapshot)
  - NZ Super Fund Annual Report 2026
  - FMA KiwiSaver Annual Report 2026 media release
  - Stats NZ International migration: June 2026

Values taken from PDF/HTML publications are transcribed with the printed page or
section recorded as the locator; they are not machine-parsed from the PDF body.
"""
import argparse
import csv
import io
import json
import os
import re
import urllib.request
from datetime import date

UA = "Mozilla/5.0"
BIS = "https://stats.bis.org/api/v1/data/BIS,{flow},1.0/{key}?format=csv&startPeriod={start}"

STAGING = "/tmp"  # downloaded artefacts from the fetch session


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_csv(url, start=None):
    raw = get(url)
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))


def save(path, raw):
    with open(path, "wb") as f:
        f.write(raw)


def copy_staged(staged_path, dest, download_url=None, note=""):
    """Copy a staged download into the snapshot directory; if absent, download."""
    if os.path.exists(staged_path) and os.path.getsize(staged_path) > 1000:
        with open(staged_path, "rb") as f:
            save(dest, f.read())
        return "staged"
    if download_url:
        save(dest, get(download_url))
        return "downloaded"
    raise FileNotFoundError(staged_path)


def parse_bis(path, filt=None):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    out = []
    for r in rows:
        if filt and not filt(r):
            continue
        try:
            v = float(r["OBS_VALUE"])
        except (KeyError, ValueError):
            continue
        if v != v:  # NaN observation
            continue
        out.append((r["TIME_PERIOD"], v, r))
    return out


def quarter_label(period):
    return period


def period_ym(p):
    """Map a BIS period label to a comparable (year, month) tuple."""
    if "-Q" in p:
        y, q = p.split("-Q")
        return int(y), int(q) * 3
    return int(p[:4]), int(p[5:7])


def peak_trough(series, start, end):
    a, b = (int(start[:4]), int(start[5:7])), (int(end[:4]), int(end[5:7]))
    s = [(item[0], item[1]) for item in series if a <= period_ym(item[0]) <= b]
    if not s:
        return None
    pk = max(s, key=lambda x: x[1])
    after = [x for x in s if x[0] >= pk[0]]
    tr = min(after, key=lambda x: x[1])
    return pk, tr, (tr[1] / pk[1] - 1) * 100


def build(snapshot_dir, out_dir, staging):
    os.makedirs(snapshot_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # ---------------- snapshots: data series ----------------
    # 1. BIS residential property prices, NZ, quarterly, nominal and real, 1970+
    spp_url = BIS.format(flow="WS_SPP", key="Q.NZ...", start="1970")
    spp_raw = get(spp_url)
    save(os.path.join(snapshot_dir, "S_AI_BIS_SPP_20261022.csv"), spp_raw)
    # 2. BIS effective exchange rates, NZ, monthly (nominal broad and real broad)
    eer_parts = []
    for key, label in [("M.N.B.NZ.", "nominal_broad"), ("M.R.B.NZ.", "real_broad")]:
        raw = get(BIS.format(flow="WS_EER", key=key, start="1994"))
        eer_parts.append((label, list(csv.DictReader(io.StringIO(raw.decode())))))
    with open(os.path.join(snapshot_dir, "S_AI_BIS_EER_20261022.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["eer_type", "frequency", "eer_basket", "ref_area", "unit_measure",
                    "time_period", "obs_value", "title"])
        for label, rows in eer_parts:
            for r in rows:
                w.writerow([label, r["FREQ"], r["EER_BASKET"], r["REF_AREA"],
                            r["UNIT_MEASURE"], r["TIME_PERIOD"], r["OBS_VALUE"], r["TITLE_TS"]])
    # 3. BIS long CPI, NZ, monthly
    cpi_raw = get(BIS.format(flow="WS_LONG_CPI", key="M.NZ.628", start="1960"))
    save(os.path.join(snapshot_dir, "S_AI_BIS_LONG_CPI_20261022.csv"), cpi_raw)
    # 4. BIS central bank policy rate, NZ, daily
    cbpol_raw = get(BIS.format(flow="WS_CBPOL", key="D.NZ", start="1985"))
    save(os.path.join(snapshot_dir, "S_AI_BIS_CBPOL_20261022.csv"), cbpol_raw)
    # 5. BIS credit-to-GDP ratio for NZ private non-financial sector (total credit)
    cg_raw = get(BIS.format(flow="WS_CREDIT_GAP", key="Q.NZ.P.A.A.", start="1990"))
    save(os.path.join(snapshot_dir, "S_AI_BIS_CREDIT_GDP_20261022.csv"), cg_raw)
    # 6. World Bank unemployment, NZ, annual
    wb_raw = get("https://api.worldbank.org/v2/country/NZL/indicator/SL.UEM.TOTL.ZS?format=json&per_page=200")
    save(os.path.join(snapshot_dir, "S_AI_WB_UNEMPLOYMENT_20261022.csv"), wb_raw)
    wb = json.loads(wb_raw)
    wb_rows = [(int(r["date"]), float(r["value"])) for r in wb[1] if r["value"] is not None]
    wb_rows.sort()

    # 7. Nasdaq Composite daily history (official Nasdaq API, chunked by date range)
    nasdaq_rows = {}
    for y1, y2 in [(1998, 2003), (2004, 2009), (2010, 2015), (2016, 2019), (2020, 2023), (2024, 2026)]:
        u = (f"https://api.nasdaq.com/api/quote/COMP/historical?assetclass=index"
             f"&fromdate={y1}-01-01&todate={y2}-12-31&limit=10000")
        d = json.loads(get(u))
        for r in d["data"]["tradesTable"]["rows"]:
            mm, dd, yy = r["date"].split("/")
            dt = date(int(yy), int(mm), int(dd))
            nasdaq_rows[dt] = float(r["close"].replace(",", ""))
    nd = sorted(nasdaq_rows.items())
    with open(os.path.join(snapshot_dir, "S_AI_NASDAQ_COMP_20261022.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        for dt, v in nd:
            w.writerow([dt.isoformat(), v])

    # 8. SPY official holdings (used for S&P 500 constituent weights)
    spy_raw = get("https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/"
                  "etfs/us/holdings-daily-us-en-spy.xlsx")
    spy_path = os.path.join(snapshot_dir, "S_AI_SSGA_SPY_20261022.xlsx")
    save(spy_path, spy_raw)
    import openpyxl
    wb_ = openpyxl.load_workbook(spy_path, data_only=True)
    ws = wb_.active
    spy_asof = None
    spy_rows = []
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
        if row[0] == "Holdings:" and row[1]:
            spy_asof = row[1]
        if row[0] == "Name" and row[1] == "Ticker":
            continue
        if isinstance(row[4], (int, float)) and row[0]:
            spy_rows.append((row[0], row[1], float(row[4])))
    # save a csv snapshot of the holdings used
    with open(os.path.join(snapshot_dir, "S_AI_SSGA_SPY_20261022.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "ticker", "weight_pct"])
        for r in spy_rows:
            w.writerow(r)
    os.remove(spy_path)
    spy_sorted = sorted(spy_rows, key=lambda x: -x[2])
    top10 = spy_sorted[:10]
    top10_sum = sum(w for _, _, w in top10)
    nvda_w = next(w for _, t, w in spy_sorted if t == "NVDA")

    # 9. Shiller Yale historical data
    sh_raw = get("http://www.econ.yale.edu/~shiller/data/ie_data.xls", timeout=180)
    sh_path = os.path.join(snapshot_dir, "S_AI_SHILLER_YALE_20261022.xls")
    save(sh_path, sh_raw)
    import pandas as pd
    raw = pd.read_excel(pd.ExcelFile(sh_path), sheet_name="Data", header=None)
    d = raw.iloc[8:].copy()
    d = d.rename(columns={0: "date", 1: "P", 3: "E", 4: "CPI", 12: "CAPE"})
    d = d[pd.to_numeric(d["date"], errors="coerce").notna()].copy()
    d["date"] = pd.to_numeric(d["date"])
    d["year"] = d["date"].astype(int)
    d["month"] = ((d["date"] - d["year"]) * 100).round().astype(int)
    d = d[(d["month"] >= 1) & (d["month"] <= 12)]
    d["period"] = d["year"].astype(str) + "-" + d["month"].astype(str).str.zfill(2)
    for c in ["P", "E", "CPI", "CAPE"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    with open(os.path.join(snapshot_dir, "S_AI_SHILLER_YALE_20261022.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["period", "sp500_price", "earnings", "cpi", "cape"])
        for r in d[["period", "P", "E", "CPI", "CAPE"]].itertuples(index=False):
            w.writerow(r)
    os.remove(sh_path)
    cape = d.dropna(subset=["CAPE"])
    cape_2000 = cape[cape.period == "2000-01"].CAPE.iloc[0]
    cape_2021 = cape[cape.period == "2021-01"].CAPE.iloc[0]
    cape_last = cape.iloc[-1]
    shiller_max = cape.loc[cape.CAPE.idxmax()]

    # 10. multpl Shiller P/E monthly table (secondary reprint of Shiller CAPE)
    mp_raw = get("https://www.multpl.com/shiller-pe/table/by-month")
    mp_html_path = os.path.join(snapshot_dir, "S_AI_MULTIPL_CAPE_20261022.html")
    save(mp_html_path, mp_raw)
    mpt = pd.read_html(io.StringIO(mp_raw.decode("utf-8", "replace")))[0]
    mpt["date"] = pd.to_datetime(mpt["Date"], format="%b %d, %Y")
    mpt["value"] = pd.to_numeric(mpt["Value"], errors="coerce")
    mpt = mpt.dropna().sort_values("date")
    with open(os.path.join(snapshot_dir, "S_AI_MULTIPL_CAPE_20261022.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "shiller_cape"])
        for dt, v in zip(mpt["date"], mpt["value"]):
            w.writerow([dt.date().isoformat(), v])
    os.remove(mp_html_path)
    cape_now = mpt.iloc[-1]

    # ---------------- snapshots: publication files ----------------
    copies = [
        ("imf_gfsr_apr2026.pdf", "S_AI_IMF_GFSR_20261022.pdf",
         "http://web.archive.org/web/20260706023605/https://www.imf.org/-/media/files/publications/gfsr/2026/april/english/text.pdf"),
        ("ecb_fsr_202605.pdf", "S_AI_ECB_FSR_20261022.pdf",
         "https://www.ecb.europa.eu/press/financial-stability-publications/fsr/pdf/ecb.fsr202605~50566915a7.en.pdf"),
        ("boe_fsr_jul2026.pdf", "S_AI_BOE_FSR_20261022.pdf",
         "https://www.bankofengland.co.uk/-/media/boe/files/financial-stability-report/2026/financial-stability-report-july-2026.pdf"),
        ("fed_fsr.pdf", "S_AI_FED_FSR_20261022.pdf",
         "https://www.federalreserve.gov/publications/files/financial-stability-report-20251107.pdf"),
        ("bis_aer2025.pdf", "S_AI_BIS_AER_20261022.pdf",
         "http://web.archive.org/web/2026/https://www.bis.org/publications/aer-2025.pdf"),
        ("nzsf_ar2026.pdf", "S_AI_NZSUPER_ANNUAL_20261022.pdf",
         "https://nzsuperfund.nz/assets/Publications/Annual-Reports/2026-Annual-Report/NZ-Super-Fund-Annual-Report-2026_web.pdf"),
        ("fma_ks_ar2026.html", "S_AI_FMA_KIWISAVER_20261022.html",
         "https://www.fma.govt.nz/news/all-releases/media-releases/kiwisaver-annual-report-2026/"),
        ("snz_migration.html", "S_AI_STATSNZ_MIGRATION_20261022.html",
         "https://www.stats.govt.nz/information-releases/international-migration-june-2026/"),
    ]
    for staged, dest, url in copies:
        try:
            copy_staged(os.path.join(staging, staged), os.path.join(snapshot_dir, dest), url)
        except Exception as e:
            print("snapshot copy failed:", dest, e)

    # ---------------- derived series ----------------
    spp = parse_bis(os.path.join(snapshot_dir, "S_AI_BIS_SPP_20261022.csv"))
    spp_real = [(p, v) for p, v, r in spp if r["VALUE"] == "R" and r["UNIT_MEASURE"] == "628"]
    spp_nom = [(p, v) for p, v, r in spp if r["VALUE"] == "N" and r["UNIT_MEASURE"] == "628"]
    gfc_pt = peak_trough(spp_real, "2007-01", "2011-12")
    cur_pt = peak_trough(spp_real, "2021-01", "2026-12")
    dot_change = next(v for p, v in spp_real if p.startswith("2002-Q4")) / next(
        v for p, v in spp_real if p.startswith("2000-Q1")) - 1
    c19 = next(v for p, v in spp_real if p.startswith("2019-Q4"))
    c20 = next(v for p, v in spp_real if p.startswith("2020-Q4"))
    c70 = next(v for p, v in spp_real if p.startswith("1970-Q1"))
    c90 = next(v for p, v in spp_real if p.startswith("1990-Q4"))

    cpi = parse_bis(os.path.join(snapshot_dir, "S_AI_BIS_LONG_CPI_20261022.csv"))
    cpi_s = sorted(cpi, key=lambda x: x[0])
    cpi_yoy = []
    for i in range(12, len(cpi_s)):
        p0, v0 = cpi_s[i - 12][0], cpi_s[i - 12][1]
        p1, v1 = cpi_s[i][0], cpi_s[i][1]
        cpi_yoy.append((p1, (v1 / v0 - 1) * 100))

    def cpi_peak(a, b):
        s = [x for x in cpi_yoy if a <= x[0][:7] <= b]
        return max(s, key=lambda x: x[1])

    cbpol = parse_bis(os.path.join(snapshot_dir, "S_AI_BIS_CBPOL_20261022.csv"))
    cbpol_s = sorted(cbpol, key=lambda x: x[0])

    cg = parse_bis(os.path.join(snapshot_dir, "S_AI_BIS_CREDIT_GDP_20261022.csv"))
    cg_s = sorted(cg, key=lambda x: x[0])

    # ---------------- tidy panels ----------------
    # market_concentration.csv
    nd_dates = [x[0] for x in nd]
    nd_close = dict(nd)

    def nd_drawdown(a, b):
        s = [(d_, v) for d_, v in nd if a <= d_.isoformat() <= b]
        pk = max(s, key=lambda x: x[1])
        tr = min([x for x in s if x[0] >= pk[0]], key=lambda x: x[1])
        return pk, tr, (tr[1] / pk[1] - 1) * 100

    dc = nd_drawdown("2000-01-01", "2003-12-31")
    gf = nd_drawdown("2007-01-01", "2009-12-31")
    cv = nd_drawdown("2020-02-01", "2020-04-30")
    y22 = nd_drawdown("2021-01-01", "2023-12-31")
    rec = nd_drawdown("2026-01-01", "2026-12-31")
    last_dt, last_close = nd[-1]
    with open(os.path.join(out_dir, "market_concentration.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["period", "indicator", "value", "unit", "official_flag", "source_id", "locator", "note"])
        w.writerow(["2026-10-20", "S&P 500 top-10 weight (SPY holdings)", round(top10_sum, 2), "percent of fund",
                    "official", "S_AI_SSGA_SPY", "SPY holdings xlsx, 'As of 20-Oct-2026', top 10 rows",
                    "sum of the 10 largest constituent weights of the S&P 500 tracker"])
        w.writerow(["2026-10-20", "NVIDIA weight in S&P 500 (SPY holdings)", round(nvda_w, 2), "percent of fund",
                    "official", "S_AI_SSGA_SPY", "SPY holdings xlsx, 'As of 20-Oct-2026', row NVIDIA CORP",
                    "single largest constituent of the S&P 500 tracker"])
        w.writerow(["2026-10-21", "Shiller CAPE", round(float(cape_now["value"]), 2), "ratio",
                    "secondary", "S_AI_MULTIPL_CAPE", "multpl.com Shiller P/E table, latest row",
                    "third-party reprint of the Shiller CAPE; not a statistical-agency series"])
        w.writerow(["2000-01", "Shiller CAPE", round(float(cape_2000), 2), "ratio", "secondary",
                    "S_AI_SHILLER_YALE", "ie_data.xls, Data sheet, row 2000.01, CAPE column",
                    "dot-com peak reference value"])
        w.writerow(["2021-01", "Shiller CAPE", round(float(cape_2021), 2), "ratio", "secondary",
                    "S_AI_SHILLER_YALE", "ie_data.xls, Data sheet, row 2021.01, CAPE column",
                    "2021 valuation peak reference value"])
        w.writerow([str(cape_last["period"]), "Shiller CAPE", round(float(cape_last["CAPE"]), 2), "ratio",
                    "secondary", "S_AI_SHILLER_YALE", "ie_data.xls, Data sheet, last CAPE observation",
                    "last observation in the Yale file retrieved on 2026-10-22 (series ends before 2026)"])
        w.writerow(["2000-03-10 to 2002-10-09", "Nasdaq Composite drawdown", round(dc[2], 2), "percent",
                    "official", "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes", "peak-to-trough"])
        w.writerow(["2007-10-31 to 2009-03-09", "Nasdaq Composite drawdown", round(gf[2], 2), "percent",
                    "official", "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes", "peak-to-trough"])
        w.writerow([f"{cv[0][0].isoformat()} to {cv[1][0].isoformat()}", "Nasdaq Composite drawdown",
                    round(cv[2], 2), "percent", "official", "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes",
                    "peak-to-trough, February-March 2020"])
        w.writerow([f"{y22[0][0].isoformat()} to {y22[1][0].isoformat()}", "Nasdaq Composite drawdown",
                    round(y22[2], 2), "percent", "official", "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes",
                    "peak-to-trough, 2021-2022"])
        w.writerow([f"{rec[0][0].isoformat()} to {rec[1][0].isoformat()}", "Nasdaq Composite drawdown",
                    round(rec[2], 2), "percent", "official", "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes",
                    "drawdown from the 2026 peak to the latest 2026 low; market still near record"])
        w.writerow([last_dt.isoformat(), "Nasdaq Composite level", round(last_close, 2), "index points",
                    "official", "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes, latest available session",
                    "latest close before the access date"])
        w.writerow(["2025-11", "Share of Fed survey contacts citing AI as a salient risk",
                    30, "percent of surveyed contacts", "official", "S_AI_FED_FSR",
                    "Federal Reserve Financial Stability Report, November 2025, p.11, Survey of Salient Risks",
                    "Fall 2025 survey; Spring 2025 figure was 9 percent"])

    # ai_credit.csv
    with open(os.path.join(out_dir, "ai_credit.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "indicator", "value", "unit", "value_type", "source_id", "locator", "note"])
        w.writerow(["2026-04", "Projected AI-related capital expenditure through 2029", 3400, "USD billion",
                    "projected level", "S_AI_IMF_GFSR",
                    "IMF GFSR April 2026, PDF p.41 and p.43",
                    "IMF staff projection; $3.4 trillion over 2025-2029"])
        w.writerow(["2026-04", "Projected data-centre securitization by 2028", 150, "USD billion",
                    "projected level", "S_AI_IMF_GFSR", "IMF GFSR April 2026, PDF p.56",
                    "forecaster expectation cited by the IMF"])
        w.writerow(["2026-04", "Estimated AI and digital infrastructure sectoral inflows, 2025", 270,
                    "USD billion", "level", "S_AI_IMF_GFSR", "IMF GFSR April 2026, PDF p.56",
                    "IMF citing UNCTAD (2026)"])
        w.writerow(["2026-07", "Five AI hyperscalers' share of outstanding US IG debt, end-2025", 3,
                    "percent", "share", "S_AI_BOE_FSR",
                    "BoE FSR July 2026, PDF p.28 (printed p.27)",
                    "stock outstanding at end-2025"])
        w.writerow(["2026-05", "Five AI hyperscalers' share of US IG debt issuance, early May 2026",
                    15, "percent", "share (at least)", "S_AI_BOE_FSR",
                    "BoE FSR July 2026, PDF p.28 (printed p.27)",
                    "year-to-date issuance; source reports 'over 15%'"])
        w.writerow(["2026-07", "AI issuers' share of non-refinance US high-yield issuance, 2026 to date",
                    41, "percent", "share", "S_AI_BOE_FSR",
                    "BoE FSR July 2026, PDF p.29 (printed p.28)", "compared with 1% of the JPM HY index at end-2025"])
        w.writerow(["2026-07", "AI issuers' share of JPM US high-yield bond index, end-2025", 1,
                    "percent", "share", "S_AI_BOE_FSR", "BoE FSR July 2026, PDF p.29 (printed p.28)", ""])
        w.writerow(["2026-07", "Barclays estimate: AI hyperscaler 2026 investment financed by IG issuance",
                    240, "USD billion", "estimate", "S_AI_BOE_FSR",
                    "BoE FSR July 2026, PDF p.28 (printed p.27)", "bank estimate cited by the BoE"])
        w.writerow(["2026-07", "JP Morgan estimate: aggregate funding needed for AI chips over five years",
                    2000, "USD billion", "estimate (at least)", "S_AI_BOE_FSR",
                    "BoE FSR July 2026, PDF p.30 (printed p.29)", "bank estimate cited by the BoE"])
        w.writerow(["2026-07", "OECD estimate: private credit share of AI investment, 2024", 9, "percent",
                    "share", "S_AI_BOE_FSR", "BoE FSR July 2026, PDF p.29 (printed p.28)",
                    "estimate cited by the BoE"])
        w.writerow(["2026-07", "OECD estimate: private credit share of AI investment, 2025", 34, "percent",
                    "share", "S_AI_BOE_FSR", "BoE FSR July 2026, PDF p.29 (printed p.28)",
                    "estimate cited by the BoE"])
        w.writerow(["2026-05", "ECB: share of AI data-centre buildout potentially funded by private credit",
                    30, "percent", "share (up to)", "S_AI_ECB_FSR",
                    "ECB Financial Stability Review May 2026, PDF p.141, footnote 181",
                    "market intelligence cited by the ECB"])
        w.writerow(["2026-05", "Expected AI data-centre buildout funding need", 3000, "USD billion",
                    "projected level", "S_AI_ECB_FSR",
                    "ECB Financial Stability Review May 2026, PDF p.141, footnote 181", ""])
        w.writerow(["2025-12", "Bloomberg consensus: AI hyperscaler capital expenditure in 2028",
                    600, "USD billion", "consensus estimate (less than)", "S_AI_BOE_FSR",
                    "BoE FSR July 2026, PDF p.37", "consensus at the time of the December 2025 FSR"])

    # nz_transmission.csv
    eer = []
    for label, rows in eer_parts:
        for r in rows:
            try:
                eer.append((label, r["TIME_PERIOD"], float(r["OBS_VALUE"])))
            except (KeyError, ValueError):
                pass
    nom = sorted([(p, v) for lab, p, v in eer if lab == "nominal_broad"], key=lambda x: x[0])
    real = sorted([(p, v) for lab, p, v in eer if lab == "real_broad"], key=lambda x: x[0])
    nom_last = nom[-1]
    nom_yoy = next(v for p, v in nom if p == f"{int(nom_last[0][:4])-1}{nom_last[0][4:]}") if any(
        p == f"{int(nom_last[0][:4])-1}{nom_last[0][4:]}" for p, v in nom) else None
    real_last = real[-1]
    real_yoy = next((v for p, v in real if p == f"{int(real_last[0][:4])-1}{real_last[0][4:]}"), None)
    latest_cg = cg_s[-1]
    latest_cbpol = cbpol_s[-1]

    with open(os.path.join(out_dir, "nz_transmission.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["period", "indicator", "value", "unit", "change", "source_id", "locator", "note"])
        w.writerow([nom_last[0], "BIS nominal broad effective exchange rate, New Zealand",
                    round(nom_last[1], 2), "index (2020=100)",
                    f"{(nom_last[1]/nom_yoy-1)*100:.2f} percent year-on-year" if nom_yoy else "",
                    "S_AI_BIS_EER", "BIS WS_EER, NZ nominal broad (64 economies)",
                    "substitute for the RBNZ trade-weighted index, which was not accessible"])
        w.writerow([real_last[0], "BIS real broad effective exchange rate, New Zealand",
                    round(real_last[1], 2), "index (2020=100)",
                    f"{(real_last[1]/real_yoy-1)*100:.2f} percent year-on-year" if real_yoy else "",
                    "S_AI_BIS_EER", "BIS WS_EER, NZ real broad", ""])
        w.writerow(["2026-06-30", "NZ Super Fund listed equities allocation", 57, "percent of fund",
                    "49% developed markets, 4% New Zealand, 4% emerging markets",
                    "S_AI_NZSUPER_ANNUAL", "NZ Super Fund Annual Report 2026, PDF p.51, asset allocation at 30 June 2026",
                    "Reference Portfolio is 75% global equities, 20% fixed income, 5% NZ equities"])
        w.writerow(["2026-06-30", "NZ Super Fund net assets", 93.5, "NZD billion",
                    "up from 82.8 in 2024/25", "S_AI_NZSUPER_ANNUAL",
                    "NZ Super Fund Annual Report 2026, PDF p.44, financial statements",
                    "exact net assets NZD 93,497,038 thousand"])
        w.writerow(["2026-03-31", "KiwiSaver funds under management", 138.8, "NZD billion",
                    "up 12.8 percent year-on-year", "S_AI_FMA_KIWISAVER",
                    "FMA KiwiSaver Annual Report 2026 media release",
                    "year to 31 March 2026; contributions NZD 13.2bn, investment returns NZD 10.7bn"])
        w.writerow(["2026-03-31", "KiwiSaver growth-fund assets", 68, "NZD billion",
                    "largest single fund category", "S_AI_FMA_KIWISAVER",
                    "FMA KiwiSaver Annual Report 2026 media release", ""])
        w.writerow(["2026-03-31", "KiwiSaver average member balance", 40340, "NZD",
                    "up 11 percent year-on-year", "S_AI_FMA_KIWISAVER",
                    "FMA KiwiSaver Annual Report 2026 media release", ""])
        w.writerow(["2026-03-31", "KiwiSaver membership", 3.44, "million members", "",
                    "S_AI_FMA_KIWISAVER", "FMA KiwiSaver Annual Report 2026 media release", ""])
        w.writerow(["2026-06", "Net migration, June 2026 year (provisional)", 17600, "persons",
                    "plus or minus 1,500; prior June 2025 year +10,300",
                    "S_AI_STATSNZ_MIGRATION",
                    "Stats NZ International migration: June 2026, key facts",
                    "provisional estimates; annual net migration peaked at 133,700 in the October 2023 year"])
        w.writerow([latest_cg[0], "BIS credit-to-GDP ratio, NZ private non-financial sector",
                    round(latest_cg[1], 2), "percent of GDP", "", "S_AI_BIS_CREDIT_GDP",
                    "BIS WS_CREDIT_GAP, NZ, total credit to private non-financial sector",
                    "credit-to-GDP ratio, not the gap; quarterly"])
        w.writerow([latest_cbpol[0], "New Zealand official cash rate (BIS central bank policy rate)",
                    round(latest_cbpol[1], 2), "percent per annum", "", "S_AI_BIS_CBPOL",
                    "BIS WS_CBPOL, NZ, daily", "latest available observation"])

    # historical_analogues.csv
    def nd_ep(a, b):
        return nd_drawdown(a, b)

    with open(os.path.join(out_dir, "historical_analogues.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["episode", "period", "variable", "value", "unit", "change", "source_id", "locator", "note"])
        # dot-com
        w.writerow(["dot-com 2000-02", f"{dc[0][0].isoformat()} to {dc[1][0].isoformat()}",
                    "Nasdaq Composite drawdown", round(dc[2], 2), "percent", "peak-to-trough",
                    "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes", "US technology index"])
        w.writerow(["dot-com 2000-02", "2000-Q1 to 2002-Q4", "New Zealand real house price index change",
                    round(dot_change * 100, 2), "percent", "cumulative change", "S_AI_BIS_SPP",
                    "BIS WS_SPP, NZ, real, 2010=100", "NZ house prices rose through the dot-com bust"])
        # GFC
        w.writerow(["GFC 2007-11", f"{gf[0][0].isoformat()} to {gf[1][0].isoformat()}",
                    "Nasdaq Composite drawdown", round(gf[2], 2), "percent", "peak-to-trough",
                    "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes", ""])
        w.writerow(["GFC 2007-11", f"{gfc_pt[0][0]} peak to {gfc_pt[1][0]} trough",
                    "New Zealand real house price index", round(gfc_pt[2], 2), "percent",
                    "peak-to-trough", "S_AI_BIS_SPP", "BIS WS_SPP, NZ, real, 2010=100",
                    f"peak {gfc_pt[0][1]:.2f}, trough {gfc_pt[1][1]:.2f}"])
        cpi_gfc = cpi_peak("2007-01", "2011-12")
        w.writerow(["GFC 2007-11", cpi_gfc[0][:7], "New Zealand CPI inflation (year-on-year)",
                    round(cpi_gfc[1], 2), "percent", "", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, NZ",
                    "peak year-on-year rate in the window"])
        wb_gfc = max([x for x in wb_rows if 2008 <= x[0] <= 2011], key=lambda x: x[1])
        w.writerow(["GFC 2007-11", str(wb_gfc[0]), "New Zealand unemployment rate", round(wb_gfc[1], 2),
                    "percent of labour force", "", "S_AI_WB_UNEMPLOYMENT",
                    "World Bank SL.UEM.TOTL.ZS, NZ, annual",
                    "modeled ILO estimate; peak in the window"])
        # 1970s-80s inflation
        cpi80 = cpi_peak("1970-01", "1990-12")
        w.writerow(["1970s-80s inflation", cpi80[0][:7], "New Zealand CPI inflation (year-on-year)",
                    round(cpi80[1], 2), "percent", "", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, NZ",
                    "peak year-on-year rate in the window"])
        w.writerow(["1970s-80s inflation", "1970-Q1 to 1990-Q4", "New Zealand real house price index change",
                    round((c90 / c70 - 1) * 100, 2), "percent", "cumulative change", "S_AI_BIS_SPP",
                    "BIS WS_SPP, NZ, real, 2010=100", "nominal appreciation against high inflation"])
        wb80 = [x for x in wb_rows if 1975 <= x[0] <= 1990]
        # World Bank NZ series starts in 1991; the 1970s-80s unemployment path could
        # not be verified from an accessible official source and is recorded as a gap.
        if wb80:
            wb80 = max(wb80, key=lambda x: x[1])
            w.writerow(["1970s-80s inflation", str(wb80[0]), "New Zealand unemployment rate",
                        round(wb80[1], 2), "percent of labour force", "", "S_AI_WB_UNEMPLOYMENT",
                        "World Bank SL.UEM.TOTL.ZS, NZ, annual", "modeled ILO estimate; peak in the window"])
        # 2020 pandemic
        w.writerow(["2020 pandemic", f"{cv[0][0].isoformat()} to {cv[1][0].isoformat()}",
                    "Nasdaq Composite drawdown", round(cv[2], 2), "percent", "peak-to-trough",
                    "S_AI_NASDAQ_COMP", "Nasdaq COMP daily closes", "February-March 2020"])
        w.writerow(["2020 pandemic", "2019-Q4 to 2020-Q4", "New Zealand real house price index change",
                    round((c20 / c19 - 1) * 100, 2), "percent", "cumulative change", "S_AI_BIS_SPP",
                    "BIS WS_SPP, NZ, real, 2010=100", ""])
        cpi_cv = cpi_peak("2020-01", "2021-12")
        w.writerow(["2020 pandemic", cpi_cv[0][:7], "New Zealand CPI inflation (year-on-year)",
                    round(cpi_cv[1], 2), "percent", "", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, NZ",
                    "peak year-on-year rate in the window"])
        wb_cv = max([x for x in wb_rows if x[0] in (2020, 2021)], key=lambda x: x[1])
        w.writerow(["2020 pandemic", str(wb_cv[0]), "New Zealand unemployment rate", round(wb_cv[1], 2),
                    "percent of labour force", "", "S_AI_WB_UNEMPLOYMENT",
                    "World Bank SL.UEM.TOTL.ZS, NZ, annual", "modeled ILO estimate; peak"])
        # 2021-2026 housing downturn (current)
        w.writerow(["2021-2026 housing downturn", f"{cur_pt[0][0]} peak to {cur_pt[1][0]} trough",
                    "New Zealand real house price index", round(cur_pt[2], 2), "percent",
                    "peak-to-trough", "S_AI_BIS_SPP", "BIS WS_SPP, NZ, real, 2010=100",
                    f"peak {cur_pt[0][1]:.2f}, trough {cur_pt[1][1]:.2f}; latest quarter may be revised"])
        cpi_cur = cpi_peak("2021-01", "2026-12")
        w.writerow(["2021-2026 housing downturn", cpi_cur[0][:7], "New Zealand CPI inflation (year-on-year)",
                    round(cpi_cur[1], 2), "percent", "", "S_AI_BIS_LONG_CPI", "BIS WS_LONG_CPI, NZ",
                    "peak year-on-year rate in the window"])
        cb_peak = max([x for x in cbpol_s if "2021" <= x[0][:4] <= "2026"], key=lambda x: x[1])
        w.writerow(["2021-2026 housing downturn", cb_peak[0], "New Zealand official cash rate (peak)",
                    round(cb_peak[1], 2), "percent per annum", "", "S_AI_BIS_CBPOL",
                    "BIS WS_CBPOL, NZ, daily", "peak in the tightening cycle"])
        w.writerow(["2021-2026 housing downturn", latest_cbpol[0], "New Zealand official cash rate (latest)",
                    round(latest_cbpol[1], 2), "percent per annum", "", "S_AI_BIS_CBPOL",
                    "BIS WS_CBPOL, NZ, daily", "latest available observation"])

    # ---------------- print summary for claims ----------------
    print("=== summary values ===")
    print("SPY as of", spy_asof, "| top10 weight", round(top10_sum, 2), "| NVDA weight", round(nvda_w, 2))
    print("SPY top 10:", [(n, t, round(w, 2)) for n, t, w in top10])
    print("CAPE latest multpl", cape_now["date"].date(), round(float(cape_now["value"]), 2))
    print("CAPE 2000-01", round(float(cape_2000), 2), "| 2021-01", round(float(cape_2021), 2),
          "| last Yale", cape_last["period"], round(float(cape_last["CAPE"]), 2),
          "| Yale max", shiller_max["period"], round(float(shiller_max["CAPE"]), 2))
    print("Nasdaq drawdowns: dotcom", round(dc[2], 2), dc[0][0], dc[1][0],
          "| gfc", round(gf[2], 2), gf[0][0], gf[1][0],
          "| covid", round(cv[2], 2), cv[0][0], cv[1][0],
          "| 2022", round(y22[2], 2), y22[0][0], y22[1][0],
          "| 2026", round(rec[2], 2), rec[0][0], rec[1][0])
    print("Nasdaq last", last_dt, last_close)
    print("NZ real HPI: GFC", gfc_pt, "| current", cur_pt)
    print("NZ real HPI change 2000Q1-2002Q4", round(dot_change * 100, 2),
          "| 1970Q1-1990Q4", round((c90 / c70 - 1) * 100, 2),
          "| 2019Q4-2020Q4", round((c20 / c19 - 1) * 100, 2))
    print("CPI peaks: 1970-90", cpi80, "| GFC", cpi_gfc, "| 2020-21", cpi_cv, "| 2021-26", cpi_cur)
    print("OCR: peak 2021-26", cb_peak, "| latest", latest_cbpol)
    print("WB unemployment: GFC peak", wb_gfc, "| 1980s peak", wb80, "| 2020s peak", wb_cv,
          "| 2000", [x for x in wb_rows if x[0] == 2000], "| 2002", [x for x in wb_rows if x[0] == 2002],
          "| latest", wb_rows[-1])
    print("EER nominal", nom_last, "yoy", nom_yoy, "| real", real_last, "yoy", real_yoy)
    print("credit-to-GDP latest", latest_cg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--staging", default=STAGING)
    a = ap.parse_args()
    build(a.snapshot_dir, a.out_dir, a.staging)
