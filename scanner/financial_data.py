
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

SYMBOLS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
]

OUTPUT = Path(__file__).parent / "financial_results.json"


def clean_value(value):
    if value is None or pd.isna(value):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return str(value)


def extract_statement(statement):
    if statement is None or statement.empty:
        return {"status": "unavailable", "periods": []}

    periods = []

    for date in statement.columns[:4]:
        values = {}
        for metric, value in statement[date].items():
            cleaned = clean_value(value)
            if cleaned is not None:
                values[str(metric)] = cleaned

        periods.append({
            "period_end": pd.Timestamp(date).strftime("%Y-%m-%d"),
            "values": values,
        })

    return {
        "status": "available" if periods else "unavailable",
        "periods": periods,
    }


def collect_company(symbol):
    ticker = yf.Ticker(f"{symbol}.NS")

    return {
        "symbol": symbol,
        "provider": "Yahoo Finance via yfinance",
        "annual_income_statement": extract_statement(
            ticker.income_stmt
        ),
        "quarterly_income_statement": extract_statement(
            ticker.quarterly_income_stmt
        ),
        "annual_balance_sheet": extract_statement(
            ticker.balance_sheet
        ),
        "quarterly_balance_sheet": extract_statement(
            ticker.quarterly_balance_sheet
        ),
        "annual_cash_flow": extract_statement(
            ticker.cashflow
        ),
        "quarterly_cash_flow": extract_statement(
            ticker.quarterly_cashflow
        ),
    }


def main():
    results = []
    errors = []

    for symbol in SYMBOLS:
        print(f"Collecting financial data: {symbol}", flush=True)

        try:
            company = collect_company(symbol)
            results.append(company)
            print(f"Completed: {symbol}", flush=True)
        except Exception as exc:
            errors.append({
                "symbol": symbol,
                "error": str(exc)[:300],
            })
            print(f"Failed: {symbol}: {exc}", flush=True)

    output = {
        "generated_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": "Yahoo Finance via yfinance",
        "purpose": "Financial data collection prototype",
        "disclaimer": (
            "Unofficial data. Not independently verified. "
            "Missing values are not zero. "
            "Do not use for investment decisions without "
            "checking official financial statements."
        ),
        "companies": results,
        "errors": errors,
    }

    OUTPUT.write_text(
        json.dumps(output, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    print(
        f"Saved {len(results)} companies to {OUTPUT}",
        flush=True,
    )


if __name__ == "__main__":
    main()
          
