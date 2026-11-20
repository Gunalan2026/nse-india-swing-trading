"""Backtest the Nifty 500 swing scanner's SETUP rule on daily history.

Uses exactly the scanner's indicator formulas and SETUP rule, applied day
by day, and the morning report's entry rules:

- Signal: day t closes as SETUP (score >= 75, EMA trend up, +DI > -DI).
- Entry on day t+1 only: skip if it opens more than 2% above the signal
  close ("do not chase"); otherwise enter when price trades above the
  signal close (at the open if it opens above it). No entry -> signal
  expires.
- Stop = signal close - 2 x ATR14, target = signal close + 2 x risk.
- Exit at stop or target (gap through -> exit at the open; stop and target
  on the same day -> assume stop, the conservative case), or at the close
  after MAX_HOLD_DAYS trading days.
- Costs: ROUND_TRIP_COST_PCT of trade value per trade.

Two views:
1. "all_signals": every signal traded, one open trade per stock at a time.
   Measures the rule itself.
2. "portfolio": the paper account - max 3 open trades, Rs 500 risk and
   Rs 30,000 allocation per trade, Rs 90,000 deployable, best scores first.

Known limitation: the universe is TODAY's Nifty 500 list, so stocks that
left the index (often after falling) are missing - results are likely
somewhat optimistic (survivorship bias).
Research and paper trading only.
"""
import io
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT = Path("scanner/backtest_results.json")
CONSTITUENTS = Path("scanner/nifty500_constituents.csv")
HISTORY = "5y"
WARMUP = 210            # candles before signals are trusted (EMA200)
MAX_HOLD_DAYS = 20
NO_CHASE_PCT = 2.0
ROUND_TRIP_COST_PCT = 0.25   # brokerage, STT, charges and slippage (estimate)

CAPITAL = 100000
DEPLOYABLE = 90000
ALLOCATION_PER_TRADE = 30000
MAX_RISK_PER_TRADE = 500
MAX_OPEN = 3


def indicator_frame(df):
    """Scanner indicators and SETUP rule for every day (same formulas as
    scanner.indicators, vectorised)."""
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
    vr = volume / vol_avg

    trend = (close > ema20) & (ema20 > ema50) & (ema50 > ema200)
    directional = plus_di > minus_di
    rsi_ok = (rsi >= 50) & (rsi <= 70)
    score = (trend * 25 + rsi_ok * 15 + (macd > macd_signal) * 15
             + ((adx >= 20) & directional) * 15 + (vr >= 1.2) * 15
             + (close > prior_high) * 15)
    stop = close - 2 * atr
    valid = (pd.concat([ema200, rsi, macd_signal, atr, adx, vol_avg, prior_high], axis=1)
             .notna().all(axis=1)) & (vol_avg > 0) & (atr > 0)
    setup = valid & (score >= 75) & trend & directional & (stop > 0)
    setup.iloc[:WARMUP] = False
    return pd.DataFrame({
        "open": df["Open"], "high": high, "low": low, "close": close,
        "score": score, "rsi": rsi, "vr": vr, "atr": atr,
        "stop": stop, "target": close + 2 * (close - stop), "setup": setup,
    })


def simulate_trade(f, i):
    """Trade a signal on row i. Returns dict or None if never entered."""
    n = len(f)
    if i + 1 >= n:
        return None
    sig_close, stop, target = f["close"].iat[i], f["stop"].iat[i], f["target"].iat[i]
    j = i + 1
    o, h, l, c = (f[k].iat[j] for k in ("open", "high", "low", "close"))
    if o > sig_close * (1 + NO_CHASE_PCT / 100):
        return {"skipped": "gap_up"}
    if h <= sig_close:
        return {"skipped": "no_trigger"}
    entry = max(o, sig_close)
    risk = entry - stop
    if risk <= 0:
        return {"skipped": "no_risk"}

    exit_px, reason, k = None, None, j
    for k in range(j, min(n, j + MAX_HOLD_DAYS)):
        o, h, l, c = (f[x].iat[k] for x in ("open", "high", "low", "close"))
        if k > j and o <= stop:
            exit_px, reason = o, "stop"
            break
        if k > j and o >= target:
            exit_px, reason = o, "target"
            break
        if l <= stop:
            exit_px, reason = stop, "stop"
            break
        if h >= target:
            exit_px, reason = target, "target"
            break
    if exit_px is None:
        if k < j + MAX_HOLD_DAYS - 1:
            return {"skipped": "open_at_end"}   # data ended while trade open
        exit_px, reason = f["close"].iat[k], "time"

    cost_per_share = (entry + exit_px) / 2 * ROUND_TRIP_COST_PCT / 100
    r = (exit_px - entry - cost_per_share) / risk
    return {
        "signal_date": f.index[i].strftime("%Y-%m-%d"),
        "entry_date": f.index[j].strftime("%Y-%m-%d"),
        "exit_date": f.index[k].strftime("%Y-%m-%d"),
        "entry": round(float(entry), 2), "stop": round(float(stop), 2),
        "target": round(float(target), 2), "exit": round(float(exit_px), 2),
        "reason": reason, "r": round(float(r), 3), "days": k - j + 1,
        "score": int(f["score"].iat[i]), "rsi": round(float(f["rsi"].iat[i]), 1),
        "volume_ratio": round(float(f["vr"].iat[i]), 2),
        "cost_per_share": float(cost_per_share), "risk_per_share": float(risk),
    }


def backtest_symbol(symbol, f):
    """All signals for one stock, one open trade at a time."""
    trades, skipped = [], defaultdict(int)
    busy_until = None
    for i in np.flatnonzero(f["setup"].to_numpy()).tolist():
        if busy_until is not None and f.index[i] <= busy_until:
            continue
        t = simulate_trade(f, i)
        if t is None:
            continue
        if "skipped" in t:
            skipped[t["skipped"]] += 1
            continue
        t["symbol"] = symbol
        trades.append(t)
        busy_until = pd.Timestamp(t["exit_date"])
    return trades, dict(skipped)


def summarise(trades):
    if not trades:
        return {"trades": 0}
    r = np.array([t["r"] for t in trades])
    wins, losses = r[r > 0], r[r <= 0]
    reasons = defaultdict(int)
    for t in trades:
        reasons[t["reason"]] += 1
    return {
        "trades": len(trades),
        "win_rate_pct": round(100 * len(wins) / len(r), 1),
        "target_hit_pct": round(100 * reasons["target"] / len(r), 1),
        "stop_hit_pct": round(100 * reasons["stop"] / len(r), 1),
        "time_exit_pct": round(100 * reasons["time"] / len(r), 1),
        "avg_r": round(float(r.mean()), 3),
        "median_r": round(float(np.median(r)), 3),
        "profit_factor": round(float(wins.sum() / -losses.sum()), 2) if losses.sum() < 0 else None,
        "avg_days_held": round(float(np.mean([t["days"] for t in trades])), 1),
        "expectancy_rs_at_500_risk": round(float(r.mean()) * MAX_RISK_PER_TRADE, 0),
    }


def portfolio(trades):
    """Paper account: max 3 open, Rs 500 risk, Rs 30k allocation, Rs 90k
    deployable. Signals on the same day are taken best score first."""
    by_entry = defaultdict(list)
    for t in trades:
        by_entry[t["entry_date"]].append(t)
    open_pos, taken, equity, curve = [], [], 0.0, []
    for day in sorted(set(by_entry) | {t["exit_date"] for t in trades}):
        # New entries are taken in the morning; positions exiting today
        # free their slot only after today (conservative).
        for t in sorted(by_entry.get(day, []), key=lambda x: (-x["score"], -x["volume_ratio"])):
            in_use = sum(p["qty"] * p["entry"] for p in open_pos)
            if len(open_pos) >= MAX_OPEN:
                break
            qty = min(int(ALLOCATION_PER_TRADE // t["entry"]),
                      int(MAX_RISK_PER_TRADE // t["risk_per_share"]))
            if qty < 1 or in_use + qty * t["entry"] > DEPLOYABLE:
                continue
            if any(p["symbol"] == t["symbol"] for p in open_pos):
                continue
            pnl = qty * (t["exit"] - t["entry"] - t["cost_per_share"])
            p = {**t, "qty": qty, "pnl": round(pnl, 2)}
            open_pos.append(p)
            taken.append(p)
        still = []
        for p in open_pos:
            if p["exit_date"] == day:
                equity += p["pnl"]
            else:
                still.append(p)
        open_pos = still
        curve.append((day, round(equity, 2)))

    if not taken:
        return {"trades": 0}
    peak, max_dd = 0.0, 0.0
    for _, e in curve:
        peak = max(peak, e)
        max_dd = min(max_dd, e - peak)
    by_year = defaultdict(float)
    for p in taken:
        by_year[p["exit_date"][:4]] += p["pnl"]
    monthly = {}
    for d, e in curve:
        monthly[d[:7]] = e
    return {
        **summarise(taken),
        "net_pnl_rs": round(equity, 0),
        "return_on_capital_pct": round(100 * equity / CAPITAL, 1),
        "max_drawdown_rs": round(max_dd, 0),
        "pnl_by_year_rs": {y: round(v, 0) for y, v in sorted(by_year.items())},
        "equity_by_month_rs": monthly,
        "period": [taken[0]["entry_date"], taken[-1]["exit_date"]],
    }


def bucket_stats(trades, key, edges):
    out = {}
    for lo, hi, label in edges:
        sel = [t for t in trades if lo <= t[key] < hi]
        out[label] = summarise(sel)
    return out


def run(price_frames, universe_count, failures):
    all_trades, skipped = [], defaultdict(int)
    for sym, f in price_frames.items():
        trades, sk = backtest_symbol(sym, f)
        all_trades += trades
        for k, v in sk.items():
            skipped[k] += v
    all_trades.sort(key=lambda t: (t["entry_date"], t["symbol"]))
    years = defaultdict(list)
    for t in all_trades:
        years[t["entry_date"][:4]].append(t)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "rules": {
            "signal": "Scanner SETUP: score >= 75, EMA20>EMA50>EMA200 with price above EMA20, +DI > -DI",
            "entry": f"Next day only, above signal close; skip if it opens > {NO_CHASE_PCT}% higher",
            "stop": "Signal close - 2 x ATR14", "target": "Signal close + 2 x risk (2:1)",
            "max_hold_days": MAX_HOLD_DAYS, "round_trip_cost_pct": ROUND_TRIP_COST_PCT,
            "same_day_stop_and_target": "counted as stop (conservative)",
            "history": HISTORY, "warmup_candles": WARMUP,
        },
        "universe_count": universe_count, "stocks_tested": len(price_frames),
        "failures": failures[:50],
        "signals_not_entered": dict(skipped),
        "all_signals": summarise(all_trades),
        "by_score": bucket_stats(all_trades, "score",
                                 [(75, 85, "75-84"), (85, 100, "85-99"), (100, 101, "100")]),
        "by_rsi": bucket_stats(all_trades, "rsi",
                               [(0, 60, "below 60"), (60, 70, "60-70"), (70, 101, "above 70")]),
        "by_year": {y: summarise(v) for y, v in sorted(years.items())},
        "portfolio": portfolio(all_trades),
        "limitations": [
            "Universe is today's Nifty 500 list: stocks that left the index are missing (survivorship bias), so results are likely somewhat optimistic.",
            "Daily candles only: if stop and target are both inside one day's range, the stop is assumed (conservative).",
            "Costs are an estimate; real slippage on gaps can be larger.",
            "News filter used in the morning report is not part of this test.",
            "Past results do not guarantee future results.",
        ],
        "recent_trades": all_trades[-40:],
    }


def main():
    import requests  # noqa: F401  (yfinance dependency check)
    import yfinance as yf
    from chart_data import validate_prices

    universe = pd.read_csv(CONSTITUENTS)
    symbols = list(dict.fromkeys(universe["Symbol"].dropna().astype(str).str.strip()))
    frames, failures = {}, []
    for n, sym in enumerate(symbols, 1):
        try:
            raw = yf.download(sym + ".NS", period=HISTORY, interval="1d", auto_adjust=True,
                              progress=False, threads=False, timeout=20)
            df, _ = validate_prices(raw)
            frames[sym] = indicator_frame(df)
        except Exception as exc:
            failures.append({"symbol": sym, "reason": str(exc)[:120]})
        if n % 50 == 0:
            print(f"Loaded {n}/{len(symbols)}; ok={len(frames)} failed={len(failures)}", flush=True)
    if len(frames) < 400:
        raise RuntimeError(f"Only {len(frames)} stocks loaded; not writing results")
    result = run(frames, len(symbols), failures)
    OUTPUT.write_text(json.dumps(result, indent=1, allow_nan=False), encoding="utf-8")
    a, p = result["all_signals"], result["portfolio"]
    print("ALL SIGNALS:", json.dumps(a))
    print("BY SCORE:", json.dumps(result["by_score"]))
    print("PORTFOLIO:", json.dumps({k: v for k, v in p.items() if k != "equity_by_month_rs"}))


if __name__ == "__main__":
    sys.exit(main())
