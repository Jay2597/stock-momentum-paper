"""mark.py — mark the open paper portfolio to market; append to results/nav.csv.

Runs weekly in GitHub Actions. NAV starts at 100 on the first mark of each cycle's entry
date; nifty column tracks ^NSEI rebased the same way, so alpha is visible at a glance.
Because NAV rebases per cycle, cumulative performance must be chained across cycles (or
rebuilt from results/history.csv) -- it cannot be read off the last row.
"""
import csv, os, time
from datetime import date
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(HERE, "results", "portfolio.csv")
NAV = os.path.join(HERE, "results", "nav.csv")

ATTEMPTS, BACKOFF = 4, 15


def fetch(syms, start):
    """Download closes, retrying while any symbol is missing or entirely NaN.

    yfinance intermittently hands back a frame where a column exists but holds no
    usable data. The old code went straight to `.dropna().iloc[-1]` on that and died
    with an opaque `IndexError: single positional indexer is out-of-bounds` (CI run
    33647104545 on 2026-09-02), losing that day's mark entirely; a local run two
    hours later succeeded on identical inputs, so the gap is transient.

    Retry, and if the data still will not come back, exit loudly naming the symbols
    at fault. Never fall through to a NAV computed from a partial frame -- a missing
    name silently drops its weight and understates the book.
    """
    problem = ""
    for i in range(ATTEMPTS):
        if i:
            time.sleep(BACKOFF)
        px = yf.download(syms, start=start, auto_adjust=True, progress=False,
                         group_by="column")["Close"]
        missing = [s for s in syms if s not in px or px[s].dropna().empty]
        if not px.empty and not missing:
            return px
        problem = ", ".join(missing) if missing else "empty frame"
        print(f"attempt {i + 1}/{ATTEMPTS}: incomplete price data ({problem}) — retrying")
    raise SystemExit(f"no usable price data after {ATTEMPTS} attempts: {problem}")


rows = list(csv.DictReader(open(PORT, newline="")))
if not rows:
    raise SystemExit("no open portfolio")
entry = rows[0]["entry_date"]
syms = [r["symbol"] + ".NS" for r in rows] + ["^NSEI"]
px = fetch(syms, entry)
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
