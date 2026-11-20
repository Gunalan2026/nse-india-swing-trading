
"""Nifty 500 daily swing-setup research scanner (paper trading only)."""
import io
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from chart_data import validate_prices

CONSTITUENT_SOURCES = [
    "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
    "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
]
CONSTITUENT_CACHE = Path("scanner/nifty500_constituents.csv")
OUTPUT = Path("scanner/results.json")
HEADERS = {"User-Agent": "Mozilla/5.0"}
IST = ZoneInfo("Asia/Kolkata")

# Paper trading rules (agreed 20 Nov 2026).
CAPITAL = 100000
ALLOCATION_PER_TRADE = 30000
MAX_RISK_PER_TRADE = 500
DAILY_LOSS_LIMIT = 2000


def num(value, digits=2):
    return round(float(value), digits) if pd.notna(value) and np.isfinite(float(value)) else None


def prepare(raw):
    """Use exactly the same validation as the chart data, so the scanner
    and the charts always see the same sessions and prices."""
    df, quality = validate_prices(raw)
    return df


def position_size(entry, stop):
    """Quantity limited by both the allocation and the max risk per trade."""
    risk_per_share = entry - stop
    if stop <= 0 or risk_per_share <= 0:
        return {"paper_qty": None, "paper_cost": None, "paper_risk": None}
    qty = min(int(ALLOCATION_PER_TRADE // entry), int(MAX_RISK_PER_TRADE // risk_per_share))
    if qty < 1:
        return {"paper_qty": 0, "paper_cost": 0, "paper_risk": 0}
    return {"paper_qty": qty, "paper_cost": round(qty * entry, 2),
            "paper_risk": round(qty * risk_per_share, 2)}


def indicators(df):
    close, high, low, volume = (df[k].astype(float) for k in ("Close", "High", "Low", "Volume"))
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    delta = close.diff()
    avg_gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rsi = 100 - 100/(1 + avg_gain/avg_loss.replace(0, np.nan))
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100)
    rsi = rsi.mask((avg_loss == 0) & (avg_gain == 0), 50)
    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    tr = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    up, down = high.diff(), -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    plus_di = 100 * plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr.replace(0, np.nan)
    dx = 100 * (plus_di-minus_di).abs() / (plus_di+minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    vol_avg = volume.shift(1).rolling(20).mean()
    prior_high = high.shift(1).rolling(20).max()
    last = df.index[-1]
    fields = [close[last], ema20[last], ema50[last], ema200[last], rsi[last], macd[last], macd_signal[last], atr[last], plus_di[last], minus_di[last], adx[last], vol_avg[last], prior_high[last]]
    if not all(pd.notna(v) and np.isfinite(v) for v in fields) or vol_avg[last] <= 0 or atr[last] <= 0:
        raise ValueError("Invalid latest indicators")
    price = float(close[last])
    vr = float(volume[last] / vol_avg[last])
    trend = price > ema20[last] > ema50[last] > ema200[last]
    positive_macd = macd[last] > macd_signal[last]
    directional = plus_di[last] > minus_di[last]
    breakout = price > prior_high[last]
    # Transparent heuristic score, NOT a calibrated probability.
    score = (25 if trend else 0) + (15 if 50 <= rsi[last] <= 70 else 0) + (15 if positive_macd else 0) + (15 if adx[last] >= 20 and directional else 0) + (15 if vr >= 1.2 else 0) + (15 if breakout else 0)
    entry = round(price, 2)
    stop = round(price - 2*float(atr[last]), 2)
    risk = entry - stop
    target = round(entry + 2*risk, 2) if risk > 0 else None
    status = "SETUP" if score >= 75 and trend and directional and risk > 0 else "WATCH" if score >= 55 else "NO TRADE"
    return {
        "as_of": last.strftime("%Y-%m-%d"), "close": entry,
        "rsi14": num(rsi[last], 1), "ema20": num(ema20[last]),
        "ema50": num(ema50[last]), "ema200": num(ema200[last]),
        "adx14": num(adx[last], 1), "plus_di": num(plus_di[last], 1),
        "minus_di": num(minus_di[last], 1), "macd": num(macd[last]),
        "macd_signal": num(macd_signal[last]), "atr14": num(atr[last]),
        "volume_ratio": num(vr), "breakout20": bool(breakout),
        "trend_up": bool(trend), "score": int(score), "status": status,
        "candidate": status == "SETUP", "illustrative_entry": entry,
        "illustrative_stop": stop if stop > 0 else None,
        "illustrative_target": target if stop > 0 else None,
        "risk_reward": 2.0 if stop > 0 else None,
        **position_size(entry, stop),
        "reasons": [label for test, label in [
            (trend, "EMA20 > EMA50 > EMA200 and price above EMA20"),
            (50 <= rsi[last] <= 70, "RSI in 50-70 range"),
            (positive_macd, "MACD above signal"),
            (adx[last] >= 20 and directional, "ADX >= 20 with +DI > -DI"),
            (vr >= 1.2, "Volume >= 1.2x prior 20-day average"),
            (breakout, "Close above previous 20-day high"),
        ] if test]
    }


def parse_universe(content):
    universe = pd.read_csv(io.BytesIO(content))
    if "Symbol" not in universe.columns or len(universe) < 400:
        raise ValueError("not a valid Nifty 500 constituent list")
    return list(dict.fromkeys(universe["Symbol"].dropna().astype(str).str.strip()))


def load_universe():
    """Download the Nifty 500 list, trying each source in turn.
    A successful download is saved; if every source fails, the last
    saved copy is used and the report says so."""
    problems = []
    for url in CONSTITUENT_SOURCES:
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            symbols = parse_universe(response.content)
            CONSTITUENT_CACHE.write_bytes(response.content)
            print(f"Universe: {len(symbols)} symbols from {url}")
            return symbols, url
        except Exception as exc:
            problems.append(f"{url}: {str(exc)[:100]}")
            print(f"Universe source failed: {problems[-1]}")
    if CONSTITUENT_CACHE.exists():
        symbols = parse_universe(CONSTITUENT_CACHE.read_bytes())
        source = f"saved copy ({CONSTITUENT_CACHE}); all downloads failed"
        print(f"Universe: {len(symbols)} symbols from {source}")
        return symbols, source
    raise RuntimeError("Could not load Nifty 500 list: " + " | ".join(problems))


def main():
    symbols, universe_source = load_universe()
    results, errors = [], []
    for i, symbol in enumerate(symbols, 1):
        try:
            raw = yf.download(symbol + ".NS", period="2y", interval="1d", auto_adjust=True, progress=False, threads=False, timeout=15)
            metrics = indicators(prepare(raw))
            metrics["symbol"] = symbol
            results.append(metrics)
        except Exception as exc:
            errors.append({"symbol": symbol, "reason": str(exc)[:120]})
        if i % 50 == 0:
            print(f"Processed {i}/{len(symbols)}; valid={len(results)}; failed={len(errors)}", flush=True)
    if len(results) < 400:
        raise RuntimeError(f"Insufficient valid stocks ({len(results)}); refusing to replace prior report")
    # Every stock should end on the same session. Stocks behind the main
    # session have late data: list them and keep them out of candidates.
    sessions = Counter(x["as_of"] for x in results)
    main_session = sessions.most_common(1)[0][0]
    stale = []
    for x in results:
        if x["as_of"] != main_session:
            x["status"], x["candidate"] = "STALE DATA", False
            x["reasons"] = [f"Latest candle {x['as_of']} is behind {main_session}"] + x["reasons"]
            stale.append({"symbol": x["symbol"], "as_of": x["as_of"]})
    ranked = sorted(results, key=lambda x: (x["score"], x["volume_ratio"]), reverse=True)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "universe_count": len(symbols), "universe_source": universe_source, "analyzed_count": len(results),
        "failed_count": len(errors), "main_session": main_session, "stale_symbols": stale, "latest_sessions": dict(sorted(Counter(x["as_of"] for x in results).items())), "provider": "Yahoo Finance via yfinance (unofficial; delayed)", "paper_rules": {"capital": CAPITAL, "allocation_per_trade": ALLOCATION_PER_TRADE, "max_risk_per_trade": MAX_RISK_PER_TRADE, "daily_loss_limit": DAILY_LOSS_LIMIT},
        "methodology": "Heuristic technical ranking on completed sessions (same validation as charts: day included after 16:00 IST, holiday placeholder candles removed); no news or backtest validation yet",
        "disclaimer": "Research/paper trading only. Scores are not probabilities; entry/stop/target are illustrative, not orders.",
        "candidates": [x for x in ranked if x["status"] == "SETUP"][:20],
        "watchlist": [x for x in ranked if x["status"] == "WATCH"][:20],
        "top_ranked": ranked[:20], "status_counts": {
            s: sum(x["status"] == s for x in results) for s in ("SETUP", "WATCH", "NO TRADE", "STALE DATA")
        },
        "errors_sample": errors[:25], "errors": errors
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Universe={len(symbols)} analyzed={len(results)} failures={len(errors)} setups={report['status_counts']['SETUP']} watches={report['status_counts']['WATCH']}")


if __name__ == "__main__":
    main()
    
