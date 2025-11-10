# Simplified Crypto Data API

The `CryptoHelper` class provides a clean, simple interface for fetching cryptocurrency market data from Alpaca. It eliminates the complexity of working with multiple request classes and provides intuitive methods with Python native types.

## Quick Start

```python
from alpaca.data.crypto_helper import CryptoHelper

# Initialize (auto-loads from environment variables)
helper = CryptoHelper()

# Get latest quote
quote = helper.get_latest_quote("BTC/USD")
print(f"BTC: ${quote.ask_price:,.2f}")

# Get hourly bars for the past 7 days
bars = helper.get_bars("BTC/USD", timeframe="1H", days_back=7)
for bar in bars:
    print(f"{bar.timestamp}: ${bar.close:,.2f}")
```

## Configuration

### Environment Variables

The `CryptoHelper` automatically loads credentials from environment variables:

```bash
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

### Explicit Credentials

You can also provide credentials explicitly:

```python
helper = CryptoHelper(
    api_key="your_api_key",
    secret_key="your_secret_key"
)
```

### Note on Authentication

Alpaca's cryptocurrency data does not require authentication, but authenticating increases your data rate limit. It's recommended to provide API keys for production applications.

## Features

### Latest Data (Real-time)

Get the most recent market data for cryptocurrencies.

#### Latest Quote

```python
quote = helper.get_latest_quote("BTC/USD")
print(f"Bid: ${quote.bid_price:,.2f} x {quote.bid_size}")
print(f"Ask: ${quote.ask_price:,.2f} x {quote.ask_size}")
```

#### Latest Bar (Minute)

```python
bar = helper.get_latest_bar("ETH/USD")
print(f"Close: ${bar.close:,.2f}")
print(f"Volume: {bar.volume} ETH")
```

#### Latest Trade

```python
trade = helper.get_latest_trade("BTC/USD")
print(f"Price: ${trade.price:,.2f}")
print(f"Size: {trade.size} BTC")
print(f"Side: {trade.taker_side}")
```

### Historical Bars (OHLCV)

Get historical price bars with simple timeframe strings.

#### Single Symbol

```python
# Get daily bars for the past 30 days
bars = helper.get_bars("BTC/USD", timeframe="1D", days_back=30)

# Get hourly bars with explicit dates
from datetime import datetime
bars = helper.get_bars(
    "ETH/USD",
    timeframe="1H",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 7)
)

# Limit number of bars
bars = helper.get_bars("BTC/USD", timeframe="1H", limit=100)
```

#### Multiple Symbols

```python
bars_dict = helper.get_bars_multi(
    ["BTC/USD", "ETH/USD", "SOL/USD"],
    timeframe="1D",
    days_back=7
)

for symbol, bars in bars_dict.items():
    print(f"{symbol}: {len(bars)} bars")
```

### Historical Trades

Get tick-by-tick trade data.

```python
# Get trades from the past day
trades = helper.get_trades("BTC/USD", days_back=1, limit=100)
for trade in trades:
    print(f"{trade.timestamp}: ${trade.price:,.2f} x {trade.size}")
```

### Snapshots

Get a complete snapshot of latest market data in one call.

#### Single Symbol

```python
snapshot = helper.get_snapshot("BTC/USD")
print(f"Latest quote: ${snapshot.latest_quote.ask_price:,.2f}")
print(f"Latest trade: ${snapshot.latest_trade.price:,.2f}")
print(f"Latest bar: ${snapshot.latest_bar.close:,.2f}")
print(f"Prev daily: ${snapshot.prev_daily_bar.close:,.2f}")
```

#### Multiple Symbols

```python
snapshots = helper.get_snapshots(["BTC/USD", "ETH/USD", "DOGE/USD"])
for symbol, snap in snapshots.items():
    if snap.latest_bar:
        print(f"{symbol}: ${snap.latest_bar.close:,.2f}")
```

## Timeframes

CryptoHelper supports simple timeframe strings instead of complex `TimeFrame` objects:

| String | Description |
|--------|-------------|
| `"1Min"`, `"5Min"`, `"15Min"` | Minute bars (1, 5, or 15 minutes) |
| `"1H"`, `"4H"` | Hour bars (1 or 4 hours) |
| `"1D"` | Daily bars |
| `"1W"` | Weekly bars |
| `"1M"` | Monthly bars |

You can also use longer forms like `"1Hour"`, `"1Day"`, etc.

## Data Models

All data is returned as clean dataclasses with Python native types (no string conversion needed).

### CryptoBarData

```python
@dataclass
class CryptoBarData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float  # Volume in crypto (e.g., BTC, not USD)
    trade_count: Optional[int]
    vwap: Optional[float]  # Volume-weighted average price
```

### CryptoQuoteData

```python
@dataclass
class CryptoQuoteData:
    symbol: str
    timestamp: datetime
    bid_price: float
    bid_size: float  # Size in crypto
    ask_price: float
    ask_size: float  # Size in crypto
```

### CryptoTradeData

```python
@dataclass
class CryptoTradeData:
    symbol: str
    timestamp: datetime
    price: float
    size: float  # Size in crypto
    taker_side: Optional[str]  # "buy" or "sell"
```

### CryptoSnapshotData

```python
@dataclass
class CryptoSnapshotData:
    symbol: str
    latest_trade: Optional[CryptoTradeData]
    latest_quote: Optional[CryptoQuoteData]
    latest_bar: Optional[CryptoBarData]  # Latest minute bar
    prev_daily_bar: Optional[CryptoBarData]  # Previous day's bar
```

## Examples

### Example 1: Price Monitor

Monitor real-time prices for multiple cryptocurrencies.

```python
from alpaca.data.crypto_helper import CryptoHelper
import time

helper = CryptoHelper()
symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]

while True:
    quotes = helper.get_latest_quotes(symbols)
    
    print("\nCrypto Prices:")
    for symbol, quote in quotes.items():
        mid = (quote.bid_price + quote.ask_price) / 2
        spread = quote.ask_price - quote.bid_price
        print(f"{symbol:10} ${mid:>10,.2f}  Spread: ${spread:>6,.2f}")
    
    time.sleep(10)  # Update every 10 seconds
```

### Example 2: Daily Movers

Find the biggest gainers and losers over the past 24 hours.

```python
from alpaca.data.crypto_helper import CryptoHelper

helper = CryptoHelper()
symbols = ["BTC/USD", "ETH/USD", "SOL/USD", "AVAX/USD", "DOGE/USD"]

bars_dict = helper.get_bars_multi(symbols, timeframe="1D", days_back=2)

movers = []
for symbol, bars in bars_dict.items():
    if len(bars) >= 2:
        prev_close = bars[-2].close
        curr_close = bars[-1].close
        change_pct = ((curr_close - prev_close) / prev_close) * 100
        movers.append((symbol, change_pct, curr_close))

# Sort by absolute change
movers.sort(key=lambda x: abs(x[1]), reverse=True)

print("Top Movers (24h):")
for symbol, change, price in movers:
    direction = "▲" if change >= 0 else "▼"
    print(f"{symbol:10} {direction} {change:>+7.2f}%  ${price:>10,.2f}")
```

### Example 3: Volume Analysis

Analyze trading volume patterns.

```python
from alpaca.data.crypto_helper import CryptoHelper

helper = CryptoHelper()

# Get hourly bars for the past 7 days
bars = helper.get_bars("BTC/USD", timeframe="1H", days_back=7)

# Calculate average volume
total_volume = sum(bar.volume for bar in bars)
avg_volume = total_volume / len(bars)

# Find high volume periods
high_volume_bars = [
    bar for bar in bars
    if bar.volume > avg_volume * 1.5
]

print(f"Average hourly volume: {avg_volume:.2f} BTC")
print(f"High volume periods: {len(high_volume_bars)}")

for bar in high_volume_bars[:5]:  # Show first 5
    pct_above = ((bar.volume / avg_volume) - 1) * 100
    print(
        f"{bar.timestamp.strftime('%Y-%m-%d %H:%M')} | "
        f"Volume: {bar.volume:>8.2f} BTC "
        f"({pct_above:>+5.1f}% above avg)"
    )
```

### Example 4: Multi-Timeframe Analysis

Analyze the same asset across different timeframes.

```python
from alpaca.data.crypto_helper import CryptoHelper

helper = CryptoHelper()

timeframes = ["1H", "4H", "1D"]
symbol = "BTC/USD"

print(f"Multi-Timeframe Analysis for {symbol}:\n")

for tf in timeframes:
    bars = helper.get_bars(symbol, timeframe=tf, days_back=7)
    
    if len(bars) >= 2:
        first = bars[0]
        last = bars[-1]
        change = last.close - first.open
        change_pct = (change / first.open) * 100
        
        # Calculate volatility (high-low range)
        avg_range = sum(bar.high - bar.low for bar in bars) / len(bars)
        volatility_pct = (avg_range / last.close) * 100
        
        print(f"{tf:4} Timeframe:")
        print(f"  Bars: {len(bars)}")
        print(f"  Change: {change_pct:>+7.2f}%")
        print(f"  Avg Range: ${avg_range:,.2f}")
        print(f"  Volatility: {volatility_pct:.2f}%")
        print()
```

## Migration from Original API

### Old Way (Complex)

```python
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import (
    CryptoBarsRequest,
    CryptoLatestQuoteRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

# Lots of setup
client = CryptoHistoricalDataClient(
    api_key="...",
    secret_key="..."
)

# Complex timeframe object
tf = TimeFrame(amount=1, unit=TimeFrameUnit.Hour)

# Complex request object
request = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD",
    timeframe=tf,
    start=datetime.now() - timedelta(days=7),
    end=datetime.now()
)

# Get data
response = client.get_crypto_bars(request)
bars = response["BTC/USD"]

# Convert strings to numbers
for bar in bars:
    close_price = float(bar.close)  # String!
    volume = float(bar.volume)      # String!
    print(f"Close: ${close_price:,.2f}")

# Latest quote
quote_request = CryptoLatestQuoteRequest(symbol_or_symbols="BTC/USD")
quote_response = client.get_crypto_latest_quote(quote_request)
quote = quote_response["BTC/USD"]
ask = float(quote.ask_price)  # Convert string
```

### New Way (Simple)

```python
from alpaca.data.crypto_helper import CryptoHelper

# Simple initialization (auto-loads from env)
helper = CryptoHelper()

# Simple timeframe string and automatic date calculation
bars = helper.get_bars("BTC/USD", timeframe="1H", days_back=7)

# Already native Python types!
for bar in bars:
    print(f"Close: ${bar.close:,.2f}")  # Already a float!

# Latest quote - one line
quote = helper.get_latest_quote("BTC/USD")
print(f"Ask: ${quote.ask_price:,.2f}")  # Already a float!
```

## Complete API Reference

### Initialization

```python
CryptoHelper(
    api_key: Optional[str] = None,      # Auto-loads from ALPACA_API_KEY
    secret_key: Optional[str] = None,   # Auto-loads from ALPACA_SECRET_KEY
)
```

### Latest Data Methods

```python
# Latest quote (bid/ask)
get_latest_quote(symbol: str) -> Optional[CryptoQuoteData]
get_latest_quotes(symbols: List[str]) -> Dict[str, CryptoQuoteData]

# Latest bar (OHLCV)
get_latest_bar(symbol: str) -> Optional[CryptoBarData]

# Latest trade
get_latest_trade(symbol: str) -> Optional[CryptoTradeData]
```

### Historical Data Methods

```python
# Historical bars
get_bars(
    symbol: str,
    timeframe: str = "1D",              # "1Min", "1H", "1D", etc.
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    days_back: Optional[int] = None,    # Alternative to start/end
    limit: Optional[int] = None,
) -> List[CryptoBarData]

# Multi-symbol bars
get_bars_multi(
    symbols: List[str],
    timeframe: str = "1D",
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    days_back: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, List[CryptoBarData]]

# Historical trades
get_trades(
    symbol: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    days_back: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[CryptoTradeData]
```

### Snapshot Methods

```python
# Complete market snapshot
get_snapshot(symbol: str) -> Optional[CryptoSnapshotData]
get_snapshots(symbols: List[str]) -> Dict[str, CryptoSnapshotData]
```

## Key Benefits

✅ **Simple timeframe strings** - Use `"1H"` instead of `TimeFrame(1, TimeFrameUnit.Hour)`

✅ **Automatic date calculation** - `days_back=7` instead of manual `datetime` math

✅ **Native Python types** - Prices and sizes are `float`, no string conversion needed

✅ **No request objects** - Direct method calls with named parameters

✅ **Environment variables** - Auto-loads API keys from `.env` file

✅ **Multi-symbol support** - Built-in methods for fetching multiple symbols

✅ **Clean dataclasses** - Type-safe data models with clear field names

✅ **Consistent API** - Same patterns across stocks, options, and crypto

## See Also

- [Simplified Option Data API](simplified_option_api.md)
- [Simplified Trading API](simplified_trading_api.md)
- [Simplified Stock Data API](simplified_stock_data_api.md)
- [Examples Directory](../examples/)
