"""Nifty 500 technical screening prototype. Research/paper trading only."""
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

CONSTITUENTS = 'https://niftyindices.com/IndexConstituent/ind_nifty500list.csv'
OUTPUT = Path('scanner/results.json')
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; educational-stock-screen/1.0)'}


def indicators(df):
    close = df['Close'].astype(float)
    high = df['High'].astype(float)
    low = df['Low'].astype(float)
    volume = df['Volume'].astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    prev_close = close.shift(1)
    true_range = pd.concat([(high-low), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1/14, adjust=False).mean()
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    vol20 = volume.shift(1).rolling(20).mean()
    prior_high20 = high.shift(1).rolling(20).max()
    last = df.index[-1]
    values = [close.loc[last], rsi.loc[last], atr.loc[last], sma20.loc[last], sma50.loc[last], vol20.loc[last], prior_high20.loc[last]]
    if not all(np.isfinite(x) for x in values) or vol20.loc[last] <= 0:
        return None
    price = float(close.loc[last])
    trend = bool(price > sma20.loc[last] > sma50.loc[last])
    breakout = bool(price > prior_high20.loc[last])
    volume_ratio = float(volume.loc[last] / vol20.loc[last])
    setup = trend and breakout and volume_ratio >= 1.5 and 50 <= rsi.loc[last] <= 75
    stop = price - 2 * float(atr.loc[last])
    return {'close': round(price, 2), 'rsi14': round(float(rsi.loc[last]), 1),
            'sma20': round(float(sma20.loc[last]), 2), 'sma50': round(float(sma50.loc[last]), 2),
            'atr14': round(float(atr.loc[last]), 2), 'volume_ratio': round(volume_ratio, 2),
            'breakout20': breakout, 'trend_up': trend, 'candidate': setup,
            'illustrative_stop': round(stop, 2) if stop > 0 else None}


def main():
    import yfinance as yf
    response = requests.get(CONSTITUENTS, headers=HEADERS, timeout=30)
    response.raise_for_status()
    universe = pd.read_csv(io.BytesIO(response.content))
    if 'Symbol' not in universe.columns or len(universe) < 400:
        raise RuntimeError('Nifty 500 constituent download is invalid or incomplete')
    symbols = universe['Symbol'].dropna().astype(str).str.strip().tolist()
    results, errors = [], []
    # Process individually to isolate failed symbols. Free provider can throttle.
    for symbol in symbols:
        try:
            frame = yf.download(symbol + '.NS', period='6mo', interval='1d', auto_adjust=True, progress=False, threads=False, timeout=15)
            if frame.empty or len(frame) < 60:
                raise ValueError('Insufficient price history')
            if isinstance(frame.columns, pd.MultiIndex):
                frame.columns = frame.columns.get_level_values(0)
            metrics = indicators(frame)
            if metrics is None:
                raise ValueError('Invalid indicator data')
            metrics['symbol'] = symbol
            metrics['as_of'] = str(frame.index[-1].date())
            results.append(metrics)
        except Exception as exc:
            errors.append({'symbol': symbol, 'reason': str(exc)[:120]})
    report = {'generated_utc': datetime.now(timezone.utc).isoformat(),
              'universe_count': len(symbols), 'analyzed_count': len(results),
              'failed_count': len(errors), 'provider': 'Yahoo Finance via yfinance (unofficial; delayed)',
              'disclaimer': 'Technical screening only. Not investment advice or live prices.',
              'candidates': sorted((x for x in results if x['candidate']), key=lambda x: x['volume_ratio'], reverse=True),
              'errors_sample': errors[:25]}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"Nifty 500 universe: {len(symbols)}; analyzed: {len(results)}; candidates: {len(report['candidates'])}; failed: {len(errors)}")
    if len(results) < 400:
        raise RuntimeError('Too few stocks analyzed. Check source availability and rate limits; no reliable scan produced.')


if __name__ == '__main__':
    main()
