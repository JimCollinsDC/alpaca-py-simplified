"""
Tests for CryptoHelper simplified crypto data API.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from alpaca.data.models import Bar, Quote, Snapshot, Trade
from alpaca.data.crypto_helper import (
    CryptoBarData,
    CryptoHelper,
    CryptoQuoteData,
    CryptoSnapshotData,
    CryptoTradeData,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


# ==================== Fixtures ====================


@pytest.fixture
def mock_crypto_bar():
    """Create a mock Bar object for crypto."""
    bar = MagicMock(spec=Bar)
    bar.timestamp = datetime(2025, 1, 1, 10, 0, 0)
    bar.open = "50000.00"
    bar.high = "50500.00"
    bar.low = "49900.00"
    bar.close = "50300.00"
    bar.volume = "10.5"
    bar.trade_count = "500"
    bar.vwap = "50200.00"
    return bar


@pytest.fixture
def mock_crypto_quote():
    """Create a mock Quote object for crypto."""
    quote = MagicMock(spec=Quote)
    quote.timestamp = datetime(2025, 1, 1, 10, 0, 0)
    quote.bid_price = "50250.00"
    quote.bid_size = "1.5"
    quote.ask_price = "50275.00"
    quote.ask_size = "2.0"
    return quote


@pytest.fixture
def mock_crypto_trade():
    """Create a mock Trade object for crypto."""
    trade = MagicMock(spec=Trade)
    trade.timestamp = datetime(2025, 1, 1, 10, 0, 0)
    trade.price = "50260.00"
    trade.size = "0.5"
    trade.taker_side = "buy"
    return trade


@pytest.fixture
def mock_crypto_snapshot(mock_crypto_bar, mock_crypto_quote, mock_crypto_trade):
    """Create a mock Snapshot object for crypto."""
    snapshot = MagicMock(spec=Snapshot)
    snapshot.minute_bar = mock_crypto_bar
    snapshot.latest_quote = mock_crypto_quote
    snapshot.latest_trade = mock_crypto_trade
    snapshot.previous_daily_bar = mock_crypto_bar
    return snapshot


@pytest.fixture
def crypto_helper_with_mocks():
    """Create CryptoHelper with mocked client."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "test_api_key",
            "ALPACA_SECRET_KEY": "test_secret_key",
        },
    ):
        helper = CryptoHelper()
        helper.client = MagicMock()
        return helper


# ==================== Initialization Tests ====================


def test_init_with_explicit_credentials():
    """Test initialization with explicit credentials."""
    helper = CryptoHelper(api_key="test_key", secret_key="test_secret")
    assert helper.client is not None


def test_init_from_environment():
    """Test initialization from environment variables."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "env_key",
            "ALPACA_SECRET_KEY": "env_secret",
        },
    ):
        helper = CryptoHelper()
        assert helper.api_key == "env_key"
        assert helper.secret_key == "env_secret"


def test_init_without_credentials():
    """Test that CryptoHelper can initialize without credentials."""
    with patch.dict(os.environ, {}, clear=True):
        helper = CryptoHelper()
        assert helper.api_key is None
        assert helper.secret_key is None


# ==================== Timeframe Parsing Tests ====================


def test_parse_timeframe_minutes(crypto_helper_with_mocks):
    """Test parsing minute timeframes."""
    tf = crypto_helper_with_mocks._parse_timeframe("1Min")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Minute

    tf = crypto_helper_with_mocks._parse_timeframe("5Min")
    assert tf.amount == 5
    assert tf.unit == TimeFrameUnit.Minute


def test_parse_timeframe_hours(crypto_helper_with_mocks):
    """Test parsing hour timeframes."""
    tf = crypto_helper_with_mocks._parse_timeframe("1H")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Hour

    tf = crypto_helper_with_mocks._parse_timeframe("4Hour")
    assert tf.amount == 4
    assert tf.unit == TimeFrameUnit.Hour


def test_parse_timeframe_days(crypto_helper_with_mocks):
    """Test parsing day timeframes."""
    tf = crypto_helper_with_mocks._parse_timeframe("1D")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Day


def test_parse_timeframe_weeks(crypto_helper_with_mocks):
    """Test parsing week timeframes."""
    tf = crypto_helper_with_mocks._parse_timeframe("1W")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Week


def test_parse_timeframe_invalid(crypto_helper_with_mocks):
    """Test parsing invalid timeframe raises ValueError."""
    with pytest.raises(ValueError, match="Invalid timeframe"):
        crypto_helper_with_mocks._parse_timeframe("invalid")


# ==================== Dataclass Conversion Tests ====================


def test_crypto_bar_data_from_bar(mock_crypto_bar):
    """Test CryptoBarData creation from Bar."""
    bar_data = CryptoBarData.from_bar("BTC/USD", mock_crypto_bar)
    assert bar_data.symbol == "BTC/USD"
    assert bar_data.timestamp == mock_crypto_bar.timestamp
    assert bar_data.open == 50000.00
    assert bar_data.close == 50300.00
    assert bar_data.volume == 10.5
    assert isinstance(bar_data.volume, float)


def test_crypto_quote_data_from_quote(mock_crypto_quote):
    """Test CryptoQuoteData creation from Quote."""
    quote_data = CryptoQuoteData.from_quote("BTC/USD", mock_crypto_quote)
    assert quote_data.symbol == "BTC/USD"
    assert quote_data.bid_price == 50250.00
    assert quote_data.ask_price == 50275.00
    assert isinstance(quote_data.bid_size, float)


def test_crypto_trade_data_from_trade(mock_crypto_trade):
    """Test CryptoTradeData creation from Trade."""
    trade_data = CryptoTradeData.from_trade("BTC/USD", mock_crypto_trade)
    assert trade_data.symbol == "BTC/USD"
    assert trade_data.price == 50260.00
    assert trade_data.size == 0.5
    assert trade_data.taker_side == "buy"


def test_crypto_snapshot_data_from_snapshot(mock_crypto_snapshot):
    """Test CryptoSnapshotData creation from Snapshot."""
    snap_data = CryptoSnapshotData.from_snapshot("BTC/USD", mock_crypto_snapshot)
    assert snap_data.symbol == "BTC/USD"
    assert snap_data.latest_bar is not None
    assert snap_data.latest_quote is not None
    assert snap_data.latest_trade is not None


# ==================== Latest Data Tests ====================


def test_get_latest_quote(crypto_helper_with_mocks, mock_crypto_quote):
    """Test getting latest quote for a crypto."""
    crypto_helper_with_mocks.client.get_crypto_latest_quote.return_value = {
        "BTC/USD": mock_crypto_quote
    }

    quote = crypto_helper_with_mocks.get_latest_quote("BTC/USD")
    assert quote is not None
    assert quote.symbol == "BTC/USD"
    assert quote.bid_price == 50250.00


def test_get_latest_quote_not_found(crypto_helper_with_mocks):
    """Test getting latest quote when symbol not found."""
    crypto_helper_with_mocks.client.get_crypto_latest_quote.return_value = {}

    quote = crypto_helper_with_mocks.get_latest_quote("INVALID")
    assert quote is None


def test_get_latest_quotes_multi(crypto_helper_with_mocks, mock_crypto_quote):
    """Test getting latest quotes for multiple cryptos."""
    crypto_helper_with_mocks.client.get_crypto_latest_quote.return_value = {
        "BTC/USD": mock_crypto_quote,
        "ETH/USD": mock_crypto_quote,
    }

    quotes = crypto_helper_with_mocks.get_latest_quotes(["BTC/USD", "ETH/USD"])
    assert len(quotes) == 2
    assert "BTC/USD" in quotes
    assert "ETH/USD" in quotes


def test_get_latest_bar(crypto_helper_with_mocks, mock_crypto_bar):
    """Test getting latest bar for a crypto."""
    crypto_helper_with_mocks.client.get_crypto_latest_bar.return_value = {
        "BTC/USD": mock_crypto_bar
    }

    bar = crypto_helper_with_mocks.get_latest_bar("BTC/USD")
    assert bar is not None
    assert bar.symbol == "BTC/USD"
    assert bar.close == 50300.00


def test_get_latest_trade(crypto_helper_with_mocks, mock_crypto_trade):
    """Test getting latest trade for a crypto."""
    crypto_helper_with_mocks.client.get_crypto_latest_trade.return_value = {
        "BTC/USD": mock_crypto_trade
    }

    trade = crypto_helper_with_mocks.get_latest_trade("BTC/USD")
    assert trade is not None
    assert trade.symbol == "BTC/USD"
    assert trade.price == 50260.00


# ==================== Historical Bars Tests ====================


def test_get_bars_with_timeframe(crypto_helper_with_mocks, mock_crypto_bar):
    """Test getting historical bars with timeframe."""
    mock_barset = MagicMock()
    mock_barset.__getitem__.return_value = [mock_crypto_bar]
    mock_barset.__contains__.return_value = True
    crypto_helper_with_mocks.client.get_crypto_bars.return_value = mock_barset

    bars = crypto_helper_with_mocks.get_bars("BTC/USD", timeframe="1H")
    assert len(bars) > 0
    assert bars[0].symbol == "BTC/USD"


def test_get_bars_with_days_back(crypto_helper_with_mocks, mock_crypto_bar):
    """Test getting bars with days_back parameter."""
    mock_barset = MagicMock()
    mock_barset.__getitem__.return_value = [mock_crypto_bar]
    mock_barset.__contains__.return_value = True
    crypto_helper_with_mocks.client.get_crypto_bars.return_value = mock_barset

    bars = crypto_helper_with_mocks.get_bars("BTC/USD", days_back=7)
    assert len(bars) > 0

    # Verify the request was made with correct date range
    call_args = crypto_helper_with_mocks.client.get_crypto_bars.call_args
    request = call_args[0][0]
    assert request.start is not None
    assert request.end is not None


def test_get_bars_empty_response(crypto_helper_with_mocks):
    """Test getting bars when symbol has no data."""
    mock_barset = MagicMock()
    mock_barset.__contains__.return_value = False
    crypto_helper_with_mocks.client.get_crypto_bars.return_value = mock_barset

    bars = crypto_helper_with_mocks.get_bars("INVALID")
    assert bars == []


def test_get_bars_multi(crypto_helper_with_mocks, mock_crypto_bar):
    """Test getting bars for multiple cryptos."""
    mock_barset = MagicMock()
    mock_barset.items.return_value = [
        ("BTC/USD", [mock_crypto_bar]),
        ("ETH/USD", [mock_crypto_bar]),
    ]
    crypto_helper_with_mocks.client.get_crypto_bars.return_value = mock_barset

    bars_dict = crypto_helper_with_mocks.get_bars_multi(
        ["BTC/USD", "ETH/USD"], timeframe="1H"
    )
    assert len(bars_dict) == 2
    assert "BTC/USD" in bars_dict
    assert "ETH/USD" in bars_dict


# ==================== Historical Trades Tests ====================


def test_get_trades(crypto_helper_with_mocks, mock_crypto_trade):
    """Test getting historical trades."""
    mock_tradeset = MagicMock()
    mock_tradeset.__getitem__.return_value = [mock_crypto_trade]
    mock_tradeset.__contains__.return_value = True
    crypto_helper_with_mocks.client.get_crypto_trades.return_value = mock_tradeset

    trades = crypto_helper_with_mocks.get_trades("BTC/USD", days_back=1)
    assert len(trades) > 0
    assert trades[0].symbol == "BTC/USD"
    assert trades[0].price == 50260.00


def test_get_trades_with_limit(crypto_helper_with_mocks, mock_crypto_trade):
    """Test getting trades with limit parameter."""
    mock_tradeset = MagicMock()
    mock_tradeset.__getitem__.return_value = [mock_crypto_trade]
    mock_tradeset.__contains__.return_value = True
    crypto_helper_with_mocks.client.get_crypto_trades.return_value = mock_tradeset

    trades = crypto_helper_with_mocks.get_trades("BTC/USD", limit=100)
    assert len(trades) > 0


def test_get_trades_empty(crypto_helper_with_mocks):
    """Test getting trades when no data available."""
    mock_tradeset = MagicMock()
    mock_tradeset.__contains__.return_value = False
    crypto_helper_with_mocks.client.get_crypto_trades.return_value = mock_tradeset

    trades = crypto_helper_with_mocks.get_trades("INVALID")
    assert trades == []


# ==================== Snapshot Tests ====================


def test_get_snapshot(crypto_helper_with_mocks, mock_crypto_snapshot):
    """Test getting snapshot for a crypto."""
    crypto_helper_with_mocks.client.get_crypto_snapshot.return_value = {
        "BTC/USD": mock_crypto_snapshot
    }

    snapshot = crypto_helper_with_mocks.get_snapshot("BTC/USD")
    assert snapshot is not None
    assert snapshot.symbol == "BTC/USD"
    assert snapshot.latest_bar is not None
    assert snapshot.latest_quote is not None
    assert snapshot.latest_trade is not None


def test_get_snapshot_not_found(crypto_helper_with_mocks):
    """Test getting snapshot when crypto not found."""
    crypto_helper_with_mocks.client.get_crypto_snapshot.return_value = {}

    snapshot = crypto_helper_with_mocks.get_snapshot("INVALID")
    assert snapshot is None


def test_get_snapshots_multi(crypto_helper_with_mocks, mock_crypto_snapshot):
    """Test getting snapshots for multiple cryptos."""
    crypto_helper_with_mocks.client.get_crypto_snapshot.return_value = {
        "BTC/USD": mock_crypto_snapshot,
        "ETH/USD": mock_crypto_snapshot,
    }

    snapshots = crypto_helper_with_mocks.get_snapshots(["BTC/USD", "ETH/USD"])
    assert len(snapshots) == 2
    assert "BTC/USD" in snapshots
    assert "ETH/USD" in snapshots


# ==================== Edge Cases ====================


def test_get_bars_with_explicit_dates(crypto_helper_with_mocks, mock_crypto_bar):
    """Test getting bars with explicit start/end dates."""
    mock_barset = MagicMock()
    mock_barset.__getitem__.return_value = [mock_crypto_bar]
    mock_barset.__contains__.return_value = True
    crypto_helper_with_mocks.client.get_crypto_bars.return_value = mock_barset

    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 7)
    bars = crypto_helper_with_mocks.get_bars(
        "BTC/USD", timeframe="1D", start=start, end=end
    )

    assert len(bars) > 0
    call_args = crypto_helper_with_mocks.client.get_crypto_bars.call_args
    request = call_args[0][0]
    assert request.start == start
    assert request.end == end


def test_crypto_bar_without_optional_fields():
    """Test CryptoBarData with missing optional fields."""
    bar = MagicMock(spec=Bar)
    bar.timestamp = datetime(2025, 1, 1)
    bar.open = "50000.00"
    bar.high = "51000.00"
    bar.low = "49000.00"
    bar.close = "50500.00"
    bar.volume = "10.0"
    bar.trade_count = None
    bar.vwap = None

    bar_data = CryptoBarData.from_bar("BTC/USD", bar)
    assert bar_data.trade_count is None
    assert bar_data.vwap is None


def test_crypto_trade_without_taker_side():
    """Test CryptoTradeData without taker_side field."""
    trade = MagicMock(spec=Trade)
    trade.timestamp = datetime(2025, 1, 1)
    trade.price = "50000.00"
    trade.size = "0.5"
    # No taker_side attribute

    trade_data = CryptoTradeData.from_trade("BTC/USD", trade)
    assert trade_data.taker_side is None
