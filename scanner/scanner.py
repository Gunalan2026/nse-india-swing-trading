
"""Nifty 500 daily swing-setup research scanner (paper trading only)."""
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
import yfinance as yf

CONSTITUENTS = "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv"
OUTPUT = Path("scanner/results.json")
HEADERS = {"User-Agent": "Mozilla/5.0"}
IST = ZoneInfo("Asia/Kolkata")


def num(value, digits=2):
    return round(float(value), digits) if pd.notna(value) and np.isfinite(float(value)) else None


def prepare(raw):
    if raw.empty:
        raise ValueError("Empty price history")
    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    required = ["Open", "High", "Low", "Close", "Volume"]
    if any(c not in df for c in required):
        raise ValueError("Missing OHLCV columns")
    df = df[required].apply(pd.to_numeric, errors="coerce")
    dates = pd.DatetimeIndex(df.index)
    dates = dates.tz_convert(IST) if dates.tz is not None else dates.tz_localize(IST)
    df.index = pd.DatetimeIndex(dates.date)
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df = df[df.index.date < datetime.now(IST).date()]
    valid = np.isfinite(df.to_numpy()).all(axis=1)
    valid &= (df[["Open", "High", "Low", "Close"]] > 0).all(axis=1).to_numpy()
    valid &= (df["Volume"] >= 0).to_numpy()
    valid &= (df["High"] >= df[["Open", "Close", "Low"]].max(axis=1)).to_numpy()
    valid &= (df["Low"] <= df[["Open", "Close", "High"]].min(axis=1)).to_numpy()
    df = df.loc[valid]
    if len(df) < 210:
        raise ValueError(f"Insufficient completed valid candles: {len(df)}")
    return df


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
        "reasons": [label for test, label in [
            (trend, "EMA20 > EMA50 > EMA200 and price above EMA20"),
            (50 <= rsi[last] <= 70, "RSI in 50-70 range"),
            (positive_macd, "MACD above signal"),
            (adx[last] >= 20 and directional, "ADX >= 20 with +DI > -DI"),
            (vr >= 1.2, "Volume >= 1.2x prior 20-day average"),
            (breakout, "Close above previous 20-day high"),
        ] if test]
    }


def main():
    response = requests.get(CONSTITUENTS, headers=HEADERS, timeout=30)
    response.raise_for_status()
    universe = pd.read_csv(io.BytesIO(response.content))
    if "Symbol" not in universe.columns or len(universe) < 400:
        raise RuntimeError("Invalid Nifty 500 constituent list")
    symbols = list(dict.fromkeys(universe["Symbol"].dropna().astype(str).str.strip()))
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
    ranked = sorted(results, key=lambda x: (x["score"], x["volume_ratio"]), reverse=True)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "universe_count": len(symbols), "analyzed_count": len(results),
        "failed_count": len(errors), "provider": "Yahoo Finance via yfinance (unofficial; delayed)",
        "methodology": "Heuristic technical ranking, using completed prior IST trading days; no news or backtest validation yet",
        "disclaimer": "Research/paper trading only. Scores are not probabilities; entry/stop/target are illustrative, not orders.",
        "candidates": [x for x in ranked if x["status"] == "SETUP"][:20],
        "watchlist": [x for x in ranked if x["status"] == "WATCH"][:20],
        "top_ranked": ranked[:20], "status_counts": {
            s: sum(x["status"] == s for x in results) for s in ("SETUP", "WATCH", "NO TRADE")
        },
        "errors_sample": errors[:25]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Universe={len(symbols)} analyzed={len(results)} failures={len(errors)} setups={report['status_counts']['SETUP']} watches={report['status_counts']['WATCH']}")


if __name__ == "__main__":
    main()
    
