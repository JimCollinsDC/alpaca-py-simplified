# Simplified Trading API

The `TradingHelper` class provides a simplified, pythonic interface for Alpaca trading operations. It eliminates the need to work with multiple request classes and handles common patterns with simple method calls.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Features](#features)
  - [Market Orders](#market-orders)
  - [Limit Orders](#limit-orders)
  - [Bracket Orders](#bracket-orders)
  - [Position Management](#position-management)
  - [Order Management](#order-management)
  - [Account Information](#account-information)
- [Examples](#examples)
- [Migration Guide](#migration-guide)

## Quick Start

```python
from alpaca.trading.trading_helper import TradingHelper

# Initialize (auto-loads from environment)
helper = TradingHelper()

# Buy 10 shares at market
order = helper.buy_market("SPY", qty=10)

# Buy with stop loss and take profit
order = helper.buy_with_bracket(
    "SPY",
    qty=10,
    stop_loss=450.00,
    take_profit=550.00
)

# Check your positions
positions = helper.get_all_positions()
for pos in positions:
    print(f"{pos.symbol}: ${pos.unrealized_pl:.2f} P&L")

# Close a position
helper.close_position("SPY", percentage=50)
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_PAPER=true  # Set to false for live trading
```

Then load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()

from alpaca.trading.trading_helper import TradingHelper

# Automatically uses environment variables
helper = TradingHelper()
```

### Explicit Configuration

You can also provide credentials directly:

```python
helper = TradingHelper(
    api_key="your_api_key",
    secret_key="your_secret_key",
    paper=True  # or False for live trading
)
```

## Features

### Market Orders

Place market orders with a single method call.

```python
# Buy shares
order = helper.buy_market("SPY", qty=10)

# Buy by dollar amount
order = helper.buy_market("SPY", notional=1000.0)

# Sell shares
order = helper.sell_market("SPY", qty=5)

# Custom time-in-force
from alpaca.trading.enums import TimeInForce
order = helper.buy_market("SPY", qty=10, time_in_force=TimeInForce.GTC)
```

### Limit Orders

Place limit orders to specify exact prices.

```python
# Buy at or below limit price
order = helper.buy_limit("SPY", qty=10, limit_price=550.00)

# Sell at or above limit price
order = helper.sell_limit("SPY", qty=10, limit_price=600.00)

# With GTC time-in-force
order = helper.buy_limit(
    "SPY",
    qty=10,
    limit_price=550.00,
    time_in_force=TimeInForce.GTC
)
```

### Bracket Orders

Bracket orders combine entry with stop loss and take profit in one call.

```python
# Buy with both stop loss and take profit
order = helper.buy_with_bracket(
    symbol="SPY",
    qty=10,
    stop_loss=450.00,      # Exit if price drops to $450
    take_profit=600.00     # Exit if price reaches $600
)

# Buy with only stop loss
order = helper.buy_with_bracket(
    "SPY",
    qty=10,
    stop_loss=450.00
)

# Buy with only take profit
order = helper.buy_with_bracket(
    "SPY",
    qty=10,
    take_profit=600.00
)

# Use stop-limit instead of stop order
order = helper.buy_with_bracket(
    "SPY",
    qty=10,
    stop_loss=450.00,       # Trigger price
    stop_loss_limit=445.00  # Limit price (creates stop-limit order)
)

# Sell short with bracket
order = helper.sell_with_bracket(
    "SPY",
    qty=10,
    stop_loss=550.00,      # Exit if price rises to $550
    take_profit=450.00     # Exit if price drops to $450
)
```

### Position Management

View and manage your positions.

```python
# Get all open positions
positions = helper.get_all_positions()
for pos in positions:
    print(f"{pos.symbol}: {pos.qty} shares")
    print(f"  P&L: ${pos.unrealized_pl:.2f} ({pos.unrealized_plpc * 100:.2f}%)")
    print(f"  Avg Entry: ${pos.avg_entry_price:.2f}")
    print(f"  Current: ${pos.current_price:.2f}")

# Get specific position
position = helper.get_position("SPY")
print(f"SPY: {position.qty} shares, ${position.market_value:.2f} value")

# Close entire position
order = helper.close_position("SPY")

# Close 50% of position
order = helper.close_position("SPY", percentage=50)

# Close specific quantity
order = helper.close_position("SPY", qty=5)
```

#### PositionInfo Object

The `PositionInfo` dataclass provides simplified position information:

```python
@dataclass
class PositionInfo:
    symbol: str                 # Stock symbol
    qty: float                  # Quantity of shares
    market_value: float         # Current market value
    avg_entry_price: float      # Average entry price
    current_price: float        # Current price
    unrealized_pl: float        # Unrealized profit/loss ($)
    unrealized_plpc: float      # Unrealized profit/loss (%)
    side: str                   # 'long' or 'short'
    cost_basis: float           # Total cost basis
    asset_id: str               # Alpaca asset ID
```

### Order Management

Query and manage your orders.

```python
# Get all open orders
orders = helper.get_orders()
for order in orders:
    print(f"{order.symbol}: {order.side} {order.qty} @ {order.type}")

# Get all orders (including filled and cancelled)
from alpaca.trading.enums import QueryOrderStatus
all_orders = helper.get_orders(status=QueryOrderStatus.ALL)

# Filter by symbols
spy_orders = helper.get_orders(symbols=["SPY"])

# Limit results
recent_orders = helper.get_orders(limit=10)

# Get specific order
order = helper.get_order(order_id)
print(f"Status: {order.status}")
print(f"Filled: {order.filled_qty} / {order.qty}")

# Cancel specific order
helper.cancel_order(order_id)

# Cancel all open orders
helper.cancel_all_orders()
```

#### OrderInfo Object

The `OrderInfo` dataclass provides simplified order information:

```python
@dataclass
class OrderInfo:
    id: str                          # Order ID
    symbol: str                      # Stock symbol
    qty: Optional[float]             # Quantity (if qty-based)
    notional: Optional[float]        # Dollar amount (if notional-based)
    side: str                        # 'buy' or 'sell'
    type: str                        # 'market', 'limit', 'stop', etc.
    status: str                      # Order status
    filled_qty: float                # Quantity filled
    filled_avg_price: Optional[float] # Average fill price
    limit_price: Optional[float]     # Limit price (if applicable)
    stop_price: Optional[float]      # Stop price (if applicable)
    submitted_at: datetime           # Submission time
    filled_at: Optional[datetime]    # Fill time
    order_class: Optional[str]       # 'simple', 'bracket', 'oco', 'oto'
```

### Account Information

Quick access to account details.

```python
# Get buying power
buying_power = helper.get_buying_power()
print(f"Buying Power: ${buying_power:,.2f}")

# Get cash balance
cash = helper.get_cash()
print(f"Cash: ${cash:,.2f}")

# Get total portfolio value
portfolio_value = helper.get_portfolio_value()
print(f"Portfolio: ${portfolio_value:,.2f}")

# Check if using paper trading
if helper.is_paper:
    print("Using paper trading account")
```

## Examples

### Example 1: Simple Day Trading Bot

```python
from alpaca.trading.trading_helper import TradingHelper

helper = TradingHelper()

# Buy at market open
order = helper.buy_market("SPY", qty=100)

# Set stop loss and take profit
helper.buy_with_bracket(
    "SPY",
    qty=100,
    stop_loss=order.filled_avg_price * 0.98,  # 2% stop loss
    take_profit=order.filled_avg_price * 1.05  # 5% take profit
)
```

### Example 2: Position Monitoring

```python
from alpaca.trading.trading_helper import TradingHelper

helper = TradingHelper()

# Monitor all positions
positions = helper.get_all_positions()

for pos in positions:
    # Close positions with >10% loss
    if pos.unrealized_plpc < -0.10:
        print(f"Closing {pos.symbol} with {pos.unrealized_plpc * 100:.1f}% loss")
        helper.close_position(pos.symbol)
    
    # Take profit on >20% gains
    elif pos.unrealized_plpc > 0.20:
        print(f"Taking profit on {pos.symbol} with {pos.unrealized_plpc * 100:.1f}% gain")
        helper.close_position(pos.symbol)
```

### Example 3: Portfolio Rebalancing

```python
from alpaca.trading.trading_helper import TradingHelper

helper = TradingHelper()

target_allocation = {
    "SPY": 0.50,   # 50% S&P 500
    "QQQ": 0.30,   # 30% Nasdaq
    "IWM": 0.20    # 20% Russell 2000
}

portfolio_value = helper.get_portfolio_value()

for symbol, target_pct in target_allocation.items():
    target_value = portfolio_value * target_pct
    
    try:
        position = helper.get_position(symbol)
        current_value = position.market_value
        
        if current_value < target_value * 0.95:
            # Buy more
            helper.buy_market(symbol, notional=target_value - current_value)
        elif current_value > target_value * 1.05:
            # Sell some
            helper.sell_market(symbol, notional=current_value - target_value)
    except:
        # No position, buy target amount
        helper.buy_market(symbol, notional=target_value)
```

## Migration Guide

### From Standard TradingClient

**Before (Standard API):**

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    StopLossRequest,
    TakeProfitRequest
)
from alpaca.trading.enums import OrderSide, OrderClass, TimeInForce

client = TradingClient(api_key="...", secret_key="...", paper=True)

# Complex bracket order
request = MarketOrderRequest(
    symbol="SPY",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY,
    order_class=OrderClass.BRACKET,
    take_profit=TakeProfitRequest(limit_price=550.00),
    stop_loss=StopLossRequest(stop_price=450.00)
)
order = client.submit_order(request)

# Complex position query
position = client.get_open_position("SPY")
qty = float(position.qty)
unrealized_pl = float(position.unrealized_pl)
```

**After (TradingHelper):**

```python
from alpaca.trading.trading_helper import TradingHelper

helper = TradingHelper()  # Auto-loads from env

# Simple bracket order
order = helper.buy_with_bracket(
    "SPY",
    qty=10,
    stop_loss=450.00,
    take_profit=550.00
)

# Simple position query
position = helper.get_position("SPY")
qty = position.qty  # Already a float
unrealized_pl = position.unrealized_pl  # Already a float
```

### Key Differences

1. **Environment Variables**: TradingHelper automatically loads credentials from environment variables
2. **No Request Objects**: Methods accept simple parameters instead of request objects
3. **Simplified Returns**: Returns `PositionInfo` and `OrderInfo` dataclasses with float types instead of strings
4. **One-Line Brackets**: Bracket orders are a single method call with named parameters
5. **Pythonic**: Uses standard Python types (float, str) instead of Alpaca-specific types

## Error Handling

The TradingHelper raises standard Python exceptions:

```python
from alpaca.trading.trading_helper import TradingHelper

helper = TradingHelper()

try:
    order = helper.buy_market("SPY", qty=10)
    print(f"Order placed: {order.id}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## See Also

- [OptionHelper Documentation](./simplified_option_api.md) - Simplified option data API
- [Standard Trading API](../docs/trading.rst) - Full trading API documentation
- [Alpaca API Docs](https://alpaca.markets/docs/) - Official Alpaca documentation
