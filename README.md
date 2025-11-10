[![Alpaca-py](https://github.com/alpacahq/alpaca-py/blob/master/docs/images/alpaca-py-banner.png?raw=true)](https://alpaca.markets/docs/python-sdk)

[![Downloads](https://pepy.tech/badge/alpaca-py/month)](https://pepy.tech/project/alpaca-py)
[![Python Versions](https://img.shields.io/pypi/pyversions/alpaca-py.svg?logo=python&logoColor=white)](https://pypi.org/project/alpaca-py)
[![GitHub](https://img.shields.io/github/license/alpacahq/alpaca-py?color=blue)](https://github.com/alpacahq/alpaca-py/blob/master/LICENSE.md)
[![PyPI](https://img.shields.io/pypi/v/alpaca-py?color=blue)](https://pypi.org/project/alpaca-py/)

> **Note:** This is a modified version of the official [alpaca-py](https://github.com/alpacahq/alpaca-py) repository with additional features and improvements:
> - **Simplified OptionHelper API** - Get complete option data with a single call
> - **Environment variable support** - Secure API key management with python-dotenv
> - **Enhanced code quality** - Flake8 compliant with comprehensive test coverage
> - **Additional documentation** - Examples and guides for new features

## Table of Contents

- [About](#about)
- [Documentation](#documentation)
- [Installation](#installation)
- [Update](#update)
- [What's New?](#whats-new)
  1.  [Broker API](#broker-api-new)
  2.  [OOP Design](#oop-design)
  3.  [Data Validation](#data-validation)
  4.  [Many Clients](#many-clients)
- [API Keys](#api-keys)
  1.  [Trading and Market Data API Keys](#trading-api-keys)
  2.  [Broker API Keys](#trading-api-keys)
- [Usage](#usage)
  1.  [Broker API Example](#broker-api-example)
  2.  [Trading API Example](#trading-api-example)
  3.  [Market Data API Example](#data-api-example)
- [Contributing](https://github.com/alpacahq/alpaca-py/blob/master/CONTRIBUTING.md)
- [License](https://github.com/alpacahq/alpaca-py/blob/master/LICENSE)

## About <a name="about"></a>

Alpaca-py provides an interface for interacting with the API products Alpaca offers. These API products are provided as various REST, WebSocket and SSE endpoints that allow you to do everything from streaming market data to creating your own investment apps.

This repository is a **modified version** of the [official alpaca-py SDK](https://github.com/alpacahq/alpaca-py) with enhancements for easier option trading and improved developer experience.

### What's Different in This Fork?

- **🎯 Simplified Option Data API** - New `OptionHelper` class eliminates the complexity of fetching option data. Get strike, bid/ask, greeks, IV, and volume in one simple call instead of managing multiple clients and requests. [Learn more →](docs/simplified_option_api.md)

- **📈 Simplified Trading API** - New `TradingHelper` class makes order placement and position management incredibly easy. Place bracket orders with stop loss and take profit in a single call. [Learn more →](docs/simplified_trading_api.md)

- **📊 Simplified Stock Data API** - New `StockHelper` class makes fetching market data effortless. Simple timeframe strings like `"1H"` or `"1D"`, automatic date handling with `days_back`, and clean dataclass returns with Python native types. [Learn more →](docs/simplified_stock_data_api.md)

- **₿ Simplified Crypto Data API** - New `CryptoHelper` class provides clean access to cryptocurrency market data. Same simple patterns as StockHelper but optimized for crypto (BTC/USD, ETH/USD, etc.) with proper handling of crypto-specific features. [Learn more →](docs/simplified_crypto_data_api.md)

- **💼 Simplified Account Management API** - New `AccountHelper` class makes account management effortless. Get cash, buying power, portfolio value with native Python types. Built-in Pattern Day Trader tracking and portfolio history with simple date ranges. [Learn more →](docs/simplified_account_api.md)

- **🔐 Environment Variable Support** - Integrated `python-dotenv` for secure API key management. Store your credentials in a `.env` file instead of hardcoding them.

- **✅ Enhanced Code Quality** - Improved flake8 compliance, fixed type comparisons, exception handling, and code patterns across the codebase.

- **📚 Better Documentation** - Additional examples, usage guides, and comprehensive test coverage for new features.

### Quick Start with Simplified APIs

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

# Trading - Place orders with ease
from alpaca.trading.trading_helper import TradingHelper

trader = TradingHelper()  # Auto-loads from .env
order = trader.buy_with_bracket(
    "SPY", qty=10, stop_loss=450.00, take_profit=550.00
)
```

Learn more about the API products Alpaca offers at https://alpaca.markets.

## Documentation <a name="documentation"></a>

Alpaca-py has a supplementary documentation site which contains references for all clients, methods and models found in this codebase. The documentation
also contains examples to get started with alpaca-py.

You can find the documentation site here: https://alpaca.markets/sdks/python/getting_started.html

You can also find the API Reference of Alpaca APIs: https://docs.alpaca.markets/reference

## Installation <a name="installation"></a>

Alpaca-py is supported on Python 3.8+.  You can install Alpaca-py using pip.

Run the following command in your terminal.

```shell
  pip install alpaca-py
```

## Update <a name="update"></a>

If you already have Alpaca-py installed, and would like to use the latest version available...

Run the following command in your terminal:

```shell
  pip install alpaca-py --upgrade
```

## What’s New? <a name="whats-new"></a>

If you’ve used the previous python SDK alpaca-trade-api, there are a few key differences to be aware of.

### Broker API <a name="broker-api-new"></a>

Alpaca-py lets you use Broker API to start building your investment apps! Learn more at the [Broker](https://docs.alpaca.markets/docs/about-broker-api) page.

### OOP Design <a name="oop-design"></a>

Alpaca-py uses a more OOP approach to submitting requests compared to the previous SDK. To submit a request, you will most likely need to create a request object containing the desired request data. Generally, there is a unique request model for each method.

Some examples of request models corresponding to methods:

- `GetOrdersRequest` for `TradingClient.get_orders()`
- `CryptoLatestOrderbookRequest` for `CryptoHistoricalDataClient.get_crypto_latest_orderbook()`

**Request Models Usage Example**

To get historical bar data for crypto, you will need to provide a `CryptoBarsRequest` object.

```python
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

# no keys required for crypto data
client = CryptoHistoricalDataClient()

request_params = CryptoBarsRequest(
                        symbol_or_symbols=["BTC/USD", "ETH/USD"],
                        timeframe=TimeFrame.Day,
                        start=datetime(2022, 7, 1)
                 )

bars = client.get_crypto_bars(request_params)
```

### Data Validation <a name="data-validation"></a>

Alpaca-py uses _pydantic_ to validate data models at run-time. This means if you are receiving request data via JSON from a client. You can handle parsing and validation through Alpaca’s request models. All request models can be instantiated by passing in data in dictionary format.

Here is a rough example of what is possible.

```python

 @app.route('/post_json', methods=['POST'])
 def do_trade():
     # ...

     order_data_json = request.get_json()

     # validate data
     MarketOrderRequest(**order_data_json)

     # ...
```

### Many Clients <a name="many-clients"></a>

Alpaca-py has a lot of client classes. There is a client for each API and even asset class specific clients (`StockHistoricalDataClient`, `CryptoDataStream`, `OptionHistoricalDataClient`). This requires you to pick and choose clients based on your needs.

**Broker API:** `BrokerClient`

**Trading API:** `TradingClient`

**Market Data API:** `StockHistoricalDataClient`, `CryptoHistoricalDataClient`, `NewsClient`, `OptionHistoricalDataClient`, `CryptoDataStream`, `StockDataStream`, `NewsDataStream`, `OptionDataStream`

## API Keys <a name="api-keys"></a>

### Trading and Market Data API <a name="trading-api-keys"></a>

In order to use Alpaca’s services you’ll need to sign up for an Alpaca account and retrieve your API keys. Signing up is completely free and takes only a few minutes. Sandbox environments are available to test out the API. To use the sandbox environment, you will need to provide sandbox/paper keys. API keys are passed into Alpaca-py through either `TradingClient`, `StockHistoricalDataClient`, `CryptoHistoricalDataClient`, `NewsClient`, `OptionHistoricalDataClient`, `StockDataStream`, `CryptoDataStream`,`NewsDataStream`, or `OptionDataStream`.

### Broker API <a name="broker-api-keys"></a>

To use the Broker API, you will need to sign up for a broker account and retrieve your Broker API keys. The API keys can be found on the dashboard once you’ve logged in. Alpaca also provides a sandbox environment to test out Broker API. To use the sandbox mode, provide your sandbox keys. Once you have your keys, you can pass them into `BrokerClient` to get started.

## Usage <a name="usage"></a>

Alpaca’s APIs allow you to do everything from building algorithmic trading strategies to building a full brokerage experience for your own end users. Here are some things you can do with Alpaca-py.

To view full descriptions and examples view the [documentation page](https://alpaca.markets/sdks/python/).

**Market Data API**: Access live and historical market data for 5000+ stocks, 20+ crypto, and options.

**Trading API**: Trade stock and crypto with lightning fast execution speeds.

**Broker API & Connect**: Build investment apps - from robo-advisors to brokerages.

### Broker API Example <a name="broker-api-example"></a>

**Listing All Accounts**

The `BrokerClient.list_accounts` method allows you to list all the brokerage accounts under your management. The method takes an optional parameter `search_parameters` which requires a `ListAccountsRequest` object. This parameter allows you to filter the list of accounts returned.

```python
from alpaca.broker.client import BrokerClient
from alpaca.broker.requests import ListAccountsRequest
from alpaca.broker.enums import AccountEntities

broker_client = BrokerClient('api-key', 'secret-key')

# search for accounts created after January 30th 2022.
# Response should contain Contact and Identity fields for each account.
filter = ListAccountsRequest(
                    created_after=datetime.datetime.strptime("2022-01-30", "%Y-%m-%d"),
                    entities=[AccountEntities.CONTACT, AccountEntities.IDENTITY]
                    )

accounts = broker_client.list_accounts(search_parameters=filter)
```

### Trading API Example <a name="trading-api-example"></a>

**Submitting an Order**

To create an order on Alpaca-py you must use an `OrderRequest` object. There are different `OrderRequest` objects based on the type of order you want to make. For market orders, there is `MarketOrderRequest`, limit orders have `LimitOrderRequest`, stop orders `StopOrderRequest`, and trailing stop orders have `TrailingStopOrderRequest`. Each order type have their own required parameters for a successful order.

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

trading_client = TradingClient('api-key', 'secret-key')


# preparing order data
market_order_data = MarketOrderRequest(
                      symbol="BTC/USD",
                      qty=0.0001,
                      side=OrderSide.BUY,
                      time_in_force=TimeInForce.DAY
                  )

# Market order
market_order = trading_client.submit_order(
                order_data=market_order_data
                )
```

### Market Data API Example <a name="data-api-example"></a>

**Querying Historical Bar Data**

You can request bar data via the HistoricalDataClients. In this example, we query daily bar data for “BTC/USD” and “ETH/USD” since July 1st 2022. You can convert the response to a multi-index pandas dataframe using the `.df` property. There are `StockHistoricalDataClient` and `OptionHistoricalDataClient` that you also could use to fetch equity/options historical data.

```python
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

# no keys required for crypto data
client = CryptoHistoricalDataClient()

request_params = CryptoBarsRequest(
                        symbol_or_symbols=["BTC/USD", "ETH/USD"],
                        timeframe=TimeFrame.Day,
                        start=datetime.strptime("2022-07-01", '%Y-%m-%d')
                        )

bars = client.get_crypto_bars(request_params)

# convert to dataframe
bars.df

```

**Querying News Data** <a name="news-client-example"></a>

You can query news data via the NewsClient. In this example, we query news data for “TSLA” since July 1st 2022. You can convert the response to a pandas dataframe using the `.df` property.

```python
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from datetime import datetime

# no keys required for news data
client = NewsClient()

request_params = NewsRequest(
                        symbols="TSLA",
                        start=datetime.strptime("2022-07-01", '%Y-%m-%d')
                        )

news = client.get_news(request_params)

# convert to dataframe
news.df

```

### Options Trading <a name="options-trading"></a>

We're excited to support options trading! Use this section to read up on Alpaca's options trading capabilities.
For more details, please refer to [our documentation page for options trading](https://docs.alpaca.markets/docs/options-trading)

There is an example jupyter notebook to explain methods of alpaca-py for options trading.

* [jupyter notebook: options trading basic example with alpaca-py](https://github.com/alpacahq/alpaca-py/blob/master/examples/options/options-trading-basic.ipynb)

### Jupyter Notebook Library <a name="colab-library"></a>

Explore examples for stocks, options, and crypto using alpaca-py. Notebooks for each asset class are provided in their respective directories!

* [Stocks](https://github.com/alpacahq/alpaca-py/blob/master/examples/stocks/README.md)
* [Crypto](https://github.com/alpacahq/alpaca-py/blob/master/examples/crypto/README.md)
* [Options](https://github.com/alpacahq/alpaca-py/blob/master/examples/options/README.md)
* [Multi-Leg Options](https://github.com/alpacahq/alpaca-py/blob/master/examples/options/README.md)