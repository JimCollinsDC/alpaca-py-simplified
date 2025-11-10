# Simplified Account Management API

The `AccountHelper` class provides a clean, simple interface for managing your Alpaca trading account. It eliminates the complexity of working with string-based account data and provides intuitive methods with Python native types.

## Quick Start

```python
from alpaca.trading.account_helper import AccountHelper

# Initialize (auto-loads from environment variables)
helper = AccountHelper()

# Get account balances
print(f"Cash: ${helper.get_cash():,.2f}")
print(f"Buying Power: ${helper.get_buying_power():,.2f}")
print(f"Portfolio: ${helper.get_portfolio_value():,.2f}")

# Check Pattern Day Trader status
if helper.is_pattern_day_trader():
    print("Account is a Pattern Day Trader")
else:
    print(f"Day trades remaining: {helper.get_day_trades_remaining()}")
```

## Configuration

### Environment Variables

The `AccountHelper` automatically loads credentials from environment variables:

```bash
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_PAPER=true  # or false for live trading
```

### Explicit Credentials

You can also provide credentials explicitly:

```python
helper = AccountHelper(
    api_key="your_api_key",
    secret_key="your_secret_key",
    paper=True  # True for paper trading, False for live
)
```

## Features

### Account Information

Get complete account details or specific values.

#### Complete Account Info

```python
account = helper.get_account()
print(f"Account Number: {account.account_number}")
print(f"Status: {account.status}")
print(f"Cash: ${account.cash:,.2f}")
print(f"Equity: ${account.equity:,.2f}")
print(f"Multiplier: {account.multiplier}x")
```

#### Specific Values

```python
# Get individual account values
cash = helper.get_cash()
buying_power = helper.get_buying_power()
portfolio_value = helper.get_portfolio_value()
equity = helper.get_equity()
multiplier = helper.get_multiplier()
```

### Pattern Day Trader (PDT) Management

Easily check PDT status and remaining day trades.

```python
# Check if account is flagged as PDT
if helper.is_pattern_day_trader():
    print("Account is a Pattern Day Trader")
    print("Minimum equity requirement: $25,000")

# Get remaining day trades (0-3)
remaining = helper.get_day_trades_remaining()
print(f"Day trades remaining this week: {remaining}")
```

**PDT Rules:**
- Making 4+ day trades in 5 trading days flags you as a PDT
- PDT accounts must maintain $25,000 minimum equity
- PDT accounts get unlimited day trades (if equity > $25k)
- Non-PDT accounts get 3 day trades per rolling 5-day period

### Account Status

Check if account or trading is blocked.

```python
if helper.is_blocked():
    print("Account or trading is blocked!")
else:
    print("Account is active")
```

### Portfolio History

Get historical portfolio values and performance metrics.

#### Last N Days

```python
# Get last 30 days of daily portfolio history
history = helper.get_portfolio_history(days_back=30, timeframe="1D")

for ts, equity, pl in zip(
    history.timestamps, 
    history.equity, 
    history.profit_loss
):
    print(f"{ts.date()}: ${equity:,.2f} (P/L: ${pl:>+,.2f})")
```

#### Specific Time Period

```python
# Get last week
history = helper.get_portfolio_history(period="1W", timeframe="1D")

# Get last month
history = helper.get_portfolio_history(period="1M", timeframe="1D")

# Get intraday (1-minute bars for today)
history = helper.get_portfolio_history(period="1D", timeframe="1Min")
```

#### Custom Date Range

```python
from datetime import datetime

start = datetime(2025, 1, 1)
end = datetime(2025, 1, 31)
history = helper.get_portfolio_history(
    start=start, 
    end=end, 
    timeframe="1D"
)
```

## Data Models

All data is returned as clean dataclasses with Python native types.

### AccountInfo

```python
@dataclass
class AccountInfo:
    account_number: str
    status: str
    cash: float
    buying_power: float
    portfolio_value: float
    equity: float
    long_market_value: float
    short_market_value: float
    initial_margin: float
    maintenance_margin: float
    last_equity: float
    multiplier: float
    pattern_day_trader: bool
    daytrade_count: int
    daytrading_buying_power: float
    regt_buying_power: float
    trading_blocked: bool
    account_blocked: bool
    created_at: datetime
```

### PortfolioHistoryData

```python
@dataclass
class PortfolioHistoryData:
    timestamps: List[datetime]
    equity: List[float]
    profit_loss: List[float]
    profit_loss_pct: List[float]
    base_value: float
```

## Examples

### Example 1: Pre-Trade Risk Check

```python
from alpaca.trading.account_helper import AccountHelper

helper = AccountHelper()

def can_place_trade(notional: float) -> bool:
    """Check if account can execute trade."""
    # Check if account is blocked
    if helper.is_blocked():
        print("Account is blocked!")
        return False
    
    # Check buying power
    if notional > helper.get_buying_power():
        print("Insufficient buying power!")
        return False
    
    # Check PDT if day trading
    if not helper.is_pattern_day_trader():
        if helper.get_day_trades_remaining() == 0:
            print("No day trades remaining!")
            return False
    
    return True

# Use before placing orders
if can_place_trade(5000.00):
    print("Ready to trade!")
```

### Example 2: Account Performance Report

```python
from alpaca.trading.account_helper import AccountHelper

helper = AccountHelper()

# Get last 30 days
history = helper.get_portfolio_history(days_back=30, timeframe="1D")

if history.timestamps:
    first_equity = history.equity[0]
    last_equity = history.equity[-1]
    
    # Calculate performance
    total_pl = last_equity - first_equity
    total_pl_pct = (total_pl / first_equity) * 100
    
    # Calculate best/worst days
    best_day = max(history.profit_loss)
    worst_day = min(history.profit_loss)
    
    print(f"30-Day Performance Report")
    print(f"========================")
    print(f"Starting: ${first_equity:,.2f}")
    print(f"Ending: ${last_equity:,.2f}")
    print(f"Total P/L: ${total_pl:>+,.2f} ({total_pl_pct:>+.2f}%)")
    print(f"Best Day: ${best_day:>+,.2f}")
    print(f"Worst Day: ${worst_day:>+,.2f}")
```

### Example 3: Account Health Check

```python
from alpaca.trading.account_helper import AccountHelper

helper = AccountHelper()
account = helper.get_account()

# Calculate metrics
cash_ratio = (account.cash / account.equity) * 100
leverage = (account.long_market_value / account.equity)
margin_usage = (account.initial_margin / account.equity) * 100

print(f"Account Health Check")
print(f"===================")
print(f"Cash Ratio: {cash_ratio:.1f}%")
print(f"Leverage: {leverage:.2f}x")
print(f"Margin Usage: {margin_usage:.1f}%")

# Warnings
if cash_ratio < 10:
    print("⚠️ Warning: Low cash reserves")
if leverage > 1.5:
    print("⚠️ Warning: High leverage")
if margin_usage > 50:
    print("⚠️ Warning: High margin usage")
```

### Example 4: Daily Performance Tracker

```python
from alpaca.trading.account_helper import AccountHelper

helper = AccountHelper()

# Get today's performance
history = helper.get_portfolio_history(period="1D", timeframe="5Min")

if history.timestamps:
    start_eq = history.equity[0]
    current_eq = history.equity[-1]
    daily_pl = current_eq - start_eq
    daily_pl_pct = (daily_pl / start_eq) * 100
    
    print(f"Today's Performance")
    print(f"==================")
    print(f"Start: ${start_eq:,.2f}")
    print(f"Current: ${current_eq:,.2f}")
    print(f"P/L: ${daily_pl:>+,.2f} ({daily_pl_pct:>+.2f}%)")
    
    # Show hourly breakdown
    print(f"\nHourly Breakdown:")
    for i in range(0, len(history.timestamps), 12):  # Every hour (12 * 5min)
        if i < len(history.timestamps):
            ts = history.timestamps[i]
            eq = history.equity[i]
            pl = history.profit_loss[i]
            print(f"  {ts.strftime('%H:%M')}: ${eq:,.2f} ({pl:>+,.2f})")
```

## Timeframes

Portfolio history supports the following timeframes:

| Timeframe | Description |
|-----------|-------------|
| `"1Min"` | 1-minute bars |
| `"5Min"` | 5-minute bars |
| `"15Min"` | 15-minute bars |
| `"1H"` | 1-hour bars |
| `"1D"` | Daily bars |

## Periods

Portfolio history supports the following period strings:

| Period | Description |
|--------|-------------|
| `"1D"` | Last trading day |
| `"1W"` | Last week |
| `"1M"` | Last month |
| `"3M"` | Last 3 months |
| `"1A"` | Last year |
| `"all"` | All available history |

## Migration from Original API

### Old Way (Complex)

```python
from alpaca.trading.client import TradingClient

client = TradingClient(api_key="...", secret_key="...", paper=True)
account = client.get_account()

# Everything is a string!
cash = float(account.cash)
buying_power = float(account.buying_power)
equity = float(account.equity)
multiplier = float(account.multiplier)

print(f"Cash: ${cash:,.2f}")
print(f"Buying Power: ${buying_power:,.2f}")

# Manual PDT calculation
is_pdt = account.pattern_day_trader or False
day_trade_count = account.daytrade_count or 0
if is_pdt:
    remaining = 0
else:
    remaining = max(0, 3 - day_trade_count)
print(f"Day trades remaining: {remaining}")

# Portfolio history requires request object
from alpaca.trading.requests import GetPortfolioHistoryRequest
request = GetPortfolioHistoryRequest(period="1M", timeframe="1D")
history = client.get_portfolio_history(filter=request)
for ts, equity in zip(history.timestamp, history.equity):
    print(f"{ts}: {equity}")
```

### New Way (Simple)

```python
from alpaca.trading.account_helper import AccountHelper

helper = AccountHelper()  # Auto-loads from env

# Already floats!
print(f"Cash: ${helper.get_cash():,.2f}")
print(f"Buying Power: ${helper.get_buying_power():,.2f}")

# Simple PDT check
print(f"Day trades remaining: {helper.get_day_trades_remaining()}")

# Simple portfolio history
history = helper.get_portfolio_history(period="1M", timeframe="1D")
for ts, equity in zip(history.timestamps, history.equity):
    print(f"{ts.date()}: ${equity:,.2f}")
```

## Complete API Reference

### Initialization

```python
AccountHelper(
    api_key: Optional[str] = None,      # Auto-loads from ALPACA_API_KEY
    secret_key: Optional[str] = None,   # Auto-loads from ALPACA_SECRET_KEY
    paper: Optional[bool] = None,       # Auto-loads from ALPACA_PAPER (default: True)
)
```

### Account Information Methods

```python
# Complete account info
get_account() -> AccountInfo

# Specific values
get_cash() -> float
get_buying_power() -> float
get_portfolio_value() -> float
get_equity() -> float
get_multiplier() -> float
```

### Pattern Day Trader Methods

```python
# PDT status
is_pattern_day_trader() -> bool

# Remaining day trades (0-3, or 0 if PDT)
get_day_trades_remaining() -> int
```

### Status Methods

```python
# Check if account/trading is blocked
is_blocked() -> bool
```

### Portfolio History Methods

```python
get_portfolio_history(
    period: Optional[str] = None,       # "1D", "1W", "1M", "3M", "1A", "all"
    timeframe: Optional[str] = None,    # "1Min", "5Min", "15Min", "1H", "1D"
    days_back: Optional[int] = None,    # Alternative to period
    start: Optional[datetime] = None,   # Custom start date
    end: Optional[datetime] = None,     # Custom end date
) -> PortfolioHistoryData
```

## Key Benefits

✅ **Native Python types** - All values are `float`, not strings

✅ **Simple method calls** - Direct access without request objects

✅ **PDT calculations** - Built-in Pattern Day Trader tracking

✅ **Portfolio history** - Easy date ranges with `days_back`

✅ **Environment variables** - Auto-loads credentials from `.env`

✅ **Account health** - Simple blocked status and multiplier checks

✅ **Type-safe models** - Clean dataclasses with clear field names

✅ **Consistent API** - Same patterns across all helpers

## See Also

- [Simplified Trading API](simplified_trading_api.md)
- [Simplified Option Data API](simplified_option_api.md)
- [Simplified Stock Data API](simplified_stock_data_api.md)
- [Simplified Crypto Data API](simplified_crypto_data_api.md)
- [Examples Directory](../examples/)
