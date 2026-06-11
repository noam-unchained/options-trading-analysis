# Wheel Strategy Options Tracker

A clean, terminal-based Python tool to track your Cash-Secured Puts (CSP) and Covered Calls (CC) when running the Wheel Strategy.

No subscriptions. No bloated apps. Just your trades, your data, your terminal.

---

## Preview

```
======================================================================
  WHEEL STRATEGY TRACKER
======================================================================

ALL TRADES
------------------------------------------------------------------------------------------
#    Ticker  Type  Strike   Exp          Contracts  Net Premium    ROI      DTE/Days
------------------------------------------------------------------------------------------
1    SOFI    CSP   $8.00    2024-01-19   2          $139.40        0.87%    14d     closed
2    HOOD    CSP   $14.00   2024-01-26   1          $85.70         0.61%    18d     closed
...

SUMMARY
--------------------------------------------------
  Total trades:         13
  Closed trades:        10
  Open positions:       3
  Net premium (total):  $1,418.00
```

---

## Features

- Full trade log — view all trades with P&L, ROI, and days in trade
- Open positions view — with automatic DTE (days to expiry) alerts
- Per-ticker breakdown — see which underlyings are making you money
- Add trades interactively — no need to edit CSV manually
- Assignment tracking — flags assigned positions clearly
- Expiry alerts — warns you when positions are within 7 or 14 days of expiry
- Net premium calculation — automatically subtracts commissions

---

## Installation

```bash
git clone https://github.com/noam-unchained/options-wheel-tracker.git
cd options-wheel-tracker
python tracker.py
```

No external dependencies — uses Python standard library only.

Requires Python 3.7+

---

## Usage

```bash
# Full dashboard (all trades + summary + open positions)
python tracker.py

# Open positions only (with DTE alerts)
python tracker.py --open

# Filter by ticker
python tracker.py --ticker SOFI

# Add a new trade interactively
python tracker.py --add
```

---

## trades.csv Format

| Field | Description | Example |
|---|---|---|
| `trade_id` | Unique ID | `1` |
| `date_opened` | Open date | `2024-01-05` |
| `date_closed` | Close date (blank if open) | `2024-01-19` |
| `ticker` | Stock symbol | `SOFI` |
| `strategy` | Strategy name | `Wheel` |
| `contract_type` | `CSP` or `CC` | `CSP` |
| `strike` | Strike price | `8.00` |
| `expiration` | Expiry date | `2024-01-19` |
| `contracts` | Number of contracts | `2` |
| `premium_collected` | Gross premium in $ | `142.00` |
| `commission` | Commission paid in $ | `2.60` |
| `status` | `open` or `closed` | `closed` |
| `assigned` | `Yes` or `No` | `No` |
| `notes` | Optional notes | `Expired worthless` |

---

## Roadmap

- v1.1 — `yfinance` integration for live stock prices
- v1.2 — Streamlit web dashboard with charts
- v1.3 — Premium collected over time graph
- v1.4 — Wheel cycle tracker (CSP -> assignment -> CC -> repeat)
- v2.0 — Export to PDF report

---

## The Wheel Strategy (Quick Recap)

```
Sell CSP (Cash-Secured Put)
        |
        |-- Expires worthless -> Collect premium -> Sell new CSP
        |
        +-- Assigned (stock put to you)
                |
                +-- Sell CC (Covered Call)
                        |
                        |-- Expires worthless -> Collect premium -> Sell new CC
                        |
                        +-- Called away (stock sold) -> Back to selling CSPs
```

---

## Contributing

Pull requests welcome. If you're also running the Wheel and have feature ideas — open an issue.

---

## Disclaimer

This tool is for personal trade tracking only. Nothing here is financial advice.

---

## License

MIT
