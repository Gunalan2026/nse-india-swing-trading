
"""Generate daily NSE candlestick data for paper trading."""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

SYMBOLS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
OUTPUT = Path("charts/data")


def clean(value):
    if pd.isna(value) or not np.isfinite(float(value)):
        return None
    return round(float(value), 4)


def generate(symbol):
    df = yf.download(
        symbol + ".NS",
        period="1y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=20
    )

    if df.empty or len(df) < 60:
        raise ValueError("Insufficient price history")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.sort_index().dropna(
        subset=["Open", "High", "Low", "Close"]
    )

    close = df["Close"].astype(float)
    volume = df["Volume"].fillna(0).astype(float)

    for length in [20, 50, 200]:
        df[f"ema{length}"] = close.ewm(
            span=length, adjust=False
        ).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(
        alpha=1 / 14, adjust=False
    ).mean()
    loss = (-delta.clip(upper=0)).ewm(
        alpha=1 / 14, adjust=False
    ).mean()

    rs = gain / loss.replace(0, np.nan)
    df["rsi14"] = 100 - 100 / (1 + rs)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    df["macd"] = macd
    df["macd_signal"] = signal
    df["macd_hist"] = macd - signal

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
            "macd_hist": clean(row["macd_hist"])
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

    file = OUTPUT / f"{symbol}.json"
    file.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

    print(f"{symbol}: saved {len(candles)} candles")


def main():
    failures = []

    for symbol in SYMBOLS:
        try:
            generate(symbol)
        except Exception as exc:
            failures.append(f"{symbol}: {exc}")
            print(f"ERROR: {symbol}: {exc}")

    if failures:
        raise RuntimeError(
            "Chart generation failed: " + "; ".join(failures)
        )


if __name__ == "__main__":
    main()
  
