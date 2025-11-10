# Alpaca-py Simplified

[![Python Versions](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/JimCollinsDC/alpaca-py-simplified?color=blue&style=for-the-badge)](LICENSE)
[![Code Quality](https://img.shields.io/badge/code%20style-flake8-brightgreen?style=for-the-badge)](https://flake8.pycqa.org)
[![Tests Passing](https://img.shields.io/badge/tests-159%20passing-success?style=for-the-badge&logo=pytest)](https://github.com/JimCollinsDC/alpaca-py-simplified)

[![GitHub Stars](https://img.shields.io/github/stars/JimCollinsDC/alpaca-py-simplified?style=social)](https://github.com/JimCollinsDC/alpaca-py-simplified/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/JimCollinsDC/alpaca-py-simplified?style=social)](https://github.com/JimCollinsDC/alpaca-py-simplified/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/JimCollinsDC/alpaca-py-simplified?style=flat-square)](https://github.com/JimCollinsDC/alpaca-py-simplified/issues)

**A dramatically simplified Python SDK for Alpaca's trading and market data APIs**

Built on top of the official [alpaca-py](https://github.com/alpacahq/alpaca-py) SDK, this fork adds 6 powerful helper classes that eliminate 60-70% of boilerplate code. Get trading faster with intuitive APIs, automatic credential loading, and clean dataclass responses.

## Why Use This Fork?

**Before** (Official SDK):

```python
# Complex: Multiple clients, request objects, manual date handling
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

client = StockHistoricalDataClient(api_key="...", secret_key="...")
request = StockBarsRequest(
    symbol_or_symbols="SPY",
    timeframe=TimeFrame(1, TimeFrameUnit.Hour),
    start=datetime.now() - timedelta(days=5),
    end=datetime.now()
)
bars = client.get_stock_bars(request)
```

**After** (This Fork):

```python
# Simple: One import, clean methods, automatic date handling
from alpaca.data.stock_helper import StockHelper

data = StockHelper()  # Auto-loads credentials from .env
bars = data.get_bars("SPY", timeframe="1H", days_back=5)
```

## Features

### 🚀 Six Powerful Helper Classes

1. **[OptionHelper](docs/simplified_option_api.md)** - Complete option data with greeks, IV, and bid/ask spreads
2. **[TradingHelper](docs/simplified_trading_api.md)** - Order placement, bracket orders, position management
3. **[StockHelper](docs/simplified_stock_data_api.md)** - Stock market data with simple timeframe strings
4. **[CryptoHelper](docs/simplified_crypto_data_api.md)** - Cryptocurrency data (BTC/USD, ETH/USD, etc.)
5. **[AccountHelper](docs/simplified_account_api.md)** - Account info, balances, PDT tracking, portfolio history
6. **[NewsHelper](docs/simplified_news_api.md)** - Financial news articles and breaking news alerts

### ✨ Key Improvements

- **🔐 Automatic Credentials** - Loads from `.env` file automatically
- **📅 Simple Date Handling** - Use `days_back=7` instead of datetime objects
- **🎯 Native Python Types** - Returns `float` and `int` instead of strings
- **📦 Clean Dataclasses** - Easy-to-use response objects
- **🧪 Fully Tested** - 159 passing tests with comprehensive coverage
- **📚 Complete Documentation** - Examples and API references for all helpers

## Installation

### Using pip

```bash
pip install git+https://github.com/JimCollinsDC/alpaca-py-simplified.git
```

### Using uv (recommended)

```bash
uv add git+https://github.com/JimCollinsDC/alpaca-py-simplified.git
```

### Setup Environment Variables

Create a `.env` file in your project root:

```bash
APCA_API_KEY_ID=your_api_key_here
APCA_API_SECRET_KEY=your_secret_key_here
```

## Quick Start

```python
# Option Data - Get complete option info in one call
from alpaca.data.option_helper import OptionHelper

helper = OptionHelper()  # Auto-loads from .env
option = helper.get_option("SPY250117C00550000")
print(f"Strike: ${option.strike}, IV: {option.implied_volatility:.2%}")

# Stock Data - Get market data with simple timeframes
from alpaca.data.stock_helper import StockHelper

data = StockHelper()  # Auto-loads from .env
bars = data.get_bars("SPY", timeframe="1H", days_back=5)
quote = data.get_latest_quote("SPY")

# Crypto Data - Get cryptocurrency market data
from alpaca.data.crypto_helper import CryptoHelper

crypto = CryptoHelper()  # Auto-loads from .env
btc_bars = crypto.get_bars("BTC/USD", timeframe="1H", days_back=7)
btc_quote = crypto.get_latest_quote("BTC/USD")

# Account Management - Check balances and PDT status
from alpaca.trading.account_helper import AccountHelper

account = AccountHelper()  # Auto-loads from .env
print(f"Cash: ${account.get_cash():,.2f}")
print(f"Buying Power: ${account.get_buying_power():,.2f}")
print(f"Day Trades Remaining: {account.get_day_trades_remaining()}")

# News - Get financial news articles
from alpaca.data.news_helper import NewsHelper

news = NewsHelper()  # Auto-loads from .env
articles = news.get_news_for_symbol("AAPL", days_back=7)
for article in articles[:3]:
    print(f"{article.headline} - {article.source}")

# Trading - Place orders with ease
from alpaca.trading.trading_helper import TradingHelper

trader = TradingHelper()  # Auto-loads from .env
order = trader.buy_with_bracket(
    "SPY", qty=10, stop_loss=450.00, take_profit=550.00
)
```

## Documentation

### Simplified Helper Documentation

- [OptionHelper API Reference](docs/simplified_option_api.md)
- [TradingHelper API Reference](docs/simplified_trading_api.md)
- [StockHelper API Reference](docs/simplified_stock_data_api.md)
- [CryptoHelper API Reference](docs/simplified_crypto_data_api.md)
- [AccountHelper API Reference](docs/simplified_account_api.md)
- [NewsHelper API Reference](docs/simplified_news_api.md)

### Original SDK Documentation

This fork includes all functionality from the official alpaca-py SDK. For documentation on the underlying SDK:

- [Official Alpaca Python SDK Docs](https://alpaca.markets/sdks/python/getting_started.html)
- [Alpaca API Reference](https://docs.alpaca.markets/reference)

## Examples

Check out the `examples/` directory for complete working examples:

- `examples/trading_helper_example.py` - Order placement and position management
- `examples/stock_helper_example.py` - Stock market data retrieval
- `examples/crypto_helper_example.py` - Cryptocurrency data access
- `examples/account_helper_example.py` - Account management and PDT tracking
- `examples/news_helper_example.py` - Financial news retrieval

## API Keys

### Getting API Keys

You'll need Alpaca API keys to use this SDK:

1. **Paper Trading** (Free):
   - Sign up at [Alpaca](https://alpaca.markets)
   - Get paper trading keys from your dashboard
   - Perfect for testing and development

2. **Live Trading**:
   - Complete Alpaca account verification
   - Enable live trading
   - Get live trading keys (keep these secure!)

### Storing API Keys

**Best Practice** - Use environment variables:

```bash
# .env file (never commit this!)
APCA_API_KEY_ID=your_api_key_here
APCA_API_SECRET_KEY=your_secret_key_here
```

All helpers automatically load from these environment variables.

## What's Included from Original SDK

This fork maintains 100% compatibility with the original alpaca-py SDK, including:

- **Broker API** - For building investment apps
- **Trading API** - Direct order placement and account management
- **Market Data API** - Stocks, options, crypto, and news data
- **WebSocket Streaming** - Real-time market data
- **All Request/Response Models** - Full OOP design

The simplified helpers are built **on top** of the original SDK, so you can use both approaches in the same project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/JimCollinsDC/alpaca-py-simplified.git
cd alpaca-py-simplified

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
uv sync --all-extras --group dev

# Run tests
uv run pytest

# Run linting
uv run flake8 alpaca/ tests/
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

This is a fork of the official [alpaca-py](https://github.com/alpacahq/alpaca-py) project. All credit for the original SDK goes to Alpaca Markets and its contributors.

## Acknowledgments

- Built on top of [alpaca-py](https://github.com/alpacahq/alpaca-py) by Alpaca Markets
- Uses [uv](https://github.com/astral-sh/uv) for fast dependency management
- Inspired by the need for simpler, more Pythonic APIs

---

**Note**: This is an independent fork and is not officially affiliated with or endorsed by Alpaca Markets, Inc.
