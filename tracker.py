#!/usr/bin/env python3
"""
Wheel Strategy Options Tracker
================================
Track your Cash-Secured Puts and Covered Calls,
calculate P&L, ROI, and premium collected over time.

Usage:
    python tracker.py                  # Full summary
    python tracker.py --open           # Open positions only
    python tracker.py --ticker SOFI    # Filter by ticker
    python tracker.py --add            # Add a new trade interactively
"""

import csv
import argparse
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict

CSV_FILE = Path(__file__).parent / "trades.csv"
COLLATERAL_MULTIPLIER = 100  # 1 contract = 100 shares


# ─────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────

def load_trades(filepath=CSV_FILE):
    trades = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["premium_collected"] = float(row["premium_collected"])
            row["commission"] = float(row["commission"])
            row["contracts"] = int(row["contracts"])
            row["strike"] = float(row["strike"])
            trades.append(row)
    return trades


# ─────────────────────────────────────────────
# Calculations
# ─────────────────────────────────────────────

def net_premium(trade):
    return trade["premium_collected"] - trade["commission"]


def collateral_required(trade):
    """For CSP: strike * contracts * 100. For CC: already own shares."""
    if trade["contract_type"] == "CSP":
        return trade["strike"] * trade["contracts"] * COLLATERAL_MULTIPLIER
    return trade["strike"] * trade["contracts"] * COLLATERAL_MULTIPLIER  # cost basis for CC


def roi_percent(trade):
    collateral = collateral_required(trade)
    if collateral == 0:
        return 0
    return (net_premium(trade) / collateral) * 100


def days_in_trade(trade):
    opened = datetime.strptime(trade["date_opened"], "%Y-%m-%d").date()
    if trade["date_closed"]:
        closed = datetime.strptime(trade["date_closed"], "%Y-%m-%d").date()
    else:
        closed = date.today()
    return (closed - opened).days


def days_to_expiry(trade):
    if not trade["expiration"]:
        return "N/A"
    exp = datetime.strptime(trade["expiration"], "%Y-%m-%d").date()
    delta = (exp - date.today()).days
    return delta


# ─────────────────────────────────────────────
# Display Helpers
# ─────────────────────────────────────────────

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t):  return color(t, "92")
def red(t):    return color(t, "91")
def yellow(t): return color(t, "93")
def bold(t):   return color(t, "1")
def cyan(t):   return color(t, "96")

def fmt_dollar(val):
    if val >= 0:
        return green(f"${val:,.2f}")
    return red(f"-${abs(val):,.2f}")

def fmt_pct(val):
    if val >= 0:
        return green(f"{val:.2f}%")
    return red(f"{val:.2f}%")


# ─────────────────────────────────────────────
# Reports
# ─────────────────────────────────────────────

def print_header():
    print("\n" + "═" * 70)
    print(bold(cyan("  🎡  WHEEL STRATEGY TRACKER")))
    print("═" * 70)


def print_trade_table(trades, title="Trades"):
    print(f"\n{bold(title)}")
    print("─" * 90)
    header = f"{'#':<4} {'Ticker':<7} {'Type':<5} {'Strike':<8} {'Exp':<12} {'Contracts':<10} {'Net Premium':<14} {'ROI':<8} {'DTE/Days':<10} {'Status':<8}"
    print(bold(header))
    print("─" * 90)

    for i, t in enumerate(trades, 1):
        dte = days_to_expiry(t) if t["status"] == "open" else days_in_trade(t)
        dte_label = f"{dte}d" if isinstance(dte, int) else dte
        status_fmt = green("open") if t["status"] == "open" else yellow("closed")
        assigned_flag = red(" ⚠ assigned") if t["assigned"] == "Yes" else ""

        print(
            f"{i:<4} {t['ticker']:<7} {t['contract_type']:<5} "
            f"${t['strike']:<7.2f} {t['expiration']:<12} {t['contracts']:<10} "
            f"{fmt_dollar(net_premium(t)):<23} {fmt_pct(roi_percent(t)):<17} "
            f"{dte_label:<10} {status_fmt}{assigned_flag}"
        )
    print("─" * 90)


def print_summary(trades):
    closed = [t for t in trades if t["status"] == "closed"]
    open_t = [t for t in trades if t["status"] == "open"]

    total_premium = sum(net_premium(t) for t in trades)
    closed_premium = sum(net_premium(t) for t in closed)
    open_premium = sum(net_premium(t) for t in open_t)
    total_commission = sum(t["commission"] for t in trades)
    assigned_count = sum(1 for t in trades if t["assigned"] == "Yes")

    # Per-ticker breakdown
    by_ticker = defaultdict(list)
    for t in trades:
        by_ticker[t["ticker"]].append(t)

    print(f"\n{bold('📊 SUMMARY')}")
    print("─" * 50)
    print(f"  Total trades:        {len(trades)}")
    print(f"  Closed trades:       {len(closed)}")
    print(f"  Open positions:      {len(open_t)}")
    print(f"  Times assigned:      {red(str(assigned_count)) if assigned_count else green('0')}")
    print(f"  Total commissions:   {fmt_dollar(-total_commission)}")
    print(f"  Net premium (closed):{fmt_dollar(closed_premium)}")
    print(f"  Net premium (open):  {fmt_dollar(open_premium)}")
    print(f"  Net premium (total): {bold(fmt_dollar(total_premium))}")

    print(f"\n{bold('🎯 PER-TICKER BREAKDOWN')}")
    print("─" * 50)
    print(f"  {'Ticker':<8} {'Trades':<8} {'Net Premium':<16} {'Assignments'}")
    print("  " + "─" * 44)
    for ticker, ttrades in sorted(by_ticker.items()):
        ticker_net = sum(net_premium(t) for t in ttrades)
        ticker_assigned = sum(1 for t in ttrades if t["assigned"] == "Yes")
        assigned_str = red(f"{ticker_assigned}x") if ticker_assigned else green("0")
        print(f"  {ticker:<8} {len(ttrades):<8} {fmt_dollar(ticker_net):<25} {assigned_str}")

    print("─" * 50)


def print_open_positions(trades):
    open_t = [t for t in trades if t["status"] == "open"]
    if not open_t:
        print(green("\n✅ No open positions."))
        return
    print_trade_table(open_t, title="📂 OPEN POSITIONS")

    print(f"\n  {bold('⏰ DTE Alerts:')}")
    for t in open_t:
        dte = days_to_expiry(t)
        if isinstance(dte, int):
            if dte <= 7:
                print(f"  {red('⚠')}  {t['ticker']} {t['contract_type']} ${t['strike']} — {red(f'{dte} days to expiry!')}")
            elif dte <= 14:
                print(f"  {yellow('!')}  {t['ticker']} {t['contract_type']} ${t['strike']} — {yellow(f'{dte} days to expiry')}")


# ─────────────────────────────────────────────
# Add Trade Interactively
# ─────────────────────────────────────────────

def add_trade():
    print(f"\n{bold('➕ ADD NEW TRADE')}")
    print("─" * 40)

    trades = load_trades()
    new_id = max(int(t["trade_id"]) for t in trades) + 1

    ticker = input("Ticker (e.g. SOFI): ").strip().upper()
    contract_type = input("Type (CSP/CC): ").strip().upper()
    strike = float(input("Strike price: "))
    expiration = input("Expiration (YYYY-MM-DD): ").strip()
    contracts = int(input("Number of contracts: "))
    premium = float(input("Premium collected ($): "))
    commission = float(input("Commission paid ($): "))
    notes = input("Notes (optional): ").strip()

    today = date.today().isoformat()

    new_row = {
        "trade_id": new_id,
        "date_opened": today,
        "date_closed": "",
        "ticker": ticker,
        "strategy": "Wheel",
        "contract_type": contract_type,
        "strike": strike,
        "expiration": expiration,
        "contracts": contracts,
        "premium_collected": premium,
        "commission": commission,
        "status": "open",
        "assigned": "No",
        "notes": notes,
    }

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_row.keys())
        writer.writerow(new_row)

    print(green(f"\n✅ Trade #{new_id} added: {ticker} {contract_type} ${strike} — Net: ${premium - commission:.2f}"))


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wheel Strategy Tracker")
    parser.add_argument("--open", action="store_true", help="Show open positions only")
    parser.add_argument("--ticker", type=str, help="Filter by ticker symbol")
    parser.add_argument("--add", action="store_true", help="Add a new trade")
    args = parser.parse_args()

    if args.add:
        add_trade()
        return

    trades = load_trades()

    if args.ticker:
        trades = [t for t in trades if t["ticker"].upper() == args.ticker.upper()]
        if not trades:
            print(red(f"\nNo trades found for {args.ticker.upper()}"))
            return

    print_header()

    if args.open:
        print_open_positions(trades)
    else:
        print_trade_table(trades, title="📋 ALL TRADES")
        print_summary(trades)
        print_open_positions(trades)

    print()


if __name__ == "__main__":
    main()
