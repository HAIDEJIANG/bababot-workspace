# -*- coding: utf-8 -*-
import numpy_financial as npf
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ESN888272 Rent Income (USD)
cash_flows = {
    2026: {'months': 9, 'monthly': 193816.67, 'annual': 1744350},
    2027: {'months': 12, 'monthly': 199037.38, 'annual': 2388448.6},
    2028: {'months': 12, 'monthly': 204592.72, 'annual': 2455112.65},
    2029: {'months': 12, 'monthly': 210507.48, 'annual': 2526089.82},
}

total = sum([v['annual'] for v in cash_flows.values()])

print('=' * 65)
print('ESN888272 RENT INCOME SUMMARY (USD)')
print('=' * 65)
for y, d in cash_flows.items():
    print(f"{y}: ${d['monthly']:,.0f}/mo x {d['months']}mo = ${d['annual']:,.0f}")
print('-' * 65)
print(f"4-Year Total: ${total:,.0f}")
rmb = total * 7.2
print(f"RMB Equivalent: {rmb:,.0f} @ 7.2 rate")
print()

# IRR Calculation
print('=' * 65)
print('IRR CALCULATION (by purchase price)')
print('=' * 65)
print(f"{'Purchase Price':^18} | {'IRR':^10} | {'Net Profit':^18}")
print('-' * 65)

for price in [3000000, 3500000, 4000000, 4500000, 5000000]:
    cf = [-price]
    for y in sorted(cash_flows.keys()):
        cf.append(cash_flows[y]['annual'])
    
    irr = npf.irr(cf) * 100
    profit = sum(cf)
    print(f"${price:>14,} | {irr:>8.2f}% | ${profit:>14,.0f}")

print()
print('Note: IRR excludes residual value (est. $1-2M)')

# With residual value
print()
print('=' * 65)
print('IRR WITH RESIDUAL VALUE ($1.5M end of 2029)')
print('=' * 65)
print(f"{'Purchase Price':^18} | {'IRR':^10} | {'Net Profit':^18}")
print('-' * 65)

residual = 1500000
for price in [3000000, 3500000, 4000000, 4500000, 5000000]:
    cf = [-price]
    for y in sorted(cash_flows.keys()):
        val = cash_flows[y]['annual']
        if y == 2029:
            val += residual  # Add residual at end
        cf.append(val)
    
    irr = npf.irr(cf) * 100
    profit = sum(cf)
    print(f"${price:>14,} | {irr:>8.2f}% | ${profit:>14,.0f}")