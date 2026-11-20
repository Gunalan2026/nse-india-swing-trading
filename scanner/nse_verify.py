"""Check scanner prices against NSE's official daily bhavcopy.

Runs after scanner.py. Reads scanner/results.json, downloads the NSE
capital-market bhavcopy for the scan's main session, compares each stock's
latest close and volume, and writes the outcome back into results.json.

Stocks whose close differs from NSE by more than CLOSE_TOLERANCE_PCT are
marked DATA MISMATCH and removed from candidates. If NSE cannot be reached
the scan is kept but marked "NSE check unavailable" - this script never
deletes the scanner output.
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
CLOSE_TOLERANCE_PCT = 0.5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
}
SERIES_PREFERENCE = ["EQ", "BE", "BZ", "SM", "ST"]


def bhavcopy_urls(day):
    """New UDiFF format first, then the older full bhavcopy."""
    return [
        "https://nsearchives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_{day:%Y%m%d}_F_0000.csv.zip",
        "https://nsearchives.nseindia.com/products/content/"
        f"sec_bhavdata_full_{day:%d%m%Y}.csv",
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
    return df


def normalise(df):
    """Return one row per symbol: symbol, series, open, high, low, close, volume."""
    names = {
        # UDiFF format
        "TckrSymb": "symbol", "SctySrs": "series", "OpnPric": "open",
        "HghPric": "high", "LwPric": "low", "ClsPric": "close",
        "TtlTradgVol": "volume",
        # legacy full bhavcopy
        "SYMBOL": "symbol", "SERIES": "series", "OPEN_PRICE": "open",
        "HIGH_PRICE": "high", "LOW_PRICE": "low", "CLOSE_PRICE": "close",
        "TTL_TRD_QNTY": "volume",
    }
    df = df.rename(columns={k: v for k, v in names.items() if k in df.columns})
    needed = ["symbol", "series", "open", "high", "low", "close", "volume"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError("bhavcopy columns not recognised: " + ", ".join(missing))
    df = df[needed].copy()
    df["symbol"] = df["symbol"].astype(str).str.strip()
    df["series"] = df["series"].astype(str).str.strip()
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["series"].isin(SERIES_PREFERENCE)]
    rank = {s: i for i, s in enumerate(SERIES_PREFERENCE)}
    df = df.assign(_r=df["series"].map(rank)).sort_values("_r")
    df = df.drop_duplicates("symbol").drop(columns="_r")
    if len(df) < 500:
        raise ValueError(f"only {len(df)} equity rows; file looks incomplete")
    return df.set_index("symbol")


def download(day):
    problems = []
    for url in bhavcopy_urls(day):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return normalise(read_table(r.content)), url
        except Exception as exc:
            problems.append(f"{url}: {str(exc)[:120]}")
            print("NSE source failed:", problems[-1])
    raise RuntimeError(" | ".join(problems))


def ours_by_symbol(report):
    """Latest close/volume per symbol from the scanner report."""
    rows = {}
    for sym, v in (report.get("latest_closes") or {}).items():
        rows[sym] = {"as_of": v[0], "close": v[1], "volume": v[2]}
    for key in ("candidates", "watchlist", "top_ranked"):
        for x in report.get(key, []):
            rows.setdefault(x["symbol"], {"as_of": x["as_of"], "close": x["close"], "volume": None})
    return rows


def main():
    report = json.loads(RESULTS.read_text(encoding="utf-8"))
    day = date.fromisoformat(report["main_session"])
    check = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "session": day.isoformat(),
        "tolerance_pct": CLOSE_TOLERANCE_PCT,
    }
    try:
        nse, url = download(day)
    except Exception as exc:
        check.update(status="unavailable", reason=str(exc)[:400])
        report["nse_check"] = check
        RESULTS.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
        print("NSE check unavailable; scanner results kept and marked.")
        return

    ours = ours_by_symbol(report)
    mismatched, missing, matched = [], [], 0
    nse_info = {}
    for sym, o in ours.items():
        if o["as_of"] != day.isoformat():
            continue  # already flagged STALE DATA by the scanner
        if sym not in nse.index or not pd.notna(nse.at[sym, "close"]):
            missing.append(sym)
            continue
        n = nse.loc[sym]
        diff = abs(o["close"] - n["close"]) / n["close"] * 100
        nse_info[sym] = {"nse_close": float(n["close"]), "nse_volume": int(n["volume"]),
                         "close_diff_pct": round(diff, 3)}
        if diff > CLOSE_TOLERANCE_PCT:
            mismatched.append({"symbol": sym, "ours": o["close"],
                               "nse": float(n["close"]), "diff_pct": round(diff, 2)})
        else:
            matched += 1

    bad = {m["symbol"] for m in mismatched}
    for key in ("candidates", "watchlist", "top_ranked"):
        for x in report.get(key, []):
            x.update(nse_info.get(x["symbol"], {}))
            if x["symbol"] in bad and x["status"] in ("SETUP", "WATCH"):
                x["status"], x["candidate"] = "DATA MISMATCH", False
                x["reasons"] = ["Close differs from NSE bhavcopy"] + x["reasons"]
    report["candidates"] = [x for x in report.get("candidates", []) if x["status"] == "SETUP"]
    report["watchlist"] = [x for x in report.get("watchlist", []) if x["status"] == "WATCH"]

    check.update(status="ok", source=url, compared=matched + len(mismatched),
                 matched=matched, mismatched=mismatched, not_in_nse=missing)
    report["nse_check"] = check
    RESULTS.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(f"NSE check: compared={check['compared']} matched={matched} "
          f"mismatched={len(mismatched)} not_in_nse={len(missing)} source={url}")
    for m in mismatched[:20]:
        print("  MISMATCH", m)


if __name__ == "__main__":
    sys.exit(main())
