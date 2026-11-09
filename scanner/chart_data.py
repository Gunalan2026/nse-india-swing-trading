
"""NSE daily chart data and technical indicators."""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

SYMBOLS = [
    "RELIANCE", "TCS", "INFY",
    "HDFCBANK", "ICICIBANK"
]
OUTPUT = Path("charts/data")


def clean(value):
    if pd.isna(value) or not np.isfinite(float(value)):
        return None
    return round(float(value), 4)


def generate(symbol):
    df = yf.download(
        symbol + ".NS",
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=20
    )

    if df.empty or len(df) < 220:
        raise ValueError("Insufficient price history")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.sort_index().dropna(
        subset=["Open", "High", "Low", "Close"]
    )

    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    close = df["Close"].astype(float)
    volume = df["Volume"].fillna(0).astype(float)

    # EMA
    for n in [20, 50, 200]:
        df[f"ema{n}"] = close.ewm(
            span=n, adjust=False
        ).mean()

    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(
        alpha=1 / 14, adjust=False
    ).mean()
    loss = (-delta.clip(upper=0)).ewm(
        alpha=1 / 14, adjust=False
    ).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi14"] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(
        span=9, adjust=False
    ).mean()
    df["macd_hist"] = (
        df["macd"] - df["macd_signal"]
    )

    # True Range and ATR
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()

    # ADX (14)
    up = high.diff()
    down = -low.diff()

    plus_dm = pd.Series(
        np.where(
            (up > down) & (up > 0), up, 0.0
        ), index=df.index
    )
    minus_dm = pd.Series(
        np.where(
            (down > up) & (down > 0), down, 0.0
        ), index=df.index
    )

    atr_safe = atr.replace(0, np.nan)
    plus_di = 100 * plus_dm.ewm(
        alpha=1 / 14, adjust=False
    ).mean() / atr_safe
    minus_di = 100 * minus_dm.ewm(
        alpha=1 / 14, adjust=False
    ).mean() / atr_safe

    dx = 100 * (
        (plus_di - minus_di).abs() /
        (plus_di + minus_di).replace(0, np.nan)
    )

    df["adx14"] = dx.ewm(
        alpha=1 / 14, adjust=False
    ).mean()
    df["plus_di"] = plus_di
    df["minus_di"] = minus_di

    # Supertrend (10, 3)
    atr10 = tr.ewm(
        alpha=1 / 10, adjust=False
    ).mean()

    midpoint = (high + low) / 2
    upper = midpoint + 3 * atr10
    lower = midpoint - 3 * atr10

    final_upper = upper.copy()
    final_lower = lower.copy()
    direction = np.ones(len(df), dtype=int)
    supertrend = np.full(len(df), np.nan)

    for i in range(1, len(df)):
        if (
            upper.iloc[i] < final_upper.iloc[i-1]
            or close.iloc[i-1] > final_upper.iloc[i-1]
        ):
            final_upper.iloc[i] = upper.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i-1]

        if (
            lower.iloc[i] > final_lower.iloc[i-1]
            or close.iloc[i-1] < final_lower.iloc[i-1]
        ):
            final_lower.iloc[i] = lower.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i-1]

        if close.iloc[i] > final_upper.iloc[i-1]:
            direction[i] = 1
        elif close.iloc[i] < final_lower.iloc[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]

        supertrend[i] = (
            final_lower.iloc[i]
            if direction[i] == 1
            else final_upper.iloc[i]
        )

    df["supertrend"] = supertrend
    df["supertrend_direction"] = direction

    # On-Balance Volume (OBV)
    price_direction = np.sign(
        close.diff().fillna(0)
    )
    df["obv"] = (
        price_direction * volume
    ).cumsum()

    candles = []
    for date, row in df.iterrows():
        candles.append({
            "time": date.strftime("%Y-%m-%d"),
            "open": clean(row["Open"]),
            "high": clean(row["High"]),
            "low": clean(row["Low"]),
            "close": clean(row["Close"]),
            "volume": clean(row["Volume"]),
            "ema20": clean(row["ema20"]),
            "ema50": clean(row["ema50"]),
            "ema200": clean(row["ema200"]),
            "rsi14": clean(row["rsi14"]),
            "macd": clean(row["macd"]),
            "macd_signal": clean(row["macd_signal"]),
            "macd_hist": clean(row["macd_hist"]),
            "adx14": clean(row["adx14"]),
            "plus_di": clean(row["plus_di"]),
            "minus_di": clean(row["minus_di"]),
            "supertrend": clean(row["supertrend"]),
            "supertrend_direction": int(
                row["supertrend_direction"]
            ),
            "obv": clean(row["obv"])
        })

    result = {
        "symbol": symbol,
        "exchange": "NSE",
        "interval": "1d",
        "generated_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "provider": "Yahoo Finance via yfinance",
        "adjusted": True,
        "candles": candles
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / f"{symbol}.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )
    print(f"{symbol}: {len(candles)} candles saved")


def main():
    failures = []
    for symbol in SYMBOLS:
        try:
            generate(symbol)
        except Exception as exc:
            print(f"ERROR {symbol}: {exc}")
            failures.append(symbol)

    if failures:
        raise RuntimeError(
            "Failed symbols: " + ", ".join(failures)
        )


if __name__ == "__main__":
    main()
