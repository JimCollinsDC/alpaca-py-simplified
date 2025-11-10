"""
Simplified Account API for Alpaca.

This module provides a simplified interface for account management,
eliminating the need to work with complex API calls and string conversions.

Example:
    >>> from alpaca.trading.account_helper import AccountHelper
    >>> helper = AccountHelper()  # Auto-loads API keys from environment
    >>> print(f"Cash: ${helper.get_cash():,.2f}")
    >>> print(f"Portfolio: ${helper.get_portfolio_value():,.2f}")
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.models import PortfolioHistory, TradeAccount
from alpaca.trading.requests import GetPortfolioHistoryRequest


@dataclass
class AccountInfo:
    """Simplified account information."""

    account_number: str
    status: str
    cash: float
    buying_power: float
    portfolio_value: float
    equity: float
    long_market_value: float
    short_market_value: float
    initial_margin: float
    maintenance_margin: float
    last_equity: float
    multiplier: float
    pattern_day_trader: bool
    daytrade_count: int
    daytrading_buying_power: float
    regt_buying_power: float
    trading_blocked: bool
    account_blocked: bool
    created_at: datetime

    @classmethod
    def from_trade_account(cls, account: TradeAccount) -> "AccountInfo":
        """Create AccountInfo from API TradeAccount object."""
        return cls(
            account_number=account.account_number,
            status=account.status.value if account.status else "UNKNOWN",
            cash=float(account.cash) if account.cash else 0.0,
            buying_power=float(account.buying_power) if account.buying_power else 0.0,
            portfolio_value=(
                float(account.portfolio_value) if account.portfolio_value else 0.0
            ),
            equity=float(account.equity) if account.equity else 0.0,
            long_market_value=(
                float(account.long_market_value) if account.long_market_value else 0.0
            ),
            short_market_value=(
                float(account.short_market_value)
                if account.short_market_value
                else 0.0
            ),
            initial_margin=(
                float(account.initial_margin) if account.initial_margin else 0.0
            ),
            maintenance_margin=(
                float(account.maintenance_margin)
                if account.maintenance_margin
                else 0.0
            ),
            last_equity=float(account.last_equity) if account.last_equity else 0.0,
            multiplier=float(account.multiplier) if account.multiplier else 1.0,
            pattern_day_trader=account.pattern_day_trader or False,
            daytrade_count=account.daytrade_count or 0,
            daytrading_buying_power=(
                float(account.daytrading_buying_power)
                if account.daytrading_buying_power
                else 0.0
            ),
            regt_buying_power=(
                float(account.regt_buying_power) if account.regt_buying_power else 0.0
            ),
            trading_blocked=account.trading_blocked or False,
            account_blocked=account.account_blocked or False,
            created_at=account.created_at or datetime.now(),
        )


@dataclass
class PortfolioHistoryData:
    """Simplified portfolio history data."""

    timestamps: List[datetime]
    equity: List[float]
    profit_loss: List[float]
    profit_loss_pct: List[float]
    base_value: float

    @classmethod
    def from_portfolio_history(
        cls, history: PortfolioHistory
    ) -> "PortfolioHistoryData":
        """Create PortfolioHistoryData from API PortfolioHistory object."""
        return cls(
            timestamps=[
                datetime.fromtimestamp(ts) for ts in history.timestamp
            ],
            equity=history.equity,
            profit_loss=history.profit_loss,
            profit_loss_pct=[
                pct if pct is not None else 0.0
                for pct in history.profit_loss_pct
            ],
            base_value=history.base_value or 0.0,
        )


class AccountHelper:
    """
    Simplified helper for account management with Alpaca.

    This class eliminates the complexity of working with account data
    and provides a clean, simple API for account information.

    Features:
        - Automatic API key loading from environment variables
        - Python native types (float, int) instead of strings
        - Simple method calls without request objects
        - Portfolio history with easy date range specification
        - Pattern day trader status and day trade count

    Environment Variables:
        - ALPACA_API_KEY: Your Alpaca API key
        - ALPACA_SECRET_KEY: Your Alpaca secret key
        - ALPACA_PAPER: Set to "true" for paper trading (default: true)

    Example:
        >>> helper = AccountHelper()
        >>> print(f"Cash: ${helper.get_cash():,.2f}")
        >>> print(f"Buying Power: ${helper.get_buying_power():,.2f}")
        >>> print(f"Portfolio: ${helper.get_portfolio_value():,.2f}")
        >>> if helper.is_pattern_day_trader():
        ...     print(f"Day trades left: {helper.get_day_trades_remaining()}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: Optional[bool] = None,
    ):
        """
        Initialize the AccountHelper.

        Args:
            api_key: Alpaca API key (if None, loads from ALPACA_API_KEY env)
            secret_key: Alpaca secret key (if None, loads from env)
            paper: Use paper trading (if None, defaults to True)
        """
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")

        # Default to paper trading unless explicitly set
        if paper is None:
            paper_env = os.getenv("ALPACA_PAPER", "true").lower()
            paper = paper_env in ("true", "1", "yes")

        self.paper = paper

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "API credentials required. Set ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY environment variables or pass them "
                "explicitly."
            )

        self.client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=self.paper,
        )

    def get_account(self) -> AccountInfo:
        """
        Get complete account information.

        Returns:
            AccountInfo with all account details

        Example:
            >>> account = helper.get_account()
            >>> print(f"Status: {account.status}")
            >>> print(f"Cash: ${account.cash:,.2f}")
            >>> print(f"Equity: ${account.equity:,.2f}")
        """
        account = self.client.get_account()
        return AccountInfo.from_trade_account(account)

    def get_cash(self) -> float:
        """
        Get current cash balance.

        Returns:
            Cash balance as float

        Example:
            >>> cash = helper.get_cash()
            >>> print(f"Available cash: ${cash:,.2f}")
        """
        account = self.client.get_account()
        return float(account.cash) if account.cash else 0.0

    def get_buying_power(self) -> float:
        """
        Get current buying power.

        Buying power is the amount of money available to buy securities.
        For margin accounts, this includes leverage.

        Returns:
            Buying power as float

        Example:
            >>> bp = helper.get_buying_power()
            >>> print(f"Buying power: ${bp:,.2f}")
        """
        account = self.client.get_account()
        return float(account.buying_power) if account.buying_power else 0.0

    def get_portfolio_value(self) -> float:
        """
        Get total portfolio value (cash + positions).

        Returns:
            Portfolio value as float

        Example:
            >>> value = helper.get_portfolio_value()
            >>> print(f"Portfolio value: ${value:,.2f}")
        """
        account = self.client.get_account()
        return float(account.portfolio_value) if account.portfolio_value else 0.0

    def get_equity(self) -> float:
        """
        Get current equity (cash + long positions - short positions).

        Returns:
            Equity as float

        Example:
            >>> equity = helper.get_equity()
            >>> print(f"Account equity: ${equity:,.2f}")
        """
        account = self.client.get_account()
        return float(account.equity) if account.equity else 0.0

    def is_pattern_day_trader(self) -> bool:
        """
        Check if account is flagged as a pattern day trader.

        A pattern day trader has made 4+ day trades in the last 5 trading days.
        PDT accounts must maintain $25,000 minimum equity.

        Returns:
            True if account is flagged as PDT

        Example:
            >>> if helper.is_pattern_day_trader():
            ...     print("Account is a Pattern Day Trader")
        """
        account = self.client.get_account()
        return account.pattern_day_trader or False

    def get_day_trades_remaining(self) -> int:
        """
        Get number of day trades remaining before PDT flag.

        Returns 0 if already a pattern day trader.

        Returns:
            Number of day trades remaining (0-3)

        Example:
            >>> remaining = helper.get_day_trades_remaining()
            >>> print(f"Day trades remaining: {remaining}")
        """
        account = self.client.get_account()

        if account.pattern_day_trader:
            return 0

        day_trade_count = account.daytrade_count or 0
        # PDT flag kicks in at 4 day trades
        return max(0, 3 - day_trade_count)

    def get_multiplier(self) -> float:
        """
        Get account's margin multiplier.

        Returns:
            Margin multiplier (typically 2 or 4)

        Example:
            >>> mult = helper.get_multiplier()
            >>> print(f"Margin multiplier: {mult}x")
        """
        account = self.client.get_account()
        return float(account.multiplier) if account.multiplier else 1.0

    def is_blocked(self) -> bool:
        """
        Check if account or trading is blocked.

        Returns:
            True if account or trading is blocked

        Example:
            >>> if helper.is_blocked():
            ...     print("Account is blocked!")
        """
        account = self.client.get_account()
        return (account.account_blocked or False) or (
            account.trading_blocked or False
        )

    def get_portfolio_history(
        self,
        period: Optional[str] = None,
        timeframe: Optional[str] = None,
        days_back: Optional[int] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> PortfolioHistoryData:
        """
        Get portfolio value history over time.

        Args:
            period: Time period - "1D", "1W", "1M", "3M", "1A", "all"
            timeframe: Data resolution - "1Min", "5Min", "15Min", "1H", "1D"
            days_back: Alternative to period - get last N days
            start: Start datetime (alternative to period/days_back)
            end: End datetime

        Returns:
            PortfolioHistoryData with timestamps and values

        Example:
            >>> # Get last 30 days of daily history
            >>> history = helper.get_portfolio_history(days_back=30, timeframe="1D")
            >>> for ts, equity in zip(history.timestamps, history.equity):
            ...     print(f"{ts.date()}: ${equity:,.2f}")
        """
        # Auto-calculate dates if days_back provided
        if days_back and not start:
            end = end or datetime.now()
            start = end - timedelta(days=days_back)

        request = GetPortfolioHistoryRequest(
            period=period,
            timeframe=timeframe,
            start=start,
            end=end,
        )

        history = self.client.get_portfolio_history(filter=request)
        return PortfolioHistoryData.from_portfolio_history(history)
