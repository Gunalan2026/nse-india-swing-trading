import json
import math
from pathlib import Path
from datetime import datetime, timezone, date

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'financial_results.json'
OUTPUT = BASE / 'financial_analysis.json'

METRICS = {
    'revenue': ['Total Revenue', 'Operating Revenue'],
    'net_profit': ['Net Income', 'Net Income Common Stockholders'],
    'debt': ['Total Debt'],
    'equity': ['Stockholders Equity', 'Common Stock Equity'],
    'assets': ['Total Assets'],
    'operating_cash_flow': ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'],
    'free_cash_flow': ['Free Cash Flow'],
}

# Conservative manual sector list for the initial five-stock pilot.
# Unknown companies are NOT automatically treated as non-financial.
SECTOR_OVERRIDES = {'HDFCBANK': 'bank', 'ICICIBANK': 'bank', 'RELIANCE': 'diversified', 'TCS': 'non_financial', 'INFY': 'non_financial'}

def get_periods(company, section):
    data = company.get(section, {})
    periods = data.get('periods', []) if isinstance(data, dict) else []
    if not isinstance(periods, list):
        return []
    return sorted([p for p in periods if isinstance(p, dict)], key=lambda p: str(p.get('period_end') or ''), reverse=True)

def metric(period, names):
    values = period.get('values', {}) if isinstance(period, dict) else {}
    if not isinstance(values, dict):
        return None
    for name in names:
        v = values.get(name)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
            return float(v)
    return None

def growth(current, previous):
    if current is None or previous is None or previous <= 0:
        return None
    return round((current - previous) / previous * 100, 2)

def financial_score(metrics, sector):
    # A transparent, provisional quality checklist, NOT a predictive probability.
    # Scores are withheld for banks, diversified companies and unclassified sectors.
    if sector != 'non_financial':
        return None, 0, 'Sector-specific scoring not yet validated'
    rules = [
        ('revenue_growth_pct', 20, lambda v: v > 0),
        ('profit_growth_pct', 20, lambda v: v > 0),
        ('net_profit', 15, lambda v: v > 0),
        ('return_on_equity_pct', 15, lambda v: v >= 12),
        ('operating_cash_flow', 15, lambda v: v > 0),
        ('free_cash_flow', 10, lambda v: v > 0),
        ('debt_to_equity', 5, lambda v: v <= 1),
    ]
    available = [(key, weight, test) for key, weight, test in rules if metrics.get(key) is not None]
    coverage = sum(weight for _, weight, _ in available)
    if coverage < 80:
        return None, coverage, 'Insufficient metric coverage'
    points = sum(weight for key, weight, test in available if test(metrics[key]))
    return round(points / coverage * 100), coverage, 'Provisional non-financial checklist; unvalidated'

def analyze(company):
    income = get_periods(company, 'annual_income_statement')
    balance = get_periods(company, 'annual_balance_sheet')
    cash = get_periods(company, 'annual_cash_flow')
    li = income[0] if income else {}
    pi = income[1] if len(income) > 1 else {}
    lb = balance[0] if balance else {}
    lc = cash[0] if cash else {}
    revenue = metric(li, METRICS['revenue'])
    old_revenue = metric(pi, METRICS['revenue'])
    profit = metric(li, METRICS['net_profit'])
    old_profit = metric(pi, METRICS['net_profit'])
    debt = metric(lb, METRICS['debt'])
    equity = metric(lb, METRICS['equity'])
    assets = metric(lb, METRICS['assets'])
    ocf = metric(lc, METRICS['operating_cash_flow'])
    fcf = metric(lc, METRICS['free_cash_flow'])
    de = round(debt / equity, 2) if debt is not None and equity is not None and equity > 0 else None
    roe = round(profit / equity * 100, 2) if profit is not None and equity is not None and equity > 0 else None
    metrics = {
        'revenue': revenue, 'net_profit': profit, 'total_debt': debt, 'equity': equity,
        'total_assets': assets, 'operating_cash_flow': ocf, 'free_cash_flow': fcf,
        'revenue_growth_pct': growth(revenue, old_revenue),
        'profit_growth_pct': growth(profit, old_profit),
        'debt_to_equity': de, 'return_on_equity_pct': roe,
    }
    symbol = str(company.get('symbol') or 'UNKNOWN').upper()
    sector = SECTOR_OVERRIDES.get(symbol, 'unclassified')
    positives, negatives, cautions = [], [], []
    for key, label in [('revenue_growth_pct', 'Annual revenue'), ('profit_growth_pct', 'Annual net profit')]:
        v = metrics[key]
        if v is not None:
            (positives if v > 0 else negatives if v < 0 else cautions).append(label + (' increased' if v > 0 else ' declined' if v < 0 else ' unchanged'))
    for key, label in [('net_profit', 'Latest annual net profit'), ('operating_cash_flow', 'Operating cash flow'), ('free_cash_flow', 'Free cash flow')]:
        v = metrics[key]
        if v is not None:
            (positives if v > 0 else negatives if v < 0 else cautions).append(label + (' is positive' if v > 0 else ' is negative' if v < 0 else ' is zero'))
    if de is not None and de > 2 and sector == 'non_financial':
        cautions.append('High debt-to-equity ratio; review industry context')
    if not income or not balance or not cash:
        cautions.append('One or more financial statements unavailable')
    if len(income) < 2:
        cautions.append('Insufficient annual income history for growth comparison')
    periods = {'income': li.get('period_end'), 'balance_sheet': lb.get('period_end'), 'cash_flow': lc.get('period_end')}
    ages = []
    for value in periods.values():
        try:
            ages.append((datetime.now(timezone.utc).date() - date.fromisoformat(str(value)[:10])).days)
        except (ValueError, TypeError):
            pass
    if len(ages) < 3:
        cautions.append('One or more financial statement dates unavailable')
    if ages and max(ages) > 550:
        cautions.append('At least one financial statement is older than 550 days')
    score, coverage, explanation = financial_score(metrics, sector)
    if score is None:
        cautions.append(explanation)
    return {
        'symbol': symbol, 'financial_periods': periods, 'metrics': metrics,
        'positive_indicators': positives, 'negative_indicators': negatives,
        'cautions': cautions, 'assessment': 'Research required',
        'fundamental_score': score, 'fundamental_score_coverage_pct': coverage,
        'sector_classification': sector, 'score_note': explanation,
        'note': 'Experimental financial indicators. Verify audited NSE/BSE filings. Not a buy/sell signal.'
    }

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f'Missing {INPUT}. Generate financial data first.')
    with INPUT.open('r', encoding='utf-8') as f:
        source = json.load(f)
    companies = source.get('companies', [])
    if not isinstance(companies, list) or not companies:
        raise ValueError('No companies found in financial_results.json')
    results = [analyze(c) for c in companies if isinstance(c, dict)]
    if not results:
        raise ValueError('No valid company records')
    output = {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'source_generated_utc': source.get('generated_utc'),
        'company_count': len(results),
        'methodology': 'Annual financial statement comparison; provisional sector-aware scoring',
        'disclaimer': 'Experimental analysis. Verify official NSE/BSE filings and audited statements. No profit guarantee or investment recommendation.',
        'companies': results,
    }
    with OUTPUT.open('w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, allow_nan=False)
    print(f'Financial analysis completed: {len(results)} companies')
    print(f'Saved: {OUTPUT}')

if __name__ == '__main__':
    main()
    
