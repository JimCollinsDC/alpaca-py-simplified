"""
Tests for TradingHelper simplified trading API.
"""

import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
    QueryOrderStatus,
    TimeInForce,
)
from alpaca.trading.models import Order, Position, TradeAccount
from alpaca.trading.trading_helper import OrderInfo, PositionInfo, TradingHelper


# ==================== Fixtures ====================


@pytest.fixture
def mock_position():
    """Create a mock Position object."""
    position = MagicMock(spec=Position)
    position.symbol = "SPY"
    position.qty = "10"
    position.market_value = "5000.00"
    position.avg_entry_price = "500.00"
    position.current_price = "500.00"
    position.unrealized_pl = "0.00"
    position.unrealized_plpc = "0.00"
    position.side = PositionSide.LONG
    position.cost_basis = "5000.00"
    position.asset_id = UUID("12345678-1234-1234-1234-123456789012")
    return position


@pytest.fixture
def mock_order():
    """Create a mock Order object."""
    order = MagicMock(spec=Order)
    order.id = UUID("87654321-4321-4321-4321-210987654321")
    order.symbol = "SPY"
    order.qty = "10"
    order.notional = None
    order.side = OrderSide.BUY
    order.type = OrderType.MARKET
    order.status = OrderStatus.NEW
    order.filled_qty = "0"
    order.filled_avg_price = None
    order.limit_price = None
    order.stop_price = None
    order.submitted_at = datetime(2025, 1, 1, 10, 0, 0)
    order.filled_at = None
    order.order_class = None
    return order


@pytest.fixture
def mock_account():
    """Create a mock TradeAccount object."""
    account = MagicMock(spec=TradeAccount)
    account.buying_power = "100000.00"
    account.cash = "50000.00"
    account.portfolio_value = "150000.00"
    return account


@pytest.fixture
def trading_helper_with_mocks():
    """Create TradingHelper with mocked client."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "test_api_key",
            "ALPACA_SECRET_KEY": "test_secret_key",
            "ALPACA_PAPER": "true",
        },
    ):
        helper = TradingHelper()
        helper.client = MagicMock()
        return helper


# ==================== Initialization Tests ====================


def test_init_with_explicit_credentials():
    """Test initialization with explicit credentials."""
    helper = TradingHelper(
        api_key="test_key", secret_key="test_secret", paper=True
    )
    assert helper.is_paper is True
    assert helper.client is not None


def test_init_from_environment():
    """Test initialization from environment variables."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "env_key",
            "ALPACA_SECRET_KEY": "env_secret",
            "ALPACA_PAPER": "false",
        },
    ):
        helper = TradingHelper()
        assert helper.is_paper is False


def test_init_paper_defaults_true():
    """Test that paper mode defaults to True if not specified."""
    with patch.dict(
        os.environ,
        {"ALPACA_API_KEY": "test_key", "ALPACA_SECRET_KEY": "test_secret"},
        clear=True,
    ):
        helper = TradingHelper()
        assert helper.is_paper is True


def test_init_missing_credentials():
    """Test initialization fails without credentials."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API key and secret key must be provided"):
            TradingHelper()


# ==================== Market Order Tests ====================


def test_buy_market_with_qty(trading_helper_with_mocks, mock_order):
    """Test buy_market with quantity."""
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_market("SPY", qty=10)

    assert order_info.symbol == "SPY"
    assert order_info.qty == 10.0
    assert order_info.side == "buy"
    trading_helper_with_mocks.client.submit_order.assert_called_once()


def test_buy_market_with_notional(trading_helper_with_mocks, mock_order):
    """Test buy_market with notional amount."""
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_market("SPY", notional=1000.0)

    assert order_info.symbol == "SPY"
    trading_helper_with_mocks.client.submit_order.assert_called_once()


def test_buy_market_requires_qty_or_notional(trading_helper_with_mocks):
    """Test buy_market requires either qty or notional."""
    with pytest.raises(ValueError, match="Must provide exactly one"):
        trading_helper_with_mocks.buy_market("SPY")

    with pytest.raises(ValueError, match="Must provide exactly one"):
        trading_helper_with_mocks.buy_market("SPY", qty=10, notional=1000)


def test_sell_market(trading_helper_with_mocks, mock_order):
    """Test sell_market."""
    mock_order.side = OrderSide.SELL
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.sell_market("SPY", qty=5)

    assert order_info.side == "sell"
    trading_helper_with_mocks.client.submit_order.assert_called_once()


# ==================== Limit Order Tests ====================


def test_buy_limit(trading_helper_with_mocks, mock_order):
    """Test buy_limit."""
    mock_order.type = OrderType.LIMIT
    mock_order.limit_price = "450.00"
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_limit(
        "SPY", qty=10, limit_price=450.00
    )

    assert order_info.type == "limit"
    assert order_info.limit_price == 450.00
    trading_helper_with_mocks.client.submit_order.assert_called_once()


def test_sell_limit(trading_helper_with_mocks, mock_order):
    """Test sell_limit."""
    mock_order.side = OrderSide.SELL
    mock_order.type = OrderType.LIMIT
    mock_order.limit_price = "550.00"
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.sell_limit(
        "SPY", qty=10, limit_price=550.00
    )

    assert order_info.side == "sell"
    assert order_info.limit_price == 550.00


# ==================== Bracket Order Tests ====================


def test_buy_with_bracket_both_stops(trading_helper_with_mocks, mock_order):
    """Test buy_with_bracket with both stop loss and take profit."""
    mock_order.order_class = OrderClass.BRACKET
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_with_bracket(
        "SPY", qty=10, stop_loss=450.00, take_profit=550.00
    )

    assert order_info.order_class == "bracket"
    trading_helper_with_mocks.client.submit_order.assert_called_once()


def test_buy_with_bracket_stop_loss_only(trading_helper_with_mocks, mock_order):
    """Test buy_with_bracket with only stop loss."""
    mock_order.order_class = OrderClass.BRACKET
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_with_bracket(
        "SPY", qty=10, stop_loss=450.00
    )

    assert order_info.order_class == "bracket"


def test_buy_with_bracket_take_profit_only(trading_helper_with_mocks, mock_order):
    """Test buy_with_bracket with only take profit."""
    mock_order.order_class = OrderClass.BRACKET
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_with_bracket(
        "SPY", qty=10, take_profit=550.00
    )

    assert order_info.order_class == "bracket"


def test_buy_with_bracket_requires_at_least_one(trading_helper_with_mocks):
    """Test buy_with_bracket requires at least one stop."""
    with pytest.raises(
        ValueError, match="Must provide at least one of take_profit or stop_loss"
    ):
        trading_helper_with_mocks.buy_with_bracket("SPY", qty=10)


def test_buy_with_bracket_stop_limit(trading_helper_with_mocks, mock_order):
    """Test buy_with_bracket with stop-limit order."""
    mock_order.order_class = OrderClass.BRACKET
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_with_bracket(
        "SPY", qty=10, stop_loss=450.00, stop_loss_limit=445.00
    )

    assert order_info.order_class == "bracket"


def test_buy_with_bracket_stop_limit_requires_stop(trading_helper_with_mocks):
    """Test stop_loss_limit requires stop_loss."""
    with pytest.raises(ValueError, match="stop_loss is required"):
        trading_helper_with_mocks.buy_with_bracket(
            "SPY", qty=10, stop_loss_limit=445.00
        )


def test_sell_with_bracket(trading_helper_with_mocks, mock_order):
    """Test sell_with_bracket."""
    mock_order.side = OrderSide.SELL
    mock_order.order_class = OrderClass.BRACKET
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.sell_with_bracket(
        "SPY", qty=10, stop_loss=550.00, take_profit=450.00
    )

    assert order_info.side == "sell"
    assert order_info.order_class == "bracket"


# ==================== Position Tests ====================


def test_get_position(trading_helper_with_mocks, mock_position):
    """Test get_position."""
    trading_helper_with_mocks.client.get_open_position.return_value = mock_position

    position_info = trading_helper_with_mocks.get_position("SPY")

    assert position_info.symbol == "SPY"
    assert position_info.qty == 10.0
    assert position_info.side == "long"
    trading_helper_with_mocks.client.get_open_position.assert_called_once_with("SPY")


def test_get_all_positions(trading_helper_with_mocks, mock_position):
    """Test get_all_positions."""
    trading_helper_with_mocks.client.get_all_positions.return_value = [
        mock_position,
        mock_position,
    ]

    positions = trading_helper_with_mocks.get_all_positions()

    assert len(positions) == 2
    assert all(isinstance(p, PositionInfo) for p in positions)


def test_close_position_all(trading_helper_with_mocks, mock_order):
    """Test close_position (all shares)."""
    trading_helper_with_mocks.client.close_position.return_value = mock_order

    order_info = trading_helper_with_mocks.close_position("SPY")

    assert order_info.symbol == "SPY"
    trading_helper_with_mocks.client.close_position.assert_called_once_with("SPY")


def test_close_position_qty(trading_helper_with_mocks, mock_order):
    """Test close_position with specific quantity."""
    trading_helper_with_mocks.client.close_position.return_value = mock_order

    order_info = trading_helper_with_mocks.close_position("SPY", qty=5)

    assert order_info.symbol == "SPY"


def test_close_position_percentage(trading_helper_with_mocks, mock_order):
    """Test close_position with percentage."""
    trading_helper_with_mocks.client.close_position.return_value = mock_order

    order_info = trading_helper_with_mocks.close_position("SPY", percentage=50)

    assert order_info.symbol == "SPY"


def test_close_position_cannot_specify_both(trading_helper_with_mocks):
    """Test cannot specify both qty and percentage."""
    with pytest.raises(ValueError, match="Cannot specify both"):
        trading_helper_with_mocks.close_position("SPY", qty=5, percentage=50)


# ==================== Order Management Tests ====================


def test_get_order(trading_helper_with_mocks, mock_order):
    """Test get_order."""
    order_id = UUID("87654321-4321-4321-4321-210987654321")
    trading_helper_with_mocks.client.get_order_by_id.return_value = mock_order

    order_info = trading_helper_with_mocks.get_order(order_id)

    assert order_info.id == str(order_id)
    trading_helper_with_mocks.client.get_order_by_id.assert_called_once_with(order_id)


def test_get_orders_default(trading_helper_with_mocks, mock_order):
    """Test get_orders with default parameters."""
    trading_helper_with_mocks.client.get_orders.return_value = [
        mock_order,
        mock_order,
    ]

    orders = trading_helper_with_mocks.get_orders()

    assert len(orders) == 2
    assert all(isinstance(o, OrderInfo) for o in orders)


def test_get_orders_with_filters(trading_helper_with_mocks, mock_order):
    """Test get_orders with filters."""
    trading_helper_with_mocks.client.get_orders.return_value = [mock_order]

    orders = trading_helper_with_mocks.get_orders(
        status=QueryOrderStatus.ALL, symbols=["SPY"], limit=10
    )

    assert len(orders) == 1


def test_cancel_order(trading_helper_with_mocks):
    """Test cancel_order."""
    order_id = UUID("87654321-4321-4321-4321-210987654321")

    trading_helper_with_mocks.cancel_order(order_id)

    trading_helper_with_mocks.client.cancel_order_by_id.assert_called_once_with(
        order_id
    )


def test_cancel_all_orders(trading_helper_with_mocks):
    """Test cancel_all_orders."""
    trading_helper_with_mocks.cancel_all_orders()

    trading_helper_with_mocks.client.cancel_orders.assert_called_once()


# ==================== Account Info Tests ====================


def test_get_buying_power(trading_helper_with_mocks, mock_account):
    """Test get_buying_power."""
    trading_helper_with_mocks.client.get_account.return_value = mock_account

    bp = trading_helper_with_mocks.get_buying_power()

    assert bp == 100000.00


def test_get_cash(trading_helper_with_mocks, mock_account):
    """Test get_cash."""
    trading_helper_with_mocks.client.get_account.return_value = mock_account

    cash = trading_helper_with_mocks.get_cash()

    assert cash == 50000.00


def test_get_portfolio_value(trading_helper_with_mocks, mock_account):
    """Test get_portfolio_value."""
    trading_helper_with_mocks.client.get_account.return_value = mock_account

    value = trading_helper_with_mocks.get_portfolio_value()

    assert value == 150000.00


# ==================== Dataclass Tests ====================


def test_position_info_from_position(mock_position):
    """Test PositionInfo.from_position."""
    position_info = PositionInfo.from_position(mock_position)

    assert position_info.symbol == "SPY"
    assert position_info.qty == 10.0
    assert position_info.market_value == 5000.00
    assert position_info.side == "long"


def test_position_info_handles_none_values():
    """Test PositionInfo handles None values gracefully."""
    position = MagicMock(spec=Position)
    position.symbol = "SPY"
    position.qty = None
    position.market_value = None
    position.avg_entry_price = None
    position.current_price = None
    position.unrealized_pl = None
    position.unrealized_plpc = None
    position.side = None
    position.cost_basis = None
    position.asset_id = UUID("12345678-1234-1234-1234-123456789012")

    position_info = PositionInfo.from_position(position)

    assert position_info.qty == 0.0
    assert position_info.market_value == 0.0
    assert position_info.side == "long"


def test_order_info_from_order(mock_order):
    """Test OrderInfo.from_order."""
    order_info = OrderInfo.from_order(mock_order)

    assert order_info.symbol == "SPY"
    assert order_info.qty == 10.0
    assert order_info.side == "buy"
    assert order_info.type == "market"
    assert order_info.status == "new"


def test_order_info_handles_none_values():
    """Test OrderInfo handles None values gracefully."""
    order = MagicMock(spec=Order)
    order.id = UUID("87654321-4321-4321-4321-210987654321")
    order.symbol = None
    order.qty = None
    order.notional = None
    order.side = None
    order.type = None
    order.status = None
    order.filled_qty = None
    order.filled_avg_price = None
    order.limit_price = None
    order.stop_price = None
    order.submitted_at = datetime(2025, 1, 1, 10, 0, 0)
    order.filled_at = None
    order.order_class = None

    order_info = OrderInfo.from_order(order)

    assert order_info.symbol == ""
    assert order_info.side == "buy"
    assert order_info.type == "market"


# ==================== TimeInForce Tests ====================


def test_buy_market_custom_time_in_force(trading_helper_with_mocks, mock_order):
    """Test buy_market with custom time_in_force."""
    trading_helper_with_mocks.client.submit_order.return_value = mock_order

    order_info = trading_helper_with_mocks.buy_market(
        "SPY", qty=10, time_in_force=TimeInForce.GTC
    )

    assert order_info.symbol == "SPY"
