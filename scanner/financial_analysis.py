
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
INPUT = BASE / "financial_data.json"
OUTPUT = BASE / "financial_analysis.json"

METRICS = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "net_profit": ["Net Income", "Net Income Common Stockholders"],
    "debt": ["Total Debt"],
    "equity": ["Stockholders Equity", "Common Stock Equity"],
    "assets": ["Total Assets"],
    "operating_cash_flow": [
        "Operating Cash Flow",
        "Cash Flow From Continuing Operating Activities"
    ],
    "free_cash_flow": ["Free Cash Flow"],
}

def get_periods(company, section):
    data = company.get(section, {})
    if not isinstance(data, dict):
        return []
    periods = data.get("periods", [])
    if not isinstance(periods, list):
        return []
    return sorted(
        [p for p in periods if isinstance(p, dict)],
        key=lambda p: p.get("period_end", ""),
        reverse=True
    )

def metric(period, names):
    values = period.get("values", {})
    if not isinstance(values, dict):
        return None
    for name in names:
        value = values.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None

def growth(current, previous):
    if current is None or previous is None or previous <= 0:
        return None
    return round((current - previous) / previous * 100, 2)

def round_or_none(value, digits=2):
    return round(value, digits) if value is not None else None

def analyze(company):
    income = get_periods(company, "annual_income_statement")
    balance = get_periods(company, "annual_balance_sheet")
    cash = get_periods(company, "annual_cash_flow")

    latest_income = income[0] if income else {}
    previous_income = income[1] if len(income) > 1 else {}
    latest_balance = balance[0] if balance else {}
    latest_cash = cash[0] if cash else {}

    revenue = metric(latest_income, METRICS["revenue"])
    old_revenue = metric(previous_income, METRICS["revenue"])
    profit = metric(latest_income, METRICS["net_profit"])
    old_profit = metric(previous_income, METRICS["net_profit"])
    debt = metric(latest_balance, METRICS["debt"])
    equity = metric(latest_balance, METRICS["equity"])
    assets = metric(latest_balance, METRICS["assets"])
    ocf = metric(latest_cash, METRICS["operating_cash_flow"])
    fcf = metric(latest_cash, METRICS["free_cash_flow"])

    revenue_growth = growth(revenue, old_revenue)
    profit_growth = growth(profit, old_profit)

    debt_to_equity = (
        round(debt / equity, 2)
        if debt is not None and equity is not None and equity > 0
        else None
    )

    roe = (
        round(profit / equity * 100, 2)
        if profit is not None and equity is not None and equity > 0
        else None
    )

    positives = []
    negatives = []
    cautions = []

    if revenue_growth is not None:
        if revenue_growth > 0:
            positives.append("Annual revenue increased")
        elif revenue_growth < 0:
            negatives.append("Annual revenue declined")

    if profit_growth is not None:
        if profit_growth > 0:
            positives.append("Annual net profit increased")
        elif profit_growth < 0:
            negatives.append("Annual net profit declined")

    if profit is not None:
        if profit > 0:
            positives.append("Latest annual net profit is positive")
        elif profit < 0:
            negatives.append("Latest annual net profit is negative")

    if ocf is not None:
        if ocf > 0:
            positives.append("Operating cash flow is positive")
        elif ocf < 0:
            negatives.append("Operating cash flow is negative")

    if fcf is not None:
        if fcf > 0:
            positives.append("Free cash flow is positive")
        elif fcf < 0:
            negatives.append("Free cash flow is negative")

    if debt_to_equity is not None:
        if debt_to_equity > 2:
            cautions.append("High debt-to-equity ratio; review sector context")

    if not income or not balance or not cash:
        cautions.append("One or more financial statements are unavailable")

    if len(income) < 2:
        cautions.append("Insufficient annual income history for growth comparison")

    return {
        "symbol": company.get("symbol", "UNKNOWN"),
        "financial_periods": {
            "income": latest_income.get("period_end"),
            "balance_sheet": latest_balance.get("period_end"),
            "cash_flow": latest_cash.get("period_end")
        },
        "metrics": {
            "revenue": revenue,
            "net_profit": profit,
            "total_debt": debt,
            "equity": equity,
            "total_assets": assets,
            "operating_cash_flow": ocf,
            "free_cash_flow": fcf,
            "revenue_growth_pct": revenue_growth,
            "profit_growth_pct": profit_growth,
            "debt_to_equity": debt_to_equity,
            "return_on_equity_pct": roe
        },
        "positive_indicators": positives,
        "negative_indicators": negatives,
        "cautions": cautions,
        "assessment": "Research required",
        "note": (
            "Descriptive financial indicators only. "
            "Not a buy/sell signal. Ratios may require "
            "sector-specific interpretation."
        )
    }

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing {INPUT}. Generate financial data first."
        )

    with INPUT.open("r", encoding="utf-8") as f:
        source = json.load(f)

    companies = source.get("companies", [])
    if not isinstance(companies, list) or not companies:
        raise ValueError("No companies found in financial_data.json")

    results = [analyze(c) for c in companies if isinstance(c, dict)]

    output = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_generated_utc": source.get("generated_utc"),
        "company_count": len(results),
        "methodology": "Annual financial statement comparison",
        "disclaimer": (
            "Experimental financial analysis. Verify against "
            "official NSE/BSE filings and audited statements. "
            "No profit guarantee or investment recommendation."
        ),
        "companies": results
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, allow_nan=False)

    print(f"Financial analysis completed: {len(results)} companies")
    print(f"Saved: {OUTPUT}")

if __name__ == "__main__":
    main()
  
