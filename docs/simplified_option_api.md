# Simplified Option Data API

A much easier way to get option data from Alpaca.

## Quick Start

```python
# 1. Install dependencies
pip install alpaca-py python-dotenv

# 2. Set up your .env file with your Alpaca API keys
# ALPACA_API_KEY=your_key_here
# ALPACA_SECRET_KEY=your_secret_here

# 3. Use the simplified API
from dotenv import load_dotenv
from alpaca.data import OptionHelper

load_dotenv()
options = OptionHelper()  # Reads from environment variables

# Get complete option data with one call
data = options.get_option("AAPL250117C00150000")
print(f"Strike: ${data.strike}, Bid: ${data.bid}, Delta: {data.delta:.3f}")
```

## The Problem

The original API requires multiple clients and multiple calls to get complete option information:

```python
# OLD WAY - Complex! 😫
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionSnapshotRequest

client = OptionHistoricalDataClient(api_key="...", secret_key="...")
request = OptionSnapshotRequest(symbol_or_symbols="AAPL250117C00150000")
snapshots = client.get_option_snapshot(request)
snapshot = snapshots["AAPL250117C00150000"]

# Now extract what you need...
bid = snapshot.latest_quote.bid_price if snapshot.latest_quote else None
ask = snapshot.latest_quote.ask_price if snapshot.latest_quote else None
delta = snapshot.greeks.delta if snapshot.greeks else None
iv = snapshot.implied_volatility
# And so on...
```

## The Solution

The new `OptionHelper` provides everything in one simple call:

```python
# NEW WAY - Simple! ✨
from dotenv import load_dotenv
from alpaca.data import OptionHelper

load_dotenv()
options = OptionHelper()  # Automatically reads ALPACA_API_KEY and ALPACA_SECRET_KEY

data = options.get_option("AAPL250117C00150000")

# All data is readily available
print(f"Strike: ${data.strike}")
print(f"Bid/Ask: ${data.bid}/${data.ask}")
print(f"Delta: {data.delta}")
print(f"IV: {data.implied_volatility:.2%}")
print(f"Volume: {data.volume}")
```

## Configuration

### Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_PAPER=True  # Optional: Use paper trading (default: False)
```

Then use `load_dotenv()`:

```python
from dotenv import load_dotenv
from alpaca.data import OptionHelper

load_dotenv()
options = OptionHelper()  # Reads from environment variables
```

### Direct Initialization

You can also pass keys directly:

```python
from alpaca.data import OptionHelper

options = OptionHelper(api_key="your_key", secret_key="your_secret")
```

## Features

### Single Option Lookup

```python
from alpaca.data import OptionHelper

options = OptionHelper()  # Uses env vars

# Get complete option data with one call
data = options.get_option("AAPL250117C00150000")

# Access all properties
print(data.symbol)              # "AAPL250117C00150000"
print(data.strike)              # 150.0
print(data.expiration)          # datetime(2025, 1, 17)
print(data.option_type)         # "call"
print(data.bid)                 # 12.50
print(data.ask)                 # 12.75
print(data.mid)                 # 12.625
print(data.delta)               # 0.6234
print(data.implied_volatility)  # 0.2845
```

### Multiple Options

```python
# Get multiple options at once
symbols = [
    "AAPL250117C00150000",
    "AAPL250117C00155000",
    "AAPL250117P00150000"
]

data_list = options.get_options(symbols)

for data in data_list:
    print(f"{data.symbol}: Bid=${data.bid}, Delta={data.delta:.3f}")
```

### Option Chain

```python
from datetime import datetime

# Get entire option chain for a specific expiration
expiration = datetime(2025, 1, 17)
chain = options.get_option_chain("AAPL", expiration=expiration)

print(f"Found {len(chain)} options")

# Filter for what you want
atm_calls = [
    opt for opt in chain
    if opt.option_type == "call" and 0.45 < opt.delta < 0.55
]
```

## Available Data

The `OptionData` object includes:

**Basic Info:**
- `symbol` - Option contract symbol
- `strike` - Strike price
- `expiration` - Expiration date
- `option_type` - "call" or "put"

**Pricing:**
- `bid` - Current bid price
- `ask` - Current ask price  
- `mid` - Mid price (bid + ask) / 2
- `last_price` - Last trade price

**Greeks:**
- `delta` - Delta
- `gamma` - Gamma
- `theta` - Theta
- `vega` - Vega
- `rho` - Rho

**Volume & Interest:**
- `volume` - Trading volume
- `open_interest` - Open interest

**Volatility:**
- `implied_volatility` - IV

**Additional:**
- `bid_size` - Bid size
- `ask_size` - Ask size
- `last_size` - Last trade size
- `timestamp` - Data timestamp

## Real-World Examples

### Find Options to Trade

```python
from datetime import datetime

options = OptionHelper(api_key="...", secret_key="...")

# Get option chain
exp = datetime(2025, 2, 21)
chain = options.get_option_chain("SPY", expiration=exp)

# Find liquid, ATM puts with high IV
candidates = [
    opt for opt in chain
    if (
        opt.option_type == "put"
        and abs(opt.delta) > 0.4
        and opt.implied_volatility > 0.20
        and opt.bid and opt.ask
        and (opt.ask - opt.bid) < 0.50  # Tight spread
    )
]

# Sort by IV
candidates.sort(key=lambda x: x.implied_volatility, reverse=True)

# Show top candidates
for opt in candidates[:5]:
    print(f"Strike ${opt.strike}: IV={opt.implied_volatility:.2%}, Delta={opt.delta:.3f}")
```

### Compare Strikes

```python
# Compare different strikes
strikes = [145, 150, 155, 160]
symbols = [f"AAPL250117C{strike*1000:08d}" for strike in strikes]

data_list = options.get_options(symbols)

print("Strike  |  Bid   |  Delta  |   IV")
print("--------|--------|---------|--------")
for data in data_list:
    print(f"${data.strike:6.0f} | ${data.bid:6.2f} | {data.delta:7.4f} | {data.implied_volatility:6.2%}")
```

## Installation

This is included in the alpaca-py package:

```bash
uv add alpaca-py
```

## Migration Guide

### Before (Old Way)

```python
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionSnapshotRequest, OptionLatestQuoteRequest

client = OptionHistoricalDataClient(api_key="...", secret_key="...")

# Get quote
quote_req = OptionLatestQuoteRequest(symbol_or_symbols="AAPL250117C00150000")
quotes = client.get_option_latest_quote(quote_req)
bid = quotes["AAPL250117C00150000"].bid_price

# Get snapshot for greeks
snap_req = OptionSnapshotRequest(symbol_or_symbols="AAPL250117C00150000")
snaps = client.get_option_snapshot(snap_req)
delta = snaps["AAPL250117C00150000"].greeks.delta
```

### After (New Way)

```python
from alpaca.data import OptionHelper

options = OptionHelper(api_key="...", secret_key="...")
data = options.get_option("AAPL250117C00150000")

bid = data.bid
delta = data.delta
```

**Result: 10 lines → 4 lines, much clearer!**

## Backward Compatibility

The original API still works. This is a convenience wrapper that doesn't break existing code.

## See Also

- [Full Example](../examples/option_helper_example.py)
- [Original Option Client](../alpaca/data/historical/option.py)
