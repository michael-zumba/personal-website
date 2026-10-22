#!/usr/bin/env python3
"""
Rebuild of the zero-citation "attention" measure for
"What Is Accounting and Finance Research For in the AI Era?"

Reads ONLY data/crossref_articles.csv (the cleaned Crossref research-article
frame) and matches each DOI against the live OpenAlex API. Writes only inside
evidence/expansion/attention_rebuild/.

Key design choices (see NOTES.md for rationale):
  * Cohort = Crossref journal-articles with publication_year in {2020,2021,2022}.
    The year is Crossref's issue-year hierarchy, NOT OpenAlex's online-first year.
  * Citations window = the three CALENDAR YEARS starting at the Crossref
    publication year: [y, y+1, y+2], summed from OpenAlex counts_by_year.
  * Records whose OpenAlex `type` != "article" are excluded (front matter,
    paratext, preprints, errata, reviews are dropped; reviews are reported
    separately as a sensitivity check).
  * Duplicate DOIs in OpenAlex are collapsed to the highest-cited record.
  * An article is "zero-citation" iff the summed window is 0 (no positive year).

Usage:
    python3 attention_rebuild.py            # uses cached batches when present
    python3 attention_rebuild.py --refresh  # ignore cache, re-query everything
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CROSSREF = os.path.join(PROJECT, "data", "crossref_articles.csv")
OLD_ATTENTION = os.path.join(PROJECT, "data", "openalex_attention_articles.csv")

OUT_WINDOWS = os.path.join(HERE, "openalex_doi_windows.csv")
OUT_SUMMARY = os.path.join(HERE, "attention_summary.csv")
OUT_COHORT_YEAR = os.path.join(HERE, "attention_cohort_by_year.csv")
OUT_REQUESTS = os.path.join(HERE, "openalex_requests.csv")
OUT_CROSSCHECK = os.path.join(HERE, "attention_crosscheck.csv")
CACHE = os.path.join(HERE, "openalex_batch_cache.jsonl")
LOOKUP_CACHE = os.path.join(HERE, "openalex_doi_lookup_cache.jsonl")
OUT_RETRY = os.path.join(HERE, "openalex_unmatched_resolution.csv")

COHORT_YEARS = (2020, 2021, 2022)
BATCH_SIZE = 50
SELECT = "id,doi,publication_year,cited_by_count,counts_by_year,type"
MAILTO = "research@example.org"  # OpenAlex polite pool; no API key required
UA = "dsh-attention-rebuild/1.0 (mailto:%s)" % MAILTO
BASE = "https://api.openalex.org/works"
SLEEP_BETWEEN = 0.15  # ~6 req/s, well under the 10 req/s polite-pool limit


def norm_doi(d):
    if d is None or (isinstance(d, float) and pd.isna(d)):
        return None
    s = str(d).strip().lower()
    for p in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if s.startswith(p):
            s = s[len(p):]
    return s


def load_cache():
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cache[rec["key"]] = rec["results"]
    return cache


def append_cache(key, results):
    with open(CACHE, "a") as fh:
        fh.write(json.dumps({"key": key, "results": results}) + "\n")


def http_get_json(url, max_tries=8):
    """GET JSON with exponential backoff on 429/5xx/transient network errors."""
    delay = 2.0
    last_err = None
    for attempt in range(1, max_tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            last_err = "HTTP %s" % e.code
            if e.code in (429, 500, 502, 503, 504, 508):
                retry_after = e.headers.get("Retry-After") if e.headers else None
                wait = float(retry_after) if retry_after else delay
                print("  %s on attempt %d/%d; sleeping %.1fs" % (last_err, attempt, max_tries, wait),
                      file=sys.stderr)
                time.sleep(wait)
                delay = min(delay * 2, 60)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_err = "%s: %s" % (type(e).__name__, e)
            print("  %s on attempt %d/%d; sleeping %.1fs" % (last_err, attempt, max_tries, delay),
                  file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 60)
        except json.JSONDecodeError as e:
            last_err = "bad JSON: %s" % e
            time.sleep(delay)
            delay = min(delay * 2, 60)
    raise RuntimeError("giving up on %s (%s)" % (url[:200], last_err))


def build_batches(dois):
    return [dois[i:i + BATCH_SIZE] for i in range(0, len(dois), BATCH_SIZE)]


def build_url(batch):
    return (BASE + "?filter=" + urllib.parse.quote(
        "doi:" + "|".join(batch), safe=":/._-;()") +
        "&select=" + urllib.parse.quote(SELECT) +
        "&per-page=" + str(len(batch)) + "&mailto=" + MAILTO)


def fetch_batch(batch, cache, requests_log):
    """Fetch one batch, using/refreshing the cache; split on HTTP 400/414."""
    key = hashlib.sha1("|".join(batch).encode()).hexdigest()
    if key in cache:
        requests_log.append({"batch_id": len(requests_log) + 1,
                             "n_dois": len(batch), "source": "cache",
                             "url": build_url(batch)})
        return cache[key]
    url = build_url(batch)
    try:
        results = http_get_json(url)["results"]
    except urllib.error.HTTPError as e:
        if e.code in (400, 414) and len(batch) > 1:
            half = len(batch) // 2
            print("  HTTP %s (n=%d); splitting batch into %d+%d"
                  % (e.code, len(batch), half, len(batch) - half), file=sys.stderr)
            time.sleep(1.0)
            return (fetch_batch(batch[:half], cache, requests_log) +
                    fetch_batch(batch[half:], cache, requests_log))
        raise
    append_cache(key, results)
    requests_log.append({"batch_id": len(requests_log) + 1,
                         "n_dois": len(batch), "source": "api", "url": url})
    time.sleep(SLEEP_BETWEEN)
    return results


def query_batches(dois, refresh=False):
    """Return (doi -> list of raw OpenAlex work dicts, list of request records)."""
    cache = {} if refresh else load_cache()
    by_doi = defaultdict(list)
    requests_log = []
    batches = build_batches(dois)
    print("Querying OpenAlex: %d DOIs in %d batches of <=%d" % (len(dois), len(batches), BATCH_SIZE))
    for i, batch in enumerate(batches, 1):
        for w in fetch_batch(batch, cache, requests_log):
            by_doi[norm_doi(w.get("doi"))].append(w)
        if i % 10 == 0 or i == len(batches):
            print("  batch %d/%d done" % (i, len(batches)), flush=True)
    return by_doi, requests_log


def load_lookup_cache():
    cache = {}
    if os.path.exists(LOOKUP_CACHE):
        with open(LOOKUP_CACHE) as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cache[rec["doi"]] = rec
    return cache


def retry_unmatched(dois, refresh=False):
    """Second pass for DOIs the 50-value batch filter did not return.

    Uses the single-record DOI endpoint, which also follows OpenAlex DOI
    redirects. Returns (retry_rows, resolved_by_doi dict). Empirically 9 DOIs
    that exist are missed by the batch filter; this pass recovers them and
    documents the rest (mostly OpenAlex redirects to SSRN preprint records).
    """
    cache = {} if refresh else load_lookup_cache()
    rows, resolved = [], {}
    n_new = 0
    for i, doi in enumerate(dois, 1):
        if doi in cache:
            rec = cache[doi]
        else:
            url = (BASE + "/https://doi.org/" + urllib.parse.quote(doi, safe=":/._-;()") +
                   "?select=" + urllib.parse.quote(SELECT) + "&mailto=" + MAILTO)
            rec = {"doi": doi, "url": url, "http_status": 200, "work": None}
            try:
                rec["work"] = http_get_json(url)
            except urllib.error.HTTPError as e:
                rec["http_status"] = e.code
            with open(LOOKUP_CACHE, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            n_new += 1
            time.sleep(0.12)
        w = rec.get("work")
        resolved_doi = norm_doi(w.get("doi")) if w else None
        rows.append({
            "doi": doi,
            "resolution": ("same_doi" if resolved_doi == doi else
                           "redirect_other_doi" if resolved_doi else
                           "http_%s" % rec.get("http_status")),
            "resolved_doi": resolved_doi or "",
            "url": rec.get("url", ""),
        })
        if resolved_doi == doi:
            resolved[doi] = w
        if i % 20 == 0 or i == len(dois):
            print("  retry %d/%d" % (i, len(dois)), flush=True)
    return pd.DataFrame(rows), resolved


def pick_record(works):
    """Collapse duplicate OpenAlex records for one DOI."""
    if len(works) == 1:
        return works[0], 1
    ranked = sorted(works, key=lambda w: (w.get("cited_by_count") or 0), reverse=True)
    return ranked[0], len(works)


def wilson(k, n, z=1.959964):
    """95% Wilson score interval for a binomial share."""
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="ignore local cache, re-query OpenAlex")
    args = ap.parse_args()

    assert os.path.exists(CROSSREF), CROSSREF
    cr = pd.read_csv(CROSSREF)
    cr["doi_norm"] = cr["doi"].map(norm_doi)
    cohort = cr[cr["publication_year"].isin(COHORT_YEARS)].copy()
    cohort = cohort.drop_duplicates(subset=["doi_norm"], keep="first")
    cohort["field"] = cohort["field"].fillna("")
    print("Cohort: %d Crossref research articles, years %s, %d journals"
          % (len(cohort), list(COHORT_YEARS), cohort["journal"].nunique()))

    dois = sorted(cohort["doi_norm"].unique().tolist())
    by_doi, requests_log = query_batches(dois, refresh=args.refresh)

    pd.DataFrame(requests_log).to_csv(OUT_REQUESTS, index=False)

    # Second pass: DOIs the batch filter did not return. The single-record
    # endpoint recovers a handful the batch filter misses and identifies the
    # rest (dominantly OpenAlex redirects to SSRN preprint records).
    batch_unmatched = [d for d in dois if d not in by_doi]
    print("Retrying %d DOIs unmatched by the batch filter (single-record endpoint)"
          % len(batch_unmatched))
    retry_df, retry_resolved = retry_unmatched(batch_unmatched, refresh=args.refresh)
    retry_df.to_csv(OUT_RETRY, index=False)
    for d, w in retry_resolved.items():
        by_doi[d].append(w)
    retry_counts = retry_df["resolution"].value_counts().to_dict()
    print("  retry outcomes: %s" % retry_counts)

    # ---- resolve each cohort DOI to the chosen OpenAlex work -----------------
    rows = []
    seen_openalex_ids = {}
    n_multi = 0
    n_dupe_id_collisions = 0
    type_counts = defaultdict(int)
    for _, art in cohort.iterrows():
        doi = art["doi_norm"]
        works = by_doi.get(doi, [])
        rec = {
            "journal": art["journal"],
            "field": art["field"],
            "crossref_year": int(art["publication_year"]),
            "doi": doi,
            "match_status": "unmatched",
            "match_method": "",
            "openalex_id": "",
            "openalex_year": "",
            "year_mismatch": "",
            "openalex_type": "",
            "n_openalex_records": len(works),
            "c_window_y1": "",
            "c_window_y2": "",
            "c_window_y3": "",
            "citations_first_3y": "",
            "zero_citations_first_3y": "",
            "window_years": "",
        }
        if works:
            chosen, n = pick_record(works)
            if n > 1:
                n_multi += 1
            for w in works:
                type_counts[w.get("type") or "(none)"] += 1
            oid = chosen.get("id") or ""
            otype = chosen.get("type") or ""
            rec["match_status"] = "excluded_nonarticle" if otype != "article" else "matched"
            rec["match_method"] = "batch" if doi not in retry_resolved else "single_record_retry"
            rec["openalex_id"] = oid
            rec["openalex_year"] = chosen.get("publication_year") or ""
            rec["openalex_type"] = otype
            rec["c_window_y1"], rec["c_window_y2"], rec["c_window_y3"] = "", "", ""
            rec["window_years"] = "%d-%d" % (art["publication_year"], art["publication_year"] + 2)
            if oid and oid in seen_openalex_ids and seen_openalex_ids[oid] != doi:
                n_dupe_id_collisions += 1
                rec["match_status"] = "excluded_duplicate_work"
            elif oid:
                seen_openalex_ids[oid] = doi
            if otype == "article" and rec["match_status"] == "matched":
                y = int(art["publication_year"])
                cby = {int(e["year"]): int(e["cited_by_count"] or 0)
                       for e in (chosen.get("counts_by_year") or [])}
                vals = [cby.get(y + k, 0) for k in range(3)]
                rec["c_window_y1"], rec["c_window_y2"], rec["c_window_y3"] = vals
                total = sum(vals)
                rec["citations_first_3y"] = total
                rec["zero_citations_first_3y"] = int(total == 0)
                oy = chosen.get("publication_year")
                rec["year_mismatch"] = int(oy != y) if oy else ""
        rows.append(rec)

    win = pd.DataFrame(rows)
    win["unmatched_resolution"] = win["doi"].map(
        retry_df.set_index("doi")["resolution"] if len(retry_df) else {})
    win.to_csv(OUT_WINDOWS, index=False)

    # ---- cohort counts per journal/year -------------------------------------
    cy = pd.crosstab(cohort["journal"], cohort["publication_year"])
    cy.columns = ["cohort_%d" % c for c in cy.columns]
    cy["cohort_n"] = cy.sum(axis=1)
    cy = cy.reset_index()
    cy.to_csv(OUT_COHORT_YEAR, index=False)

    # ---- per-journal summary ------------------------------------------------
    matched = win[win["match_status"] == "matched"].copy()
    summary = []
    for journal in sorted(cohort["journal"].unique()):
        coh_n = int((cohort["journal"] == journal).sum())
        m = matched[matched["journal"] == journal]
        matched_n = len(m)
        zeros = int((m["zero_citations_first_3y"] == 1).sum())
        vals = m["citations_first_3y"].astype(float)
        summary.append({
            "journal": journal,
            "field": cohort.loc[cohort["journal"] == journal, "field"].iloc[0],
            "cohort_n": coh_n,
            "matched_n": matched_n,
            "coverage": round(matched_n / coh_n, 4) if coh_n else None,
            "unmatched_n": int((win["journal"] == journal).sum() -
                               ((win["journal"] == journal) & win["match_status"].isin(
                                   ["matched", "excluded_nonarticle",
                                    "excluded_duplicate_work"])).sum()),
            "unmatched_ssrn_redirect_n": int(((win["journal"] == journal) &
                                              (win["unmatched_resolution"] ==
                                               "redirect_other_doi")).sum()),
            "unmatched_absent_n": int(((win["journal"] == journal) &
                                       (win["match_status"] == "unmatched") &
                                       (win["unmatched_resolution"] !=
                                        "redirect_other_doi")).sum()),
            "excluded_nonarticle_n": int(((win["journal"] == journal) &
                                          (win["match_status"] == "excluded_nonarticle")).sum()),
            "duplicate_work_excluded_n": int(((win["journal"] == journal) &
                                              (win["match_status"] == "excluded_duplicate_work")).sum()),
            "zero_n": zeros,
            "zero_share": round(zeros / matched_n, 4) if matched_n else None,
            "zero_share_ci95_lo": round(wilson(zeros, matched_n)[0], 4) if matched_n else None,
            "zero_share_ci95_hi": round(wilson(zeros, matched_n)[1], 4) if matched_n else None,
            "mean_citations_first_3y": round(float(vals.mean()), 2) if matched_n else None,
            "median_citations_first_3y": round(float(vals.median()), 1) if matched_n else None,
            "p25": round(float(vals.quantile(0.25)), 1) if matched_n else None,
            "p75": round(float(vals.quantile(0.75)), 1) if matched_n else None,
            "year_mismatch_n": int((m["year_mismatch"] == 1).sum()),
        })
    summ = pd.DataFrame(summary).sort_values("zero_share", ascending=False)

    pooled_cohort = len(cohort)
    pooled_matched = len(matched)
    pooled_zero = int((matched["zero_citations_first_3y"] == 1).sum())
    pooled = {
        "journal": "ALL POOLED",
        "field": "",
        "cohort_n": pooled_cohort,
        "matched_n": pooled_matched,
        "coverage": round(pooled_matched / pooled_cohort, 4),
        "unmatched_n": int((win["match_status"] == "unmatched").sum()),
        "unmatched_ssrn_redirect_n": int((win["unmatched_resolution"] == "redirect_other_doi").sum()),
        "unmatched_absent_n": int(((win["match_status"] == "unmatched") &
                                   (win["unmatched_resolution"] != "redirect_other_doi")).sum()),
        "excluded_nonarticle_n": int((win["match_status"] == "excluded_nonarticle").sum()),
        "duplicate_work_excluded_n": int((win["match_status"] == "excluded_duplicate_work").sum()),
        "zero_n": pooled_zero,
        "zero_share": round(pooled_zero / pooled_matched, 4),
        "zero_share_ci95_lo": round(wilson(pooled_zero, pooled_matched)[0], 4),
        "zero_share_ci95_hi": round(wilson(pooled_zero, pooled_matched)[1], 4),
        "mean_citations_first_3y": round(float(matched["citations_first_3y"].astype(float).mean()), 2),
        "median_citations_first_3y": round(float(matched["citations_first_3y"].astype(float).median()), 1),
        "p25": round(float(matched["citations_first_3y"].astype(float).quantile(0.25)), 1),
        "p75": round(float(matched["citations_first_3y"].astype(float).quantile(0.75)), 1),
        "year_mismatch_n": int((matched["year_mismatch"] == 1).sum()),
    }
    summ = pd.concat([summ, pd.DataFrame([pooled])], ignore_index=True)
    summ.to_csv(OUT_SUMMARY, index=False)

    # ---- sensitivity: include OpenAlex "review" as article, and treat
    #      unmatched as zero (worst case) -----------------------------------
    rev = win[win["openalex_type"] == "review"]
    print("\nSensitivity: %d cohort DOIs resolved to OpenAlex type 'review' (excluded per brief)"
          % len(rev))
    unmatched_n = int((win["match_status"] == "unmatched").sum())
    excl_n = int((win["match_status"] == "excluded_nonarticle").sum())
    dupe_work_n = int((win["match_status"] == "excluded_duplicate_work").sum())
    worst_matched = pooled_zero + unmatched_n
    print("Worst case, matched-style denominator (unmatched counted as zero): %d/%d = %.2f%%"
          % (worst_matched, pooled_matched + unmatched_n,
             100.0 * worst_matched / (pooled_matched + unmatched_n)))
    print("Worst case, full cohort denominator (unmatched+excluded counted as zero): %d/%d = %.2f%%"
          % (pooled_zero + unmatched_n + excl_n + dupe_work_n, pooled_cohort,
             100.0 * (pooled_zero + unmatched_n + excl_n + dupe_work_n) / pooled_cohort))
    print("Unmatched: %d (OpenAlex->SSRN redirect: %d; absent/other: %d); "
          "excluded non-article: %d; excluded duplicate work: %d; "
          "duplicate-DOI records collapsed: %d"
          % (unmatched_n,
             int((win["unmatched_resolution"] == "redirect_other_doi").sum()),
             int(((win["match_status"] == "unmatched") &
                  (win["unmatched_resolution"] != "redirect_other_doi")).sum()),
             excl_n, dupe_work_n, n_multi))

    # ---- cross-check 10 matched DOIs against single-record endpoints --------
    rng = random.Random(20261022)
    sample = rng.sample(sorted(matched["doi"].tolist()), min(10, len(matched)))
    check_rows = []
    print("\nCross-checking %d DOIs against single-record /works/<doi> endpoints" % len(sample))
    for doi in sample:
        url = (BASE + "/https://doi.org/" + urllib.parse.quote(doi, safe=":/._-;()") +
               "?select=" + urllib.parse.quote(SELECT) + "&mailto=" + MAILTO)
        w = http_get_json(url)
        y = int(win.loc[win["doi"] == doi, "crossref_year"].iloc[0])
        cby = {int(e["year"]): int(e["cited_by_count"] or 0) for e in (w.get("counts_by_year") or [])}
        total = sum(cby.get(y + k, 0) for k in range(3))
        wrow = win[win["doi"] == doi].iloc[0]
        check_rows.append({
            "doi": doi,
            "batch_total": int(wrow["citations_first_3y"]),
            "single_total": int(total),
            "agree": int(int(wrow["citations_first_3y"]) == int(total)),
            "batch_openalex_id": wrow["openalex_id"],
            "single_openalex_id": w.get("id"),
            "match_status": wrow["match_status"],
            "url": url,
        })
        time.sleep(SLEEP_BETWEEN)
    chk = pd.DataFrame(check_rows)
    chk.to_csv(OUT_CROSSCHECK, index=False)
    print("  cross-check agreement: %d/%d" % (int(chk["agree"].sum()), len(chk)))

    # ---- old-vs-new diagnostic on shared DOIs ------------------------------
    old_note = ""
    if os.path.exists(OLD_ATTENTION):
        old = pd.read_csv(OLD_ATTENTION)
        old["doi_norm"] = old["doi"].map(norm_doi)
        old = old.drop_duplicates("doi_norm")
        j = matched.merge(old[["doi_norm", "journal", "publication_year", "citations_first_3y",
                               "zero_citations_first_3y"]],
                          left_on="doi", right_on="doi_norm", suffixes=("", "_old"))
        if len(j):
            flips = int(((j["zero_citations_first_3y"] == 1) &
                         (j["zero_citations_first_3y_old"] == 0)).sum())
            n_old = int((j["zero_citations_first_3y_old"] == 1).sum())
            n_new = int((j["zero_citations_first_3y"] == 1).sum())
            old_note = ("Old-vs-new on %d shared matched DOIs: old zero = %d (%.1f%%), "
                        "new zero = %d (%.1f%%); old-window zero that becomes non-zero = %d; "
                        "new zero that old counted non-zero = %d"
                        % (len(j), n_old, 100.0 * n_old / len(j),
                           n_new, 100.0 * n_new / len(j), flips,
                           int(((j["zero_citations_first_3y"] == 0) &
                                (j["zero_citations_first_3y_old"] == 1)).sum())))
            print("\n" + old_note)

    # ---- print summary -----------------------------------------------------
    print("\n=== PER-JOURNAL SUMMARY (matched-based) ===")
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(summ[["journal", "cohort_n", "matched_n", "coverage", "unmatched_n",
                    "unmatched_ssrn_redirect_n", "unmatched_absent_n",
                    "excluded_nonarticle_n", "zero_n", "zero_share",
                    "zero_share_ci95_lo", "zero_share_ci95_hi",
                    "median_citations_first_3y", "mean_citations_first_3y",
                    "year_mismatch_n"]].to_string(index=False))
    print("\nPooled zero share: %d/%d = %.2f%%" % (pooled_zero, pooled_matched,
                                                   100.0 * pooled_zero / pooled_matched))
    print("Per-journal zero share range: %.2f%% (%s) to %.2f%% (%s)" % (
        100.0 * summ["zero_share"].iloc[0], summ["journal"].iloc[0],
        100.0 * summ["zero_share"].iloc[-1], summ["journal"].iloc[-1]))
    print("Excluded non-article records: %d (OpenAlex types: %s)"
          % (pooled["excluded_nonarticle_n"],
             dict(sorted(type_counts.items(), key=lambda kv: -kv[1]))))
    print("DOI-level OpenAlex duplicates collapsed: %d; duplicate-work collisions: %d"
          % (n_multi, n_dupe_id_collisions))
    print("\nWrote: %s\n       %s\n       %s\n       %s\n       %s\n       %s"
          % (OUT_WINDOWS, OUT_SUMMARY, OUT_COHORT_YEAR, OUT_REQUESTS, OUT_CROSSCHECK, OUT_RETRY))
    if args.refresh is False and os.path.exists(CACHE):
        print("Batch cache: %s" % CACHE)


if __name__ == "__main__":
    main()
