"""
Tests for StockHelper simplified stock data API.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from alpaca.data.models import Bar, BarSet, Quote, QuoteSet, Snapshot, Trade, TradeSet
from alpaca.data.stock_helper import (
    BarData,
    QuoteData,
    SnapshotData,
    StockHelper,
    TradeData,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


# ==================== Fixtures ====================


@pytest.fixture
def mock_bar():
    """Create a mock Bar object."""
    bar = MagicMock(spec=Bar)
    bar.timestamp = datetime(2025, 1, 1, 10, 0, 0)
    bar.open = "500.00"
    bar.high = "505.00"
    bar.low = "499.00"
    bar.close = "503.00"
    bar.volume = "1000000"
    bar.trade_count = "5000"
    bar.vwap = "502.00"
    return bar


@pytest.fixture
def mock_quote():
    """Create a mock Quote object."""
    quote = MagicMock(spec=Quote)
    quote.timestamp = datetime(2025, 1, 1, 10, 0, 0)
    quote.bid_price = "502.50"
    quote.bid_size = "100"
    quote.ask_price = "502.75"
    quote.ask_size = "200"
    quote.conditions = ["A", "B"]
    return quote


@pytest.fixture
def mock_trade():
    """Create a mock Trade object."""
    trade = MagicMock(spec=Trade)
    trade.timestamp = datetime(2025, 1, 1, 10, 0, 0)
    trade.price = "502.60"
    trade.size = "100"
    trade.conditions = ["@"]
    trade.exchange = "V"
    return trade


@pytest.fixture
def mock_snapshot(mock_bar, mock_quote, mock_trade):
    """Create a mock Snapshot object."""
    snapshot = MagicMock(spec=Snapshot)
    snapshot.latest_bar = mock_bar
    snapshot.latest_quote = mock_quote
    snapshot.latest_trade = mock_trade
    snapshot.prev_daily_bar = mock_bar
    return snapshot


@pytest.fixture
def stock_helper_with_mocks():
    """Create StockHelper with mocked client."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "test_api_key",
            "ALPACA_SECRET_KEY": "test_secret_key",
        },
    ):
        helper = StockHelper()
        helper.client = MagicMock()
        return helper


# ==================== Initialization Tests ====================


def test_init_with_explicit_credentials():
    """Test initialization with explicit credentials."""
    helper = StockHelper(api_key="test_key", secret_key="test_secret")
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
        helper = StockHelper()
        assert helper.client is not None


def test_init_missing_credentials():
    """Test initialization fails without credentials."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(
            ValueError, match="API key and secret key must be provided"
        ):
            StockHelper()


# ==================== Timeframe Parsing Tests ====================


def test_parse_timeframe_minutes(stock_helper_with_mocks):
    """Test parsing minute timeframes."""
    tf = stock_helper_with_mocks._parse_timeframe("1Min")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Minute

    tf = stock_helper_with_mocks._parse_timeframe("5Min")
    assert tf.amount == 5


def test_parse_timeframe_hours(stock_helper_with_mocks):
    """Test parsing hour timeframes."""
    tf = stock_helper_with_mocks._parse_timeframe("1H")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Hour

    tf = stock_helper_with_mocks._parse_timeframe("1Hour")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Hour


def test_parse_timeframe_days(stock_helper_with_mocks):
    """Test parsing day timeframes."""
    tf = stock_helper_with_mocks._parse_timeframe("1D")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Day

    tf = stock_helper_with_mocks._parse_timeframe("1Day")
    assert tf.amount == 1


def test_parse_timeframe_weeks(stock_helper_with_mocks):
    """Test parsing week timeframes."""
    tf = stock_helper_with_mocks._parse_timeframe("1W")
    assert tf.amount == 1
    assert tf.unit == TimeFrameUnit.Week


def test_parse_timeframe_invalid(stock_helper_with_mocks):
    """Test parsing invalid timeframe raises error."""
    with pytest.raises(ValueError, match="Invalid timeframe"):
        stock_helper_with_mocks._parse_timeframe("invalid")


# ==================== Latest Data Tests ====================


def test_get_latest_quote(stock_helper_with_mocks, mock_quote):
    """Test get_latest_quote."""
    stock_helper_with_mocks.client.get_stock_latest_quote.return_value = {
        "SPY": mock_quote
    }

    quote = stock_helper_with_mocks.get_latest_quote("SPY")

    assert quote.symbol == "SPY"
    assert quote.bid_price == 502.50
    assert quote.ask_price == 502.75
    assert quote.bid_size == 100
    assert quote.ask_size == 200


def test_get_latest_quotes_multi(stock_helper_with_mocks, mock_quote):
    """Test get_latest_quotes for multiple symbols."""
    stock_helper_with_mocks.client.get_stock_latest_quote.return_value = {
        "SPY": mock_quote,
        "QQQ": mock_quote,
    }

    quotes = stock_helper_with_mocks.get_latest_quotes(["SPY", "QQQ"])

    assert len(quotes) == 2
    assert "SPY" in quotes
    assert "QQQ" in quotes
    assert all(isinstance(q, QuoteData) for q in quotes.values())


def test_get_latest_bar(stock_helper_with_mocks, mock_bar):
    """Test get_latest_bar."""
    stock_helper_with_mocks.client.get_stock_latest_bar.return_value = {
        "SPY": mock_bar
    }

    bar = stock_helper_with_mocks.get_latest_bar("SPY")

    assert bar.symbol == "SPY"
    assert bar.open == 500.00
    assert bar.high == 505.00
    assert bar.low == 499.00
    assert bar.close == 503.00
    assert bar.volume == 1000000


def test_get_latest_trade(stock_helper_with_mocks, mock_trade):
    """Test get_latest_trade."""
    stock_helper_with_mocks.client.get_stock_latest_trade.return_value = {
        "SPY": mock_trade
    }

    trade = stock_helper_with_mocks.get_latest_trade("SPY")

    assert trade.symbol == "SPY"
    assert trade.price == 502.60
    assert trade.size == 100


# ==================== Historical Bar Tests ====================


def test_get_bars(stock_helper_with_mocks, mock_bar):
    """Test get_bars."""
    mock_response = MagicMock()
    mock_response.data = {"SPY": [mock_bar, mock_bar]}
    stock_helper_with_mocks.client.get_stock_bars.return_value = mock_response

    bars = stock_helper_with_mocks.get_bars("SPY", timeframe="1H", days_back=1)

    assert len(bars) == 2
    assert all(isinstance(b, BarData) for b in bars)
    assert bars[0].symbol == "SPY"


def test_get_bars_with_dates(stock_helper_with_mocks, mock_bar):
    """Test get_bars with specific start/end dates."""
    mock_response = MagicMock()
    mock_response.data = {"SPY": [mock_bar]}
    stock_helper_with_mocks.client.get_stock_bars.return_value = mock_response

    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 31)

    bars = stock_helper_with_mocks.get_bars(
        "SPY", timeframe="1D", start=start, end=end
    )

    assert len(bars) == 1


def test_get_bars_multi(stock_helper_with_mocks, mock_bar):
    """Test get_bars_multi for multiple symbols."""
    mock_response = MagicMock()
    mock_response.data = {
        "SPY": [mock_bar],
        "QQQ": [mock_bar, mock_bar],
    }
    stock_helper_with_mocks.client.get_stock_bars.return_value = mock_response

    bars = stock_helper_with_mocks.get_bars_multi(
        ["SPY", "QQQ"], timeframe="1H", days_back=1
    )

    assert len(bars) == 2
    assert len(bars["SPY"]) == 1
    assert len(bars["QQQ"]) == 2


# ==================== Historical Quote Tests ====================


def test_get_quotes(stock_helper_with_mocks, mock_quote):
    """Test get_quotes."""
    mock_response = MagicMock()
    mock_response.data = {"SPY": [mock_quote, mock_quote]}
    stock_helper_with_mocks.client.get_stock_quotes.return_value = mock_response

    quotes = stock_helper_with_mocks.get_quotes("SPY", days_back=1, limit=10)

    assert len(quotes) == 2
    assert all(isinstance(q, QuoteData) for q in quotes)


# ==================== Historical Trade Tests ====================


def test_get_trades(stock_helper_with_mocks, mock_trade):
    """Test get_trades."""
    mock_response = MagicMock()
    mock_response.data = {"SPY": [mock_trade, mock_trade]}
    stock_helper_with_mocks.client.get_stock_trades.return_value = mock_response

    trades = stock_helper_with_mocks.get_trades("SPY", days_back=1, limit=10)

    assert len(trades) == 2
    assert all(isinstance(t, TradeData) for t in trades)


# ==================== Snapshot Tests ====================


def test_get_snapshot(stock_helper_with_mocks, mock_snapshot):
    """Test get_snapshot."""
    stock_helper_with_mocks.client.get_stock_snapshot.return_value = {
        "SPY": mock_snapshot
    }

    snapshot = stock_helper_with_mocks.get_snapshot("SPY")

    assert snapshot.symbol == "SPY"
    assert snapshot.latest_bar is not None
    assert snapshot.latest_quote is not None
    assert snapshot.latest_trade is not None
    assert isinstance(snapshot.latest_bar, BarData)
    assert isinstance(snapshot.latest_quote, QuoteData)
    assert isinstance(snapshot.latest_trade, TradeData)


def test_get_snapshots_multi(stock_helper_with_mocks, mock_snapshot):
    """Test get_snapshots for multiple symbols."""
    stock_helper_with_mocks.client.get_stock_snapshot.return_value = {
        "SPY": mock_snapshot,
        "QQQ": mock_snapshot,
    }

    snapshots = stock_helper_with_mocks.get_snapshots(["SPY", "QQQ"])

    assert len(snapshots) == 2
    assert "SPY" in snapshots
    assert "QQQ" in snapshots
    assert all(isinstance(s, SnapshotData) for s in snapshots.values())


# ==================== Dataclass Tests ====================


def test_bar_data_from_bar(mock_bar):
    """Test BarData.from_bar."""
    bar_data = BarData.from_bar("SPY", mock_bar)

    assert bar_data.symbol == "SPY"
    assert bar_data.open == 500.00
    assert bar_data.high == 505.00
    assert bar_data.low == 499.00
    assert bar_data.close == 503.00
    assert bar_data.volume == 1000000
    assert bar_data.trade_count == 5000
    assert bar_data.vwap == 502.00


def test_quote_data_from_quote(mock_quote):
    """Test QuoteData.from_quote."""
    quote_data = QuoteData.from_quote("SPY", mock_quote)

    assert quote_data.symbol == "SPY"
    assert quote_data.bid_price == 502.50
    assert quote_data.ask_price == 502.75
    assert quote_data.bid_size == 100
    assert quote_data.ask_size == 200
    assert quote_data.conditions == ["A", "B"]


def test_trade_data_from_trade(mock_trade):
    """Test TradeData.from_trade."""
    trade_data = TradeData.from_trade("SPY", mock_trade)

    assert trade_data.symbol == "SPY"
    assert trade_data.price == 502.60
    assert trade_data.size == 100
    assert trade_data.conditions == ["@"]
    assert trade_data.exchange == "V"


def test_snapshot_data_from_snapshot(mock_snapshot):
    """Test SnapshotData.from_snapshot."""
    snapshot_data = SnapshotData.from_snapshot("SPY", mock_snapshot)

    assert snapshot_data.symbol == "SPY"
    assert snapshot_data.latest_bar is not None
    assert snapshot_data.latest_quote is not None
    assert snapshot_data.latest_trade is not None
    assert snapshot_data.prev_daily_bar is not None


# ==================== Edge Case Tests ====================


def test_get_latest_quote_no_data(stock_helper_with_mocks):
    """Test get_latest_quote raises error when no data returned."""
    stock_helper_with_mocks.client.get_stock_latest_quote.return_value = {}

    with pytest.raises(ValueError, match="No quote data returned"):
        stock_helper_with_mocks.get_latest_quote("INVALID")


def test_get_bars_empty_response(stock_helper_with_mocks):
    """Test get_bars with empty response."""
    mock_response = MagicMock()
    mock_response.data = {}
    stock_helper_with_mocks.client.get_stock_bars.return_value = mock_response

    bars = stock_helper_with_mocks.get_bars("SPY", timeframe="1D")

    assert len(bars) == 0


def test_bar_data_none_values():
    """Test BarData handles None values gracefully."""
    bar = MagicMock(spec=Bar)
    bar.timestamp = datetime(2025, 1, 1)
    bar.open = "100"
    bar.high = "105"
    bar.low = "99"
    bar.close = "103"
    bar.volume = "1000"
    bar.trade_count = None
    bar.vwap = None

    bar_data = BarData.from_bar("SPY", bar)

    assert bar_data.trade_count is None
    assert bar_data.vwap is None


def test_quote_data_none_conditions():
    """Test QuoteData handles None conditions."""
    quote = MagicMock(spec=Quote)
    quote.timestamp = datetime(2025, 1, 1)
    quote.bid_price = "100"
    quote.bid_size = "10"
    quote.ask_price = "101"
    quote.ask_size = "20"
    quote.conditions = None

    quote_data = QuoteData.from_quote("SPY", quote)

    assert quote_data.conditions is None
