# Simplified Stock Data API

The `StockHelper` class provides a simplified, pythonic interface for Alpaca stock market data. It eliminates the need to work with complex request objects and provides clean, type-safe data models.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Features](#features)
  - [Latest Data](#latest-data)
  - [Historical Bars (OHLCV)](#historical-bars-ohlcv)
  - [Historical Quotes](#historical-quotes)
  - [Historical Trades](#historical-trades)
  - [Snapshots](#snapshots)
  - [Multi-Symbol Support](#multi-symbol-support)
- [Timeframes](#timeframes)
- [Data Models](#data-models)
- [Examples](#examples)
- [Migration Guide](#migration-guide)

## Quick Start

```python
from alpaca.data.stock_helper import StockHelper

# Initialize (auto-loads from environment)
helper = StockHelper()

# Get latest quote
quote = helper.get_latest_quote("SPY")
print(f"Bid: ${quote.bid_price}, Ask: ${quote.ask_price}")

# Get historical bars
bars = helper.get_bars("SPY", timeframe="1H", days_back=5)
for bar in bars:
    print(f"{bar.timestamp}: ${bar.close}")

# Get data for multiple symbols
quotes = helper.get_latest_quotes(["SPY", "QQQ", "IWM"])
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

Then load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()

from alpaca.data.stock_helper import StockHelper

# Automatically uses environment variables
helper = StockHelper()
```

### Explicit Configuration

```python
helper = StockHelper(
    api_key="your_api_key",
    secret_key="your_secret_key"
)
```

## Features

### Latest Data

Get the most recent quote, bar, or trade for any symbol.

#### Latest Quote

```python
# Single symbol
quote = helper.get_latest_quote("SPY")
print(f"Bid: ${quote.bid_price} x {quote.bid_size}")
print(f"Ask: ${quote.ask_price} x {quote.ask_size}")
print(f"Spread: ${quote.ask_price - quote.bid_price:.2f}")

# Multiple symbols
quotes = helper.get_latest_quotes(["SPY", "QQQ", "IWM"])
for symbol, quote in quotes.items():
    print(f"{symbol}: ${quote.bid_price} / ${quote.ask_price}")
```

#### Latest Bar

```python
bar = helper.get_latest_bar("SPY")
print(f"Close: ${bar.close:.2f}")
print(f"Volume: {bar.volume:,}")
print(f"VWAP: ${bar.vwap:.2f}")
```

#### Latest Trade

```python
trade = helper.get_latest_trade("SPY")
print(f"Price: ${trade.price:.2f}")
print(f"Size: {trade.size}")
print(f"Time: {trade.timestamp}")
```

### Historical Bars (OHLCV)

Get historical bar data with simple timeframe strings.

```python
# Last 5 days of hourly bars
bars = helper.get_bars("SPY", timeframe="1H", days_back=5)

# Specific date range
from datetime import datetime, timedelta

end = datetime.now()
start = end - timedelta(days=30)

bars = helper.get_bars(
    "SPY",
    timeframe="1D",
    start=start,
    end=end
)

# With limit
bars = helper.get_bars("SPY", timeframe="5Min", days_back=1, limit=100)

# Access bar data
for bar in bars:
    print(f"{bar.timestamp}")
    print(f"  O: ${bar.open:.2f}")
    print(f"  H: ${bar.high:.2f}")
    print(f"  L: ${bar.low:.2f}")
    print(f"  C: ${bar.close:.2f}")
    print(f"  V: {bar.volume:,}")
```

### Historical Quotes

Get historical bid/ask quotes.

```python
# Last 100 quotes from past day
quotes = helper.get_quotes("SPY", days_back=1, limit=100)

for quote in quotes:
    spread = quote.ask_price - quote.bid_price
    print(f"{quote.timestamp}: ${quote.bid_price} / ${quote.ask_price} "
          f"(spread: ${spread:.2f})")
```

### Historical Trades

Get historical trade (tick) data.

```python
# Last 100 trades from past day
trades = helper.get_trades("SPY", days_back=1, limit=100)

for trade in trades:
    print(f"{trade.timestamp}: ${trade.price:.2f} x {trade.size}")
```

### Snapshots

Get a snapshot with latest bar, quote, and trade all in one call.

```python
# Single symbol
snapshot = helper.get_snapshot("SPY")

if snapshot.latest_quote:
    print(f"Latest Quote: ${snapshot.latest_quote.bid_price} / "
          f"${snapshot.latest_quote.ask_price}")

if snapshot.latest_trade:
    print(f"Latest Trade: ${snapshot.latest_trade.price:.2f}")

if snapshot.latest_bar:
    print(f"Latest Bar Close: ${snapshot.latest_bar.close:.2f}")

if snapshot.prev_daily_bar:
    # Calculate daily change
    change_pct = (
        (snapshot.latest_bar.close - snapshot.prev_daily_bar.close)
        / snapshot.prev_daily_bar.close * 100
    )
    print(f"Daily Change: {change_pct:+.2f}%")
```

### Multi-Symbol Support

Many methods support fetching data for multiple symbols at once.

```python
# Multiple quotes
quotes = helper.get_latest_quotes(["SPY", "QQQ", "IWM", "DIA"])

# Multiple bars
bars_dict = helper.get_bars_multi(
    ["SPY", "QQQ", "IWM"],
    timeframe="1H",
    days_back=5
)

for symbol, bars in bars_dict.items():
    latest = bars[-1]
    print(f"{symbol}: {len(bars)} bars, latest ${latest.close:.2f}")

# Multiple snapshots
snapshots = helper.get_snapshots(["SPY", "QQQ", "IWM"])
for symbol, snapshot in snapshots.items():
    if snapshot.latest_quote:
        print(f"{symbol}: ${snapshot.latest_quote.bid_price}")
```

## Timeframes

StockHelper supports simple timeframe strings instead of complex TimeFrame objects.

### Supported Formats

| Format | Description | Example |
|--------|-------------|---------|
| `1Min`, `5Min`, `15Min` | Minutes | `"5Min"` = 5-minute bars |
| `1H`, `1Hour`, `4H` | Hours | `"1H"` = 1-hour bars |
| `1D`, `1Day` | Days | `"1D"` = daily bars |
| `1W`, `1Week` | Weeks | `"1W"` = weekly bars |
| `1M`, `1Month` | Months | `"1M"` = monthly bars |

### Examples

```python
# 5-minute bars
bars = helper.get_bars("SPY", timeframe="5Min", days_back=1)

# Hourly bars
bars = helper.get_bars("SPY", timeframe="1H", days_back=5)

# Daily bars
bars = helper.get_bars("SPY", timeframe="1D", days_back=30)

# Weekly bars
bars = helper.get_bars("SPY", timeframe="1W", days_back=90)
```

## Data Models

StockHelper returns clean dataclass objects with Python native types (float, int) instead of strings.

### BarData

```python
@dataclass
class BarData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    trade_count: Optional[int]
    vwap: Optional[float]
```

### QuoteData

```python
@dataclass
class QuoteData:
    symbol: str
    timestamp: datetime
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int
    conditions: Optional[List[str]]
```

### TradeData

```python
@dataclass
class TradeData:
    symbol: str
    timestamp: datetime
    price: float
    size: int
    conditions: Optional[List[str]]
    exchange: Optional[str]
```

### SnapshotData

```python
@dataclass
class SnapshotData:
    symbol: str
    latest_trade: Optional[TradeData]
    latest_quote: Optional[QuoteData]
    latest_bar: Optional[BarData]
    prev_daily_bar: Optional[BarData]
```

## Examples

### Example 1: Price Monitor

```python
from alpaca.data.stock_helper import StockHelper

helper = StockHelper()

symbols = ["SPY", "QQQ", "IWM", "DIA"]
snapshots = helper.get_snapshots(symbols)

print("Current Prices:")
for symbol, snapshot in snapshots.items():
    if snapshot.latest_quote:
        midpoint = (snapshot.latest_quote.bid_price + 
                   snapshot.latest_quote.ask_price) / 2
        print(f"{symbol}: ${midpoint:.2f}")
```

### Example 2: Daily Movers

```python
from alpaca.data.stock_helper import StockHelper

helper = StockHelper()

symbols = ["SPY", "QQQ", "IWM", "DIA", "AAPL", "MSFT", "GOOGL"]
snapshots = helper.get_snapshots(symbols)

movers = []
for symbol, snapshot in snapshots.items():
    if snapshot.latest_bar and snapshot.prev_daily_bar:
        change_pct = (
            (snapshot.latest_bar.close - snapshot.prev_daily_bar.close)
            / snapshot.prev_daily_bar.close * 100
        )
        movers.append((symbol, change_pct))

# Sort by absolute change
movers.sort(key=lambda x: abs(x[1]), reverse=True)

print("Top Movers:")
for symbol, change in movers[:5]:
    print(f"{symbol}: {change:+.2f}%")
```

### Example 3: Volume Analysis

```python
from alpaca.data.stock_helper import StockHelper

helper = StockHelper()

# Get last 20 days of daily bars
bars = helper.get_bars("SPY", timeframe="1D", days_back=20)

# Calculate average volume
avg_volume = sum(bar.volume for bar in bars) / len(bars)

# Check latest volume
latest = bars[-1]
volume_ratio = latest.volume / avg_volume

print(f"Average Volume: {avg_volume:,.0f}")
print(f"Latest Volume:  {latest.volume:,}")
print(f"Ratio: {volume_ratio:.2f}x")

if volume_ratio > 1.5:
    print("⚠️ High volume alert!")
```

### Example 4: Multi-Timeframe Analysis

```python
from alpaca.data.stock_helper import StockHelper

helper = StockHelper()

symbol = "SPY"

# Get data at different timeframes
daily_bars = helper.get_bars(symbol, timeframe="1D", days_back=5)
hourly_bars = helper.get_bars(symbol, timeframe="1H", days_back=5)
minute_bars = helper.get_bars(symbol, timeframe="5Min", days_back=1)

print(f"Daily trend: {len(daily_bars)} bars")
print(f"Hourly trend: {len(hourly_bars)} bars")
print(f"Intraday: {len(minute_bars)} bars")

# Calculate returns at each timeframe
for name, bars in [("Daily", daily_bars), ("Hourly", hourly_bars)]:
    if len(bars) >= 2:
        returns = ((bars[-1].close - bars[0].open) / bars[0].open * 100)
        print(f"{name} return: {returns:+.2f}%")
```

## Migration Guide

### From Standard StockHistoricalDataClient

**Before (Standard API):**

```python
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

# Complex setup
client = StockHistoricalDataClient(api_key="...", secret_key="...")

# Get bars - multiple steps
request = StockBarsRequest(
    symbol_or_symbols="SPY",
    timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Hour),
    start=datetime.now() - timedelta(days=5)
)
response = client.get_stock_bars(request)

# Extract and convert data
bars = []
for bar in response.data["SPY"]:
    bars.append({
        'timestamp': bar.timestamp,
        'close': float(bar.close),
        'volume': int(bar.volume)
    })

# Get latest quote - separate call
quote_request = StockLatestQuoteRequest(symbol_or_symbols="SPY")
quote_response = client.get_stock_latest_quote(quote_request)
quote = quote_response["SPY"]
bid = float(quote.bid_price)
ask = float(quote.ask_price)
```

**After (StockHelper):**

```python
from alpaca.data.stock_helper import StockHelper

# Simple setup
helper = StockHelper()  # Auto-loads from env

# Get bars - one line
bars = helper.get_bars("SPY", timeframe="1H", days_back=5)

# Data already in clean format
for bar in bars:
    print(f"{bar.timestamp}: ${bar.close}, Vol: {bar.volume}")

# Get latest quote - one line
quote = helper.get_latest_quote("SPY")
print(f"${quote.bid_price} / ${quote.ask_price}")
```

### Key Differences

1. **Environment Variables**: Automatic credential loading
2. **Simple Timeframes**: `"1H"` instead of `TimeFrame(1, TimeFrameUnit.Hour)`
3. **Clean Returns**: Dataclasses with float/int types, not strings
4. **days_back Parameter**: Simplified date range specification
5. **Multi-Symbol**: Built-in support with `_multi` methods

## See Also

- [OptionHelper Documentation](./simplified_option_api.md) - Simplified option data API
- [TradingHelper Documentation](./simplified_trading_api.md) - Simplified trading API
- [Standard Data API](../docs/market_data.rst) - Full market data API documentation
- [Alpaca API Docs](https://alpaca.markets/docs/) - Official Alpaca documentation
