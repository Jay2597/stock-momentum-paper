"""pick.py — monthly rebalance of the 12-1 momentum paper portfolio.

Run near month-end. Ranks the F&O universe on 12-month return skipping the last month
(P[d-21]/P[d-252] - 1 on daily closes), takes the top 20 equal-weight. Closes the previous
cycle into results/history.csv (realized returns at today's close) and writes the new
portfolio to results/portfolio.csv. Marking is done weekly by mark.py in CI.
"""
import csv, json, os
from datetime import date
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
PORT = os.path.join(RES, "portfolio.csv")
HIST = os.path.join(RES, "history.csv")
N, LB, SKIP = 20, 252, 21

uni = json.load(open(os.path.join(HERE, "universe.json")))["universe"]
px = yf.download([s + ".NS" for s in uni], period="15mo", auto_adjust=True,
                 progress=False, group_by="column")["Close"]
px.columns = [c[:-3] for c in px.columns]
today = px.index[-1].strftime("%Y-%m-%d")

# close the open cycle, if any
if os.path.exists(PORT):
    rows = list(csv.DictReader(open(PORT, newline="")))
    if rows:
        os.makedirs(RES, exist_ok=True)
        new = not os.path.exists(HIST)
        with open(HIST, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["entry_date", "exit_date", "symbol", "entry_px", "exit_px", "ret_pct"])
            for r in rows:
                s = r["symbol"]
                exit_px = float(px[s].dropna().iloc[-1]) if s in px else ""
                ret = (exit_px / float(r["entry_px"]) - 1) * 100 if exit_px else ""
                w.writerow([r["entry_date"], today, s, r["entry_px"],
                            f"{exit_px:.2f}" if exit_px else "", f"{ret:.2f}" if ret else ""])
        print(f"closed cycle of {len(rows)} names -> history.csv")

# rank and open the new cycle
mom = (px.iloc[-1 - SKIP] / px.iloc[-1 - LB + 1] - 1).dropna()
mom = mom[px.iloc[-1].notna()]
top = mom.nlargest(N)
os.makedirs(RES, exist_ok=True)
with open(PORT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["entry_date", "symbol", "entry_px", "weight", "mom_12_1_pct"])
    for s, sc in top.items():
        w.writerow([today, s, f"{float(px[s].dropna().iloc[-1]):.2f}",
                    f"{1/N:.4f}", f"{sc*100:.1f}"])
print(f"new portfolio ({today}):")
for s, sc in top.items():
    print(f"  {s:<12} 12-1 mom {sc*100:+7.1f}%")
