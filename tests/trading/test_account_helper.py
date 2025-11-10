"""
Tests for AccountHelper simplified account management API.
"""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from alpaca.trading.account_helper import (
    AccountHelper,
    AccountInfo,
    PortfolioHistoryData,
)
from alpaca.trading.enums import AccountStatus
from alpaca.trading.models import PortfolioHistory, TradeAccount


# ==================== Fixtures ====================


@pytest.fixture
def mock_trade_account():
    """Create a mock TradeAccount object."""
    account = MagicMock(spec=TradeAccount)
    account.account_number = "123456789"
    account.status = AccountStatus.ACTIVE
    account.cash = "50000.00"
    account.buying_power = "100000.00"
    account.portfolio_value = "75000.00"
    account.equity = "75000.00"
    account.long_market_value = "25000.00"
    account.short_market_value = "0.00"
    account.initial_margin = "10000.00"
    account.maintenance_margin = "5000.00"
    account.last_equity = "74000.00"
    account.multiplier = "2"
    account.pattern_day_trader = False
    account.daytrade_count = 2
    account.daytrading_buying_power = "100000.00"
    account.regt_buying_power = "50000.00"
    account.trading_blocked = False
    account.account_blocked = False
    account.created_at = datetime(2024, 1, 1, 10, 0, 0)
    return account


@pytest.fixture
def mock_portfolio_history():
    """Create a mock PortfolioHistory object."""
    history = MagicMock(spec=PortfolioHistory)
    history.timestamp = [1704110400, 1704196800, 1704283200]  # 3 days
    history.equity = [70000.0, 72000.0, 75000.0]
    history.profit_loss = [0.0, 2000.0, 5000.0]
    history.profit_loss_pct = [0.0, 0.0286, 0.0714]
    history.base_value = 70000.0
    history.timeframe = "1D"
    return history


@pytest.fixture
def account_helper_with_mocks():
    """Create AccountHelper with mocked client."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "test_api_key",
            "ALPACA_SECRET_KEY": "test_secret_key",
            "ALPACA_PAPER": "true",
        },
    ):
        helper = AccountHelper()
        helper.client = MagicMock()
        return helper


# ==================== Initialization Tests ====================


def test_init_with_explicit_credentials():
    """Test initialization with explicit credentials."""
    helper = AccountHelper(
        api_key="test_key",
        secret_key="test_secret",
        paper=True
    )
    assert helper.api_key == "test_key"
    assert helper.secret_key == "test_secret"
    assert helper.paper is True


def test_init_from_environment():
    """Test initialization from environment variables."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "env_key",
            "ALPACA_SECRET_KEY": "env_secret",
            "ALPACA_PAPER": "true",
        },
    ):
        helper = AccountHelper()
        assert helper.api_key == "env_key"
        assert helper.secret_key == "env_secret"
        assert helper.paper is True


def test_init_paper_defaults_true():
    """Test that paper trading defaults to True."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "key",
            "ALPACA_SECRET_KEY": "secret",
        },
        clear=True,
    ):
        helper = AccountHelper()
        assert helper.paper is True


def test_init_paper_from_env_false():
    """Test paper trading from environment variable false."""
    with patch.dict(
        os.environ,
        {
            "ALPACA_API_KEY": "key",
            "ALPACA_SECRET_KEY": "secret",
            "ALPACA_PAPER": "false",
        },
    ):
        helper = AccountHelper()
        assert helper.paper is False


def test_init_missing_credentials():
    """Test that missing credentials raises ValueError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API credentials required"):
            AccountHelper()


# ==================== Account Info Tests ====================


def test_get_account(account_helper_with_mocks, mock_trade_account):
    """Test getting complete account information."""
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    account_info = account_helper_with_mocks.get_account()

    assert isinstance(account_info, AccountInfo)
    assert account_info.account_number == "123456789"
    assert account_info.status == "ACTIVE"
    assert account_info.cash == 50000.00
    assert account_info.buying_power == 100000.00
    assert account_info.portfolio_value == 75000.00


def test_get_cash(account_helper_with_mocks, mock_trade_account):
    """Test getting cash balance."""
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    cash = account_helper_with_mocks.get_cash()
    assert cash == 50000.00
    assert isinstance(cash, float)


def test_get_buying_power(account_helper_with_mocks, mock_trade_account):
    """Test getting buying power."""
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    bp = account_helper_with_mocks.get_buying_power()
    assert bp == 100000.00
    assert isinstance(bp, float)


def test_get_portfolio_value(account_helper_with_mocks, mock_trade_account):
    """Test getting portfolio value."""
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    value = account_helper_with_mocks.get_portfolio_value()
    assert value == 75000.00
    assert isinstance(value, float)


def test_get_equity(account_helper_with_mocks, mock_trade_account):
    """Test getting equity."""
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    equity = account_helper_with_mocks.get_equity()
    assert equity == 75000.00
    assert isinstance(equity, float)


# ==================== PDT Tests ====================


def test_is_pattern_day_trader_false(account_helper_with_mocks, mock_trade_account):
    """Test PDT status when not a pattern day trader."""
    mock_trade_account.pattern_day_trader = False
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    is_pdt = account_helper_with_mocks.is_pattern_day_trader()
    assert is_pdt is False


def test_is_pattern_day_trader_true(account_helper_with_mocks, mock_trade_account):
    """Test PDT status when flagged as pattern day trader."""
    mock_trade_account.pattern_day_trader = True
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    is_pdt = account_helper_with_mocks.is_pattern_day_trader()
    assert is_pdt is True


def test_get_day_trades_remaining(account_helper_with_mocks, mock_trade_account):
    """Test getting remaining day trades."""
    mock_trade_account.pattern_day_trader = False
    mock_trade_account.daytrade_count = 2
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    remaining = account_helper_with_mocks.get_day_trades_remaining()
    assert remaining == 1  # 3 - 2 = 1


def test_get_day_trades_remaining_zero_for_pdt(
    account_helper_with_mocks, mock_trade_account
):
    """Test that PDT accounts get 0 remaining day trades."""
    mock_trade_account.pattern_day_trader = True
    mock_trade_account.daytrade_count = 5
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    remaining = account_helper_with_mocks.get_day_trades_remaining()
    assert remaining == 0


def test_get_day_trades_remaining_all_available(
    account_helper_with_mocks, mock_trade_account
):
    """Test remaining day trades when none used."""
    mock_trade_account.pattern_day_trader = False
    mock_trade_account.daytrade_count = 0
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    remaining = account_helper_with_mocks.get_day_trades_remaining()
    assert remaining == 3


# ==================== Other Account Methods Tests ====================


def test_get_multiplier(account_helper_with_mocks, mock_trade_account):
    """Test getting margin multiplier."""
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    mult = account_helper_with_mocks.get_multiplier()
    assert mult == 2.0
    assert isinstance(mult, float)


def test_is_blocked_false(account_helper_with_mocks, mock_trade_account):
    """Test account is not blocked."""
    mock_trade_account.account_blocked = False
    mock_trade_account.trading_blocked = False
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    blocked = account_helper_with_mocks.is_blocked()
    assert blocked is False


def test_is_blocked_account(account_helper_with_mocks, mock_trade_account):
    """Test account is blocked."""
    mock_trade_account.account_blocked = True
    mock_trade_account.trading_blocked = False
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    blocked = account_helper_with_mocks.is_blocked()
    assert blocked is True


def test_is_blocked_trading(account_helper_with_mocks, mock_trade_account):
    """Test trading is blocked."""
    mock_trade_account.account_blocked = False
    mock_trade_account.trading_blocked = True
    account_helper_with_mocks.client.get_account.return_value = mock_trade_account

    blocked = account_helper_with_mocks.is_blocked()
    assert blocked is True


# ==================== Portfolio History Tests ====================


def test_get_portfolio_history(
    account_helper_with_mocks, mock_portfolio_history
):
    """Test getting portfolio history."""
    account_helper_with_mocks.client.get_portfolio_history.return_value = (
        mock_portfolio_history
    )

    history = account_helper_with_mocks.get_portfolio_history(
        period="1W", timeframe="1D"
    )

    assert isinstance(history, PortfolioHistoryData)
    assert len(history.timestamps) == 3
    assert len(history.equity) == 3
    assert history.equity[0] == 70000.0
    assert history.equity[-1] == 75000.0
    assert history.base_value == 70000.0


def test_get_portfolio_history_with_days_back(
    account_helper_with_mocks, mock_portfolio_history
):
    """Test getting portfolio history with days_back parameter."""
    account_helper_with_mocks.client.get_portfolio_history.return_value = (
        mock_portfolio_history
    )

    history = account_helper_with_mocks.get_portfolio_history(
        days_back=7, timeframe="1D"
    )

    assert isinstance(history, PortfolioHistoryData)
    assert len(history.timestamps) == 3

    # Verify request was made with dates
    call_args = account_helper_with_mocks.client.get_portfolio_history.call_args
    request = call_args[1]["filter"]
    assert request.start is not None
    assert request.end is not None


# ==================== Dataclass Conversion Tests ====================


def test_account_info_from_trade_account(mock_trade_account):
    """Test AccountInfo creation from TradeAccount."""
    account_info = AccountInfo.from_trade_account(mock_trade_account)

    assert account_info.account_number == "123456789"
    assert account_info.cash == 50000.00
    assert account_info.buying_power == 100000.00
    assert isinstance(account_info.cash, float)
    assert isinstance(account_info.buying_power, float)


def test_account_info_handles_none_values():
    """Test AccountInfo handles None values gracefully."""
    account = MagicMock(spec=TradeAccount)
    account.account_number = "123"
    account.status = None
    account.cash = None
    account.buying_power = None
    account.portfolio_value = None
    account.equity = None
    account.long_market_value = None
    account.short_market_value = None
    account.initial_margin = None
    account.maintenance_margin = None
    account.last_equity = None
    account.multiplier = None
    account.pattern_day_trader = None
    account.daytrade_count = None
    account.daytrading_buying_power = None
    account.regt_buying_power = None
    account.trading_blocked = None
    account.account_blocked = None
    account.created_at = None

    account_info = AccountInfo.from_trade_account(account)

    assert account_info.cash == 0.0
    assert account_info.buying_power == 0.0
    assert account_info.multiplier == 1.0
    assert account_info.pattern_day_trader is False
    assert account_info.daytrade_count == 0


def test_portfolio_history_data_from_portfolio_history(mock_portfolio_history):
    """Test PortfolioHistoryData creation from PortfolioHistory."""
    history_data = PortfolioHistoryData.from_portfolio_history(
        mock_portfolio_history
    )

    assert len(history_data.timestamps) == 3
    assert len(history_data.equity) == 3
    assert len(history_data.profit_loss) == 3
    assert history_data.base_value == 70000.0
    assert isinstance(history_data.timestamps[0], datetime)


def test_portfolio_history_handles_none_pct():
    """Test PortfolioHistoryData handles None percentages."""
    history = MagicMock(spec=PortfolioHistory)
    history.timestamp = [1704110400, 1704196800]
    history.equity = [70000.0, 72000.0]
    history.profit_loss = [0.0, 2000.0]
    history.profit_loss_pct = [None, 0.0286]  # First value is None
    history.base_value = 70000.0

    history_data = PortfolioHistoryData.from_portfolio_history(history)

    assert history_data.profit_loss_pct[0] == 0.0  # None converted to 0.0
    assert history_data.profit_loss_pct[1] == 0.0286


# ==================== Edge Cases ====================


def test_get_cash_when_none(account_helper_with_mocks):
    """Test getting cash when value is None."""
    account = MagicMock(spec=TradeAccount)
    account.cash = None
    account_helper_with_mocks.client.get_account.return_value = account

    cash = account_helper_with_mocks.get_cash()
    assert cash == 0.0


def test_get_multiplier_when_none(account_helper_with_mocks):
    """Test getting multiplier when value is None."""
    account = MagicMock(spec=TradeAccount)
    account.multiplier = None
    account_helper_with_mocks.client.get_account.return_value = account

    mult = account_helper_with_mocks.get_multiplier()
    assert mult == 1.0
