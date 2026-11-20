"""Check scanner prices against NSE's and BSE's official daily bhavcopies.

Runs after scanner.py. Reads scanner/results.json, downloads the NSE and
BSE equity bhavcopies for the scan's main session, compares each stock's
latest close, and writes the outcome back into results.json.

- NSE is the primary check: a close more than NSE_TOLERANCE_PCT away from
  NSE marks the stock DATA MISMATCH and removes it from candidates.
- BSE is the independent second check. Stocks are matched by ISIN (BSE
  symbols do not always equal NSE symbols). The same stock trades at
  slightly different prices on the two exchanges, so BSE uses a wider
  tolerance. A BSE difference only adds a warning - unless NSE could not
  be reached, in which case BSE decides DATA MISMATCH instead.
- If an exchange cannot be reached, its check is marked "unavailable".
  This script never deletes the scanner output.
Research and paper trading only.
"""
import io
import json
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import requests

RESULTS = Path("scanner/results.json")
CONSTITUENTS = Path("scanner/nifty500_constituents.csv")
NSE_TOLERANCE_PCT = 0.5
BSE_TOLERANCE_PCT = 1.0
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Accept": "*/*",
}
NSE_SERIES = ["EQ", "BE", "BZ", "SM", "ST"]

COLUMN_NAMES = {
    # UDiFF format (NSE and BSE)
    "TckrSymb": "symbol", "SctySrs": "series", "ISIN": "isin",
    "OpnPric": "open", "HghPric": "high", "LwPric": "low",
    "ClsPric": "close", "TtlTradgVol": "volume",
    # legacy NSE full bhavcopy
    "SYMBOL": "symbol", "SERIES": "series", "OPEN_PRICE": "open",
    "HIGH_PRICE": "high", "LOW_PRICE": "low", "CLOSE_PRICE": "close",
    "TTL_TRD_QNTY": "volume",
}


def nse_urls(day):
    return [
        "https://nsearchives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_{day:%Y%m%d}_F_0000.csv.zip",
        "https://nsearchives.nseindia.com/products/content/"
        f"sec_bhavdata_full_{day:%d%m%Y}.csv",
    ]


def bse_urls(day):
    return [
        "https://www.bseindia.com/download/BhavCopy/Equity/"
        f"BhavCopy_BSE_CM_0_0_0_{day:%Y%m%d}_F_0000.CSV",
    ]


def read_table(content):
    if content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
            content = z.read(name)
    if content.lstrip()[:1] == b"<":
        raise ValueError("received an HTML page, not a CSV file")
    df = pd.read_csv(io.BytesIO(content))
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={k: v for k, v in COLUMN_NAMES.items() if k in df.columns})
    needed = ["symbol", "series", "close", "volume"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError("bhavcopy columns not recognised: " + ", ".join(missing))
    keep = [c for c in ["symbol", "series", "isin", "close", "volume"] if c in df.columns]
    df = df[keep].copy()
    for c in ["symbol", "series", "isin"]:
        if c in df:
            df[c] = df[c].astype(str).str.strip()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    if len(df) < 500:
        raise ValueError(f"only {len(df)} rows; file looks incomplete")
    return df


def nse_table(df):
    df = df[df["series"].isin(NSE_SERIES)]
    rank = {s: i for i, s in enumerate(NSE_SERIES)}
    df = df.assign(_r=df["series"].map(rank)).sort_values("_r")
    return df.drop_duplicates("symbol").drop(columns="_r").set_index("symbol")


def bse_table(df):
    # Prefer ordinary equity groups; drop rows without a close.
    df = df[df["close"].notna()]
    return df.drop_duplicates("isin" if "isin" in df else "symbol")


def download(urls, label, referer):
    problems = []
    for url in urls:
        try:
            r = requests.get(url, headers={**HEADERS, "Referer": referer}, timeout=30)
            r.raise_for_status()
            return read_table(r.content), url
        except Exception as exc:
            problems.append(f"{url}: {str(exc)[:120]}")
            print(f"{label} source failed:", problems[-1])
    raise RuntimeError(" | ".join(problems))


def constituent_isins():
    """Symbol -> ISIN from the saved Nifty 500 list (fallback if NSE is down)."""
    try:
        df = pd.read_csv(CONSTITUENTS)
        df.columns = [str(c).strip() for c in df.columns]
        return dict(zip(df["Symbol"].astype(str).str.strip(),
                        df["ISIN Code"].astype(str).str.strip()))
    except Exception:
        return {}


def ours_by_symbol(report):
    """Latest close/volume per symbol from the scanner report."""
    rows = {}
    for sym, v in (report.get("latest_closes") or {}).items():
        rows[sym] = {"as_of": v[0], "close": v[1], "volume": v[2]}
    for key in ("candidates", "watchlist", "top_ranked"):
        for x in report.get(key, []):
            rows.setdefault(x["symbol"], {"as_of": x["as_of"], "close": x["close"], "volume": None})
    return rows


def compare(ours, day, lookup, tolerance):
    """lookup(sym) -> (close, volume) or None."""
    mismatched, missing, info, matched = [], [], {}, 0
    for sym, o in ours.items():
        if o["as_of"] != day.isoformat():
            continue  # already flagged STALE DATA by the scanner
        row = lookup(sym)
        if row is None or not pd.notna(row[0]) or row[0] <= 0:
            missing.append(sym)
            continue
        close, volume = float(row[0]), row[1]
        diff = abs(o["close"] - close) / close * 100
        info[sym] = {"close": close, "volume": int(volume) if pd.notna(volume) else None,
                     "diff_pct": round(diff, 3)}
        if diff > tolerance:
            mismatched.append({"symbol": sym, "ours": o["close"], "exchange": close,
                               "diff_pct": round(diff, 2)})
        else:
            matched += 1
    return {"compared": matched + len(mismatched), "matched": matched,
            "mismatched": mismatched, "not_found": missing}, info


def main():
    report = json.loads(RESULTS.read_text(encoding="utf-8"))
    day = date.fromisoformat(report["main_session"])
    ours = ours_by_symbol(report)
    stamp = {"checked_utc": datetime.now(timezone.utc).isoformat(), "session": day.isoformat()}

    # --- NSE (primary) ---
    nse = None
    nse_info = {}
    try:
        raw, url = download(nse_urls(day), "NSE", "https://www.nseindia.com/")
        nse = nse_table(raw)
        result, nse_info = compare(
            ours, day,
            lambda s: (nse.at[s, "close"], nse.at[s, "volume"]) if s in nse.index else None,
            NSE_TOLERANCE_PCT)
        report["nse_check"] = {**stamp, "status": "ok", "source": url,
                               "tolerance_pct": NSE_TOLERANCE_PCT, **result}
    except Exception as exc:
        report["nse_check"] = {**stamp, "status": "unavailable", "reason": str(exc)[:400]}

    # --- BSE (independent second source), matched by ISIN ---
    bse_info = {}
    try:
        raw, url = download(bse_urls(day), "BSE", "https://www.bseindia.com/")
        bse = bse_table(raw)
        by_isin = bse.set_index("isin") if "isin" in bse else None
        by_symbol = bse.drop_duplicates("symbol").set_index("symbol")
        isin_of = constituent_isins()
        if nse is not None and "isin" in nse:
            isin_of.update(nse["isin"].to_dict())

        def bse_lookup(sym):
            isin = isin_of.get(sym)
            if by_isin is not None and isin in by_isin.index:
                r = by_isin.loc[isin]
            elif sym in by_symbol.index:   # fallback when NSE ISINs are unknown
                r = by_symbol.loc[sym]
            else:
                return None
            return r["close"], r["volume"]

        result, bse_info = compare(ours, day, bse_lookup, BSE_TOLERANCE_PCT)
        report["bse_check"] = {**stamp, "status": "ok", "source": url,
                               "tolerance_pct": BSE_TOLERANCE_PCT,
                               "matched_by": "ISIN" if isin_of else "symbol", **result}
    except Exception as exc:
        report["bse_check"] = {**stamp, "status": "unavailable", "reason": str(exc)[:400]}

    # --- Apply to listed stocks ---
    nse_ok = report["nse_check"]["status"] == "ok"
    bse_ok = report["bse_check"]["status"] == "ok"
    nse_bad = {m["symbol"] for m in report["nse_check"].get("mismatched", [])}
    bse_bad = {m["symbol"] for m in report["bse_check"].get("mismatched", [])}
    # BSE decides exclusion only when NSE was unavailable.
    exclude = nse_bad if nse_ok else (bse_bad if bse_ok else set())

    for key in ("candidates", "watchlist", "top_ranked"):
        for x in report.get(key, []):
            s = x["symbol"]
            if s in nse_info:
                x.update(nse_close=nse_info[s]["close"], nse_volume=nse_info[s]["volume"],
                         close_diff_pct=nse_info[s]["diff_pct"])
            if s in bse_info:
                x.update(bse_close=bse_info[s]["close"], bse_diff_pct=bse_info[s]["diff_pct"])
            if s in bse_bad and s not in exclude:
                x["bse_warning"] = f"Close differs from BSE by {bse_info[s]['diff_pct']}%"
            if s in exclude and x["status"] in ("SETUP", "WATCH"):
                x["status"], x["candidate"] = "DATA MISMATCH", False
                src = "NSE" if nse_ok else "BSE"
                x["reasons"] = [f"Close differs from {src} bhavcopy"] + x["reasons"]
    report["candidates"] = [x for x in report.get("candidates", []) if x["status"] == "SETUP"]
    report["watchlist"] = [x for x in report.get("watchlist", []) if x["status"] == "WATCH"]

    RESULTS.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    for name in ("nse_check", "bse_check"):
        c = report[name]
        if c["status"] == "ok":
            print(f"{name}: compared={c['compared']} matched={c['matched']} "
                  f"mismatched={len(c['mismatched'])} not_found={len(c['not_found'])} "
                  f"source={c['source']}")
            for m in c["mismatched"][:15]:
                print("  MISMATCH", m)
        else:
            print(f"{name}: unavailable - {c['reason'][:200]}")


if __name__ == "__main__":
    sys.exit(main())
