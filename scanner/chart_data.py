
"""NSE daily charts: validated historical data and technical indicators.
Research and paper trading only.
"""

import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf

# Always charted. A failure here fails the run.
CORE_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
]
SYMBOLS = CORE_SYMBOLS  # kept for compatibility

# Scanner candidates and the top of the watchlist are charted too, so any
# stock in the morning report can be opened on the charts page. A failure
# here only skips that stock.
RESULTS = Path("scanner/results.json")
MAX_WATCH_CHARTS = 10

OUTPUT = Path("charts/data")
INDEX = OUTPUT / "index.json"
IST = ZoneInfo("Asia/Kolkata")
MIN_CANDLES = 220

# NSE closes at 15:30 IST. After this time the day's candle is
# treated as complete.
SESSION_COMPLETE_IST = time(16, 0)

# If the latest candle is older than the expected session by more
# than this many calendar days, the data is treated as stale.
# (Allows for a holiday next to a weekend.)
MAX_STALE_DAYS = 4


def last_completed_session(now_ist):
    """Latest weekday whose session should be complete by now_ist.

    NSE holidays are not known here, so on a holiday this date is
    later than the real last session. That is reported, not failed.
    """
    day = now_ist.date()
    if now_ist.time() < SESSION_COMPLETE_IST:
        day -= timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def clean(value):
    try:
        value = float(value)
        if not np.isfinite(value):
            return None
        return round(value, 4)
    except (ValueError, TypeError):
        return None


def validate_prices(raw, now_ist=None):
    """Reject invalid rows, placeholder rows and incomplete sessions."""
    if now_ist is None:
        now_ist = datetime.now(IST)

    if raw.empty:
        raise ValueError("No market data returned")

    df = raw.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    df = df[required].copy()

    # Convert timestamps to NSE local calendar dates.
    index = pd.DatetimeIndex(df.index)
    if index.tz is not None:
        index = index.tz_convert(IST)
    else:
        # Yahoo daily bars generally use exchange-local dates.
        index = index.tz_localize(IST)

    df.index = pd.DatetimeIndex(index.date)
    df = df.sort_index()

    original_count = len(df)

    # Keep the latest row when a date appears more than once.
    duplicate_count = int(df.index.duplicated(keep="last").sum())
    df = df[~df.index.duplicated(keep="last")].copy()

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Use a session only once it is complete: today's candle is
    # kept after SESSION_COMPLETE_IST, never earlier.
    expected_session = last_completed_session(now_ist)
    incomplete = df.index.date > expected_session
    incomplete_dates = [
        d.strftime("%Y-%m-%d") for d in df.index[incomplete]
    ]
    df = df[~incomplete].copy()

    finite = np.isfinite(df[required].to_numpy()).all(axis=1)

    # Yahoo fills holidays and missing sessions with a flat candle
    # (open = high = low = close) and zero volume. Not a real session.
    placeholder = (
        (df["Volume"] == 0)
        & (df["Open"] == df["High"])
        & (df["High"] == df["Low"])
        & (df["Low"] == df["Close"])
    )
    placeholder_dates = [
        d.strftime("%Y-%m-%d") for d in df.index[placeholder]
    ]
    df = df[~placeholder].copy()
    finite = finite[~placeholder.to_numpy()]

    valid = (
        finite
        & (df["Open"] > 0)
        & (df["High"] > 0)
        & (df["Low"] > 0)
        & (df["Close"] > 0)
        & (df["Volume"] >= 0)
        & (df["High"] >= df["Low"])
        & (df["High"] >= df[["Open", "Close"]].max(axis=1))
        & (df["Low"] <= df[["Open", "Close"]].min(axis=1))
    )

    invalid_dates = [
        d.strftime("%Y-%m-%d") for d in df.index[~valid]
    ]
    df = df.loc[valid].copy()

    if len(df) < MIN_CANDLES:
        raise ValueError(
            f"Only {len(df)} valid completed candles; "
            f"minimum required: {MIN_CANDLES}"
        )

    if not df.index.is_monotonic_increasing:
        raise ValueError("Dates are not sorted")

    if df.index.has_duplicates:
        raise ValueError("Duplicate dates remain")

    latest = df.index[-1].date()
    lag_days = (expected_session - latest).days

    if lag_days > MAX_STALE_DAYS:
        raise ValueError(
            f"Stale data: latest candle {latest}, "
            f"expected session {expected_session}"
        )

    quality = {
        "downloaded_rows": original_count,
        "duplicate_dates_removed": duplicate_count,
        "incomplete_session_rows_removed": len(incomplete_dates),
        "incomplete_session_dates": incomplete_dates,
        "placeholder_rows_removed": len(placeholder_dates),
        "placeholder_dates": placeholder_dates,
        "invalid_price_rows_removed": len(invalid_dates),
        "invalid_price_dates": invalid_dates,
        "valid_completed_candles": len(df),
        "latest_completed_candle": latest.strftime("%Y-%m-%d"),
        "expected_session": expected_session.strftime("%Y-%m-%d"),
        "latest_matches_expected": lag_days == 0,
        "policy": (
            "Include a day's candle only after 16:00 IST; "
            "remove zero-volume flat placeholder candles; "
            "validate daily OHLC and volume; "
            f"fail if more than {MAX_STALE_DAYS} days behind"
        ),
    }

    return df, quality


def calculate_indicators(df):
    """Calculate technical indicators from validated candles."""
    df = df.copy()

    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    volume = df["Volume"]

    # Exponential moving averages.
    for n in (20, 50, 200):
        df[f"ema{n}"] = close.ewm(
            span=n, adjust=False
        ).mean()

    # RSI (14), using Wilder-style smoothing.
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)

    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain > 0), 100
    )
    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain == 0), 50
    )
    df["rsi14"] = rsi

    # MACD (12, 26, 9).
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(
        span=9, adjust=False
    ).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # True range.
    previous_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - previous_close).abs(),
        (low - previous_close).abs()
    ], axis=1).max(axis=1)

    # ADX (14).
    up = high.diff()
    down = -low.diff()

    plus_dm = pd.Series(
        np.where(
            (up > down) & (up > 0), up, 0.0
        ),
        index=df.index
    )

    minus_dm = pd.Series(
        np.where(
            (down > up) & (down > 0), down, 0.0
        ),
        index=df.index
    )

    atr14 = tr.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    atr_safe = atr14.replace(0, np.nan)

    plus_di = (
        100 * plus_dm.ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14
        ).mean() / atr_safe
    )

    minus_di = (
        100 * minus_dm.ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14
        ).mean() / atr_safe
    )

    dx = (
        100 * (plus_di - minus_di).abs()
        / (plus_di + minus_di).replace(0, np.nan)
    )

    df["adx14"] = dx.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    df["plus_di"] = plus_di
    df["minus_di"] = minus_di

    # Supertrend (10, 3).
    atr10 = tr.ewm(
        alpha=1 / 10,
        adjust=False,
        min_periods=10
    ).mean()

    midpoint = (high + low) / 2
    upper = midpoint + 3 * atr10
    lower = midpoint - 3 * atr10

    final_upper = upper.to_numpy(copy=True)
    final_lower = lower.to_numpy(copy=True)

    closing = close.to_numpy()
    direction = np.ones(len(df), dtype=int)
    supertrend = np.full(len(df), np.nan)

    for i in range(1, len(df)):
        if not np.isfinite(atr10.iloc[i]):
            continue

        if not np.isfinite(final_upper[i - 1]):
            final_upper[i - 1] = upper.iloc[i - 1]
        if not np.isfinite(final_lower[i - 1]):
            final_lower[i - 1] = lower.iloc[i - 1]

        if (
            upper.iloc[i] < final_upper[i - 1]
            or closing[i - 1] > final_upper[i - 1]
        ):
            final_upper[i] = upper.iloc[i]
        else:
            final_upper[i] = final_upper[i - 1]

        if (
            lower.iloc[i] > final_lower[i - 1]
            or closing[i - 1] < final_lower[i - 1]
        ):
            final_lower[i] = lower.iloc[i]
        else:
            final_lower[i] = final_lower[i - 1]

        if closing[i] > final_upper[i - 1]:
            direction[i] = 1
        elif closing[i] < final_lower[i - 1]:
            direction[i] = -1
        else:
            direction[i] = direction[i - 1]

        supertrend[i] = (
            final_lower[i]
            if direction[i] == 1
            else final_upper[i]
        )

    df["supertrend"] = supertrend
    df["supertrend_direction"] = direction

    # On-Balance Volume.
    price_direction = np.sign(
        close.diff().fillna(0)
    )
    df["obv"] = (price_direction * volume).cumsum()

    return df


def generate(symbol):
    print(f"Downloading {symbol}...")

    raw = yf.download(
        symbol + ".NS",
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=20
    )

    df, quality = validate_prices(raw)
    df = calculate_indicators(df)

    candles = []

    fields = [
        "open", "high", "low", "close", "volume",
        "ema20", "ema50", "ema200", "rsi14",
        "macd", "macd_signal", "macd_hist",
        "adx14", "plus_di", "minus_di",
        "supertrend", "obv"
    ]

    source_names = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }

    for date, row in df.iterrows():
        candle = {
            "time": date.strftime("%Y-%m-%d")
        }

        for field in fields:
            source = source_names.get(field, field)
            candle[field] = clean(row[source])

        candle["supertrend_direction"] = int(
            row["supertrend_direction"]
        )

        candles.append(candle)

    # Confirm latest candle has valid indicators.
    latest = candles[-1]

    essential = [
        "ema20", "ema50", "ema200",
        "rsi14", "macd", "macd_signal",
        "adx14", "plus_di", "minus_di",
        "supertrend", "obv"
    ]

    unavailable = [
        key for key in essential
        if latest[key] is None
    ]

    if unavailable:
        raise ValueError(
            "Latest indicators unavailable: "
            + ", ".join(unavailable)
        )

    result = {
        "symbol": symbol,
        "exchange": "NSE",
        "interval": "1d",
        "generated_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "provider": "Yahoo Finance via yfinance",
        "adjusted": True,
        "data_quality": quality,
        "disclaimer": (
            "Historical adjusted data, not live prices. "
            "For research and paper trading only."
        ),
        "candles": candles
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)

    path = OUTPUT / f"{symbol}.json"

    path.write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False),
        encoding="utf-8"
    )

    print(
        f"SUCCESS {symbol}: {len(candles)} candles | "
        f"latest={latest['time']} | "
        f"expected={quality['expected_session']} | "
        f"placeholders_removed="
        f"{quality['placeholder_dates']} | "
        f"invalid_removed={quality['invalid_price_dates']}"
    )

    return latest["time"]


def scanner_symbols():
    """(symbol, group) for scanner candidates and top watchlist stocks."""
    try:
        report = json.loads(RESULTS.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Scanner results unavailable, charting core only: {exc}")
        return []
    picks = [(x["symbol"], "candidate") for x in report.get("candidates", [])]
    picks += [(x["symbol"], "watch")
              for x in report.get("watchlist", [])[:MAX_WATCH_CHARTS]]
    seen, out = set(CORE_SYMBOLS), []
    for sym, group in picks:
        if sym not in seen:
            seen.add(sym)
            out.append((sym, group))
    return out


def main():
    failures = []
    latest_dates = {}

    for symbol in CORE_SYMBOLS:
        try:
            latest_dates[symbol] = generate(symbol)
        except Exception as exc:
            print(f"ERROR {symbol}: {exc}")
            failures.append(symbol)

    if failures:
        raise RuntimeError(
            "Failed symbols: " + ", ".join(failures)
        )

    # Every core symbol should end on the same session. A mismatch means
    # one download is behind; fail so nothing is committed.
    if len(set(latest_dates.values())) > 1:
        raise RuntimeError(
            "Latest candle differs between symbols: "
            + ", ".join(f"{s}={d}" for s, d in latest_dates.items())
        )
    session = next(iter(latest_dates.values()))

    index = [{"symbol": s, "group": "core", "latest": session}
             for s in CORE_SYMBOLS]
    skipped = []
    for symbol, group in scanner_symbols():
        try:
            latest = generate(symbol)
            if latest != session:
                raise ValueError(f"latest candle {latest}, expected {session}")
            index.append({"symbol": symbol, "group": group, "latest": latest})
        except Exception as exc:
            print(f"SKIP {symbol}: {exc}")
            skipped.append({"symbol": symbol, "reason": str(exc)[:120]})
            (OUTPUT / f"{symbol}.json").unlink(missing_ok=True)

    # Remove charts for stocks that have left the candidate/watch lists.
    keep = {x["symbol"] for x in index}
    for path in OUTPUT.glob("*.json"):
        if path.name != INDEX.name and path.stem not in keep:
            path.unlink()
            print(f"Removed old chart {path.name}")

    INDEX.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "latest_session": session,
        "symbols": index,
        "skipped": skipped,
    }, indent=1), encoding="utf-8")

    print(
        f"Charts generated: {len(index)} "
        f"(core {len(CORE_SYMBOLS)}, scanner {len(index) - len(CORE_SYMBOLS)}, "
        f"skipped {len(skipped)}). Latest session: {session}"
    )


if __name__ == "__main__":
    main()
    
