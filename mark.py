"""mark.py — mark the open paper portfolio to market; append to results/nav.csv.

Runs weekly in GitHub Actions. NAV starts at 100 on the first mark of each cycle's entry
date; nifty column tracks ^NSEI rebased the same way, so alpha is visible at a glance.
"""
import csv, os
from datetime import date
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(HERE, "results", "portfolio.csv")
NAV = os.path.join(HERE, "results", "nav.csv")

rows = list(csv.DictReader(open(PORT, newline="")))
if not rows:
    raise SystemExit("no open portfolio")
entry = rows[0]["entry_date"]
syms = [r["symbol"] + ".NS" for r in rows] + ["^NSEI"]
px = yf.download(syms, start=entry, auto_adjust=True, progress=False, group_by="column")["Close"]
today = px.index[-1].strftime("%Y-%m-%d")

nav = sum(float(r["weight"]) * float(px[r["symbol"] + ".NS"].dropna().iloc[-1]) / float(r["entry_px"])
          for r in rows) * 100
n0 = float(px["^NSEI"].dropna().iloc[0]); n1 = float(px["^NSEI"].dropna().iloc[-1])
nifty = n1 / n0 * 100

new = not os.path.exists(NAV)
with open(NAV, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["date", "cycle_entry", "nav", "nifty"])
    w.writerow([today, entry, f"{nav:.2f}", f"{nifty:.2f}"])
print(f"{today}: NAV {nav:.2f} vs NIFTY {nifty:.2f} (cycle {entry})")
