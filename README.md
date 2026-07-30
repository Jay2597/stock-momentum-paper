# stock-momentum-paper — 12-1 momentum on the F&O universe (forward paper test)

Forward (paper) test of cross-sectional **12-1 momentum**: each month, rank the ~208-stock
NSE F&O universe on 12-month return **skipping the most recent month**, hold the **top 20
equal-weight**, rebalance monthly. Chosen 2026-07-30 after a factor bake-off on 2018-2026
daily data (momentum 3/6/9/12m, low-vol, mom+low-vol, sector rotation, VIX gates).

## Why this spec
- **Robust plateau, not a lucky cell**: net Sharpe 1.4-1.6 across lookbacks 9-12m and top-N
  10-30. 12-1 with skip-month is the literature standard and sat mid-plateau.
- **VIX gate rejected** (unlike the index vol-selling system): every gate tested (17/20/25)
  *lowered* Sharpe 1.55 -> 1.1-1.25. Momentum here wants to stay invested.
- **Sector rotation, low-vol, and combos all underperformed** plain stock momentum.

## Honest numbers (2019-01..2026-06, net of 0.25%/side on ~40%/mo one-way turnover)
| | CAGR | Sharpe | maxDD |
|---|---|---|---|
| NIFTY (cap-weight) | 11.1% | 0.70 | -29% |
| EW universe (beta benchmark) | 28.2% | 1.31 | -31% |
| **MOM 12-1 top20** | **42.4%** | **1.55** | **-33%** |
| MOM 12-1, pre-2019-listed only | 38.4% | 1.46 | -33% |

**True momentum alpha over the EW universe: ~+9-13%/yr** (survives the pre-2019-listing
survivorship control). Much of the headline CAGR is equal-weight midcap beta from a strong
period — do NOT extrapolate 42%. Realistic forward expectation: **15-25% CAGR, maxDD to -35%**.

## Known biases (why this forward test exists)
- **Survivorship**: universe = today's F&O list; delisted losers absent from the backtest.
  The EW-relative alpha is the cleaner claim; this paper test is the real referee.
- **Momentum crashes**: worst month **-29% (Feb 2020)**; longest underwater stretch 8 months.
  Position sizing must survive that without abandoning the system.
- Dividends captured in stock returns but not in the NIFTY price-index benchmark (~+1.3%/yr
  flattering); costs modeled at 0.25%/side which assumes liquid F&O-name spreads.

## Files
- `pick.py` — monthly rebalance: closes the open cycle into `results/history.csv`, writes the
  new top-20 to `results/portfolio.csv`. Run locally near month-end.
- `mark.py` — marks the open portfolio vs NIFTY into `results/nav.csv`; runs Mon/Wed/Fri via
  GitHub Actions (`.github/workflows/mark.yml`), no broker needed.
- `universe.json` — the F&O stock universe + sector map (from NSE fo_mktlots, 2026-07-30).

## Protocol
Paper-only for **>= 3 monthly cycles**, then review: NAV vs NIFTY and vs the EW universe,
realized turnover, and whether picks were actually fillable. Not investment advice.

> Related: [nifty-condor-paper](https://github.com/Jay2597/nifty-condor-paper) — the
> VIX-gated index vol-selling system this research process came from. Same-period analysis
> showed single-stock *options* selling has no edge (realized/implied ~0.9 vs NIFTY ~0.5);
> single-stock *momentum* is where the stock-level edge lives.
