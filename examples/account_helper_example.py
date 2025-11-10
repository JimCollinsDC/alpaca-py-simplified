"""
AccountHelper - Simplified Account Management API Examples

This file demonstrates how to use the AccountHelper class for
account management with a clean, simple API.
"""

from alpaca.trading.account_helper import AccountHelper

# Initialize helper (auto-loads API keys from environment)
helper = AccountHelper()

# Alternative: explicit credentials
# helper = AccountHelper(api_key="your_key", secret_key="your_secret", paper=True)

print("=" * 70)
print("AccountHelper Examples - Simplified Account Management API")
print("=" * 70)

# ============================================================================
# Example 1: Quick Account Overview
# ============================================================================
print("\n1. Quick Account Overview:")
print("-" * 70)

print(f"Cash: ${helper.get_cash():,.2f}")
print(f"Buying Power: ${helper.get_buying_power():,.2f}")
print(f"Portfolio Value: ${helper.get_portfolio_value():,.2f}")
print(f"Equity: ${helper.get_equity():,.2f}")

# ============================================================================
# Example 2: Complete Account Details
# ============================================================================
print("\n2. Complete Account Information:")
print("-" * 70)

account = helper.get_account()
print(f"Account Number: {account.account_number}")
print(f"Status: {account.status}")
print(f"Created: {account.created_at.strftime('%Y-%m-%d')}")
print("\nBalances:")
print(f"  Cash: ${account.cash:,.2f}")
print(f"  Buying Power: ${account.buying_power:,.2f}")
print(f"  Portfolio Value: ${account.portfolio_value:,.2f}")
print(f"  Equity: ${account.equity:,.2f}")
print("\nPositions:")
print(f"  Long Market Value: ${account.long_market_value:,.2f}")
print(f"  Short Market Value: ${account.short_market_value:,.2f}")
print("\nMargin:")
print(f"  Multiplier: {account.multiplier}x")
print(f"  Initial Margin: ${account.initial_margin:,.2f}")
print(f"  Maintenance Margin: ${account.maintenance_margin:,.2f}")

# ============================================================================
# Example 3: Pattern Day Trader (PDT) Status
# ============================================================================
print("\n3. Pattern Day Trader Status:")
print("-" * 70)

if helper.is_pattern_day_trader():
    print("⚠️  Account is flagged as a Pattern Day Trader")
    print("   Minimum equity requirement: $25,000")
else:
    remaining = helper.get_day_trades_remaining()
    print("✓ Not a Pattern Day Trader")
    print(f"  Day trades remaining this week: {remaining}")
    if remaining <= 1:
        print("  ⚠️ Warning: Low day trades remaining!")

# ============================================================================
# Example 4: Account Status Checks
# ============================================================================
print("\n4. Account Status Checks:")
print("-" * 70)

if helper.is_blocked():
    print("❌ Account or trading is blocked!")
else:
    print("✓ Account is active and trading is enabled")

multiplier = helper.get_multiplier()
print(f"\nMargin Multiplier: {multiplier}x")
if multiplier >= 4:
    print("  (Portfolio Margin Account)")
elif multiplier >= 2:
    print("  (Reg T Margin Account)")
else:
    print("  (Cash Account)")

# ============================================================================
# Example 5: Portfolio History - Last 30 Days
# ============================================================================
print("\n5. Portfolio History (Last 30 Days):")
print("-" * 70)

history = helper.get_portfolio_history(days_back=30, timeframe="1D")

if history.timestamps:
    first_equity = history.equity[0]
    last_equity = history.equity[-1]
    total_pl = last_equity - first_equity
    total_pl_pct = (total_pl / first_equity) * 100

    print(f"Period: {history.timestamps[0].date()} to "
          f"{history.timestamps[-1].date()}")
    print(f"Starting Equity: ${first_equity:,.2f}")
    print(f"Ending Equity: ${last_equity:,.2f}")
    print(f"Total P/L: ${total_pl:>+,.2f} ({total_pl_pct:>+.2f}%)")

    # Show last 5 days
    print("\nLast 5 Days:")
    for i in range(max(0, len(history.timestamps) - 5), len(history.timestamps)):
        ts = history.timestamps[i]
        eq = history.equity[i]
        pl = history.profit_loss[i]
        pl_pct = history.profit_loss_pct[i]
        arrow = "▲" if pl >= 0 else "▼"
        print(
            f"  {ts.date()} | Equity: ${eq:>10,.2f} | "
            f"P/L: {arrow} ${abs(pl):>8,.2f} ({pl_pct:>+6.2f}%)"
        )

# ============================================================================
# Example 6: Portfolio History - Intraday (1 Minute Bars)
# ============================================================================
print("\n6. Intraday Portfolio History (Last Hour):")
print("-" * 70)

intraday = helper.get_portfolio_history(period="1D", timeframe="1Min")

if intraday.timestamps and len(intraday.timestamps) > 0:
    # Show last 5 minutes
    print("Last 5 minutes of trading:")
    for i in range(max(0, len(intraday.timestamps) - 5),
                   len(intraday.timestamps)):
        ts = intraday.timestamps[i]
        eq = intraday.equity[i]
        pl = intraday.profit_loss[i]
        print(f"  {ts.strftime('%H:%M')} | ${eq:>10,.2f} | "
              f"P/L: ${pl:>+8,.2f}")

# ============================================================================
# Example 7: Calculate Account Metrics
# ============================================================================
print("\n7. Account Metrics:")
print("-" * 70)

account = helper.get_account()

# Calculate utilization
cash_pct = (account.cash / account.equity) * 100 if account.equity > 0 else 0
positions_pct = 100 - cash_pct

# Calculate leverage
leverage = (
    account.long_market_value / account.equity
    if account.equity > 0 else 0
)

# Calculate margin used
margin_used_pct = (
    (account.initial_margin / account.equity) * 100
    if account.equity > 0 else 0
)

print("Account Utilization:")
print(f"  Cash: {cash_pct:.1f}%")
print(f"  Positions: {positions_pct:.1f}%")
print(f"\nLeverage: {leverage:.2f}x")
print(f"Margin Used: {margin_used_pct:.1f}%")

# Buying power as % of equity
bp_ratio = (
    (account.buying_power / account.equity)
    if account.equity > 0 else 0
)
print(f"Buying Power Ratio: {bp_ratio:.2f}x")

# ============================================================================
# Example 8: Weekly Performance Summary
# ============================================================================
print("\n8. Weekly Performance Summary:")
print("-" * 70)

weekly = helper.get_portfolio_history(period="1W", timeframe="1D")

if weekly.timestamps and len(weekly.timestamps) > 0:
    # Group by week day
    daily_changes = {}
    for i, ts in enumerate(weekly.timestamps):
        day_name = ts.strftime("%A")
        pl = weekly.profit_loss[i]
        if day_name not in daily_changes:
            daily_changes[day_name] = []
        daily_changes[day_name].append(pl)

    print("Average P/L by day of week:")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        if day in daily_changes:
            avg_pl = sum(daily_changes[day]) / len(daily_changes[day])
            arrow = "▲" if avg_pl >= 0 else "▼"
            print(f"  {day:10} {arrow} ${abs(avg_pl):>8,.2f}")

# ============================================================================
# Example 9: Risk Check Before Trading
# ============================================================================
print("\n9. Pre-Trade Risk Check:")
print("-" * 70)


def can_trade(symbol: str, notional: float) -> bool:
    """Check if account can execute trade."""
    if helper.is_blocked():
        print(f"❌ Cannot trade {symbol}: Account is blocked")
        return False

    bp = helper.get_buying_power()
    if notional > bp:
        print(f"❌ Cannot trade {symbol}: Insufficient buying power")
        print(f"   Required: ${notional:,.2f}, Available: ${bp:,.2f}")
        return False

    # Check PDT if day trading
    if not helper.is_pattern_day_trader():
        remaining = helper.get_day_trades_remaining()
        if remaining == 0:
            print("⚠️  Warning: No day trades remaining this week")

    print(f"✓ Can execute {symbol} trade for ${notional:,.2f}")
    return True


# Example trade check
can_trade("AAPL", 5000.00)

# ============================================================================
# Example 10: Old API vs New API Comparison
# ============================================================================
print("\n10. Old API vs New API Comparison:")
print("-" * 70)

print("\nOLD WAY (Complex):")
print("""
from alpaca.trading.client import TradingClient

client = TradingClient(api_key="...", secret_key="...", paper=True)
account = client.get_account()

# Everything is a string!
cash = float(account.cash)
buying_power = float(account.buying_power)
portfolio_value = float(account.portfolio_value)

print(f"Cash: ${cash:,.2f}")
print(f"Buying Power: ${buying_power:,.2f}")
print(f"Portfolio: ${portfolio_value:,.2f}")

# Pattern Day Trader check
is_pdt = account.pattern_day_trader or False
day_trade_count = account.daytrade_count or 0
remaining = max(0, 3 - day_trade_count) if not is_pdt else 0
print(f"Day trades remaining: {remaining}")
""")

print("\nNEW WAY (Simple):")
print("""
from alpaca.trading.account_helper import AccountHelper

helper = AccountHelper()  # Auto-loads from env

# Already floats!
print(f"Cash: ${helper.get_cash():,.2f}")
print(f"Buying Power: ${helper.get_buying_power():,.2f}")
print(f"Portfolio: ${helper.get_portfolio_value():,.2f}")

# Simple PDT check
print(f"Day trades remaining: {helper.get_day_trades_remaining()}")
""")

print("\n" + "=" * 70)
print("Key Benefits:")
print("  - Native Python types (float, not strings)")
print("  - Simple method calls (no complex parsing)")
print("  - Pattern Day Trader calculations built-in")
print("  - Portfolio history with easy date ranges")
print("  - Environment variable loading")
print("  - Clean account status checks")
print("=" * 70)
