"""
Simplified Trading API for Alpaca.

This module provides a simplified interface for trading operations, eliminating
the need to work with multiple request classes and complex API calls.

Example:
    >>> from alpaca.trading.trading_helper import TradingHelper
    >>> helper = TradingHelper()  # Auto-loads API keys from environment
    >>> order = helper.buy_market("SPY", qty=10)
    >>> position = helper.get_position("SPY")
    >>> helper.close_position("SPY", percentage=50)
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    QueryOrderStatus,
    TimeInForce,
)
from alpaca.trading.models import Order, Position
from alpaca.trading.requests import (
    ClosePositionRequest,
    GetOrdersRequest,
    LimitOrderRequest,
    MarketOrderRequest,
    StopLossRequest,
    TakeProfitRequest,
)


@dataclass
class PositionInfo:
    """Simplified position information."""

    symbol: str
    qty: float
    market_value: float
    avg_entry_price: float
    current_price: float
    unrealized_pl: float
    unrealized_plpc: float
    side: str  # 'long' or 'short'
    cost_basis: float
    asset_id: str

    @classmethod
    def from_position(cls, position: Position) -> "PositionInfo":
        """Create PositionInfo from API Position object."""
        return cls(
            symbol=position.symbol,
            qty=float(position.qty) if position.qty else 0.0,
            market_value=float(position.market_value) if position.market_value else 0.0,
            avg_entry_price=float(position.avg_entry_price) if position.avg_entry_price else 0.0,
            current_price=float(position.current_price) if position.current_price else 0.0,
            unrealized_pl=float(position.unrealized_pl) if position.unrealized_pl else 0.0,
            unrealized_plpc=float(position.unrealized_plpc) if position.unrealized_plpc else 0.0,
            side=position.side.value if position.side else "long",
            cost_basis=float(position.cost_basis) if position.cost_basis else 0.0,
            asset_id=str(position.asset_id),
        )


@dataclass
class OrderInfo:
    """Simplified order information."""

    id: str
    symbol: str
    qty: Optional[float]
    notional: Optional[float]
    side: str  # 'buy' or 'sell'
    type: str  # 'market', 'limit', 'stop', etc.
    status: str
    filled_qty: float
    filled_avg_price: Optional[float]
    limit_price: Optional[float]
    stop_price: Optional[float]
    submitted_at: datetime
    filled_at: Optional[datetime]
    order_class: Optional[str]

    @classmethod
    def from_order(cls, order: Order) -> "OrderInfo":
        """Create OrderInfo from API Order object."""
        return cls(
            id=str(order.id),
            symbol=order.symbol if order.symbol else "",
            qty=float(order.qty) if order.qty else None,
            notional=float(order.notional) if order.notional else None,
            side=order.side.value if order.side else "buy",
            type=order.type.value if order.type else "market",
            status=order.status.value if order.status else "unknown",
            filled_qty=float(order.filled_qty) if order.filled_qty else 0.0,
            filled_avg_price=(
                float(order.filled_avg_price) if order.filled_avg_price else None
            ),
            limit_price=float(order.limit_price) if order.limit_price else None,
            stop_price=float(order.stop_price) if order.stop_price else None,
            submitted_at=order.submitted_at,
            filled_at=order.filled_at,
            order_class=order.order_class.value if order.order_class else None,
        )


class TradingHelper:
    """
    Simplified interface for Alpaca trading operations.

    This class provides easy-to-use methods for common trading operations
    without requiring knowledge of the underlying request objects.

    Attributes:
        client: The underlying TradingClient instance.

    Example:
        >>> helper = TradingHelper()
        >>> order = helper.buy_market("SPY", qty=10)
        >>> position = helper.get_position("SPY")
        >>> helper.close_position("SPY")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: Optional[bool] = None,
    ):
        """
        Initialize TradingHelper.

        Args:
            api_key: Alpaca API key. If None, reads from ALPACA_API_KEY env var.
            secret_key: Alpaca secret key. If None, reads from ALPACA_SECRET_KEY.
            paper: Use paper trading. If None, reads from ALPACA_PAPER env var
                   (defaults to True if not set).

        Raises:
            ValueError: If API credentials are not provided and not in env vars.
        """
        # Load from environment if not provided
        if api_key is None:
            api_key = os.getenv("ALPACA_API_KEY")
        if secret_key is None:
            secret_key = os.getenv("ALPACA_SECRET_KEY")
        if paper is None:
            paper_env = os.getenv("ALPACA_PAPER", "true").lower()
            paper = paper_env in ("true", "1", "yes", "t")

        if not api_key or not secret_key:
            raise ValueError(
                "API key and secret key must be provided either as arguments "
                "or via ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables"
            )

        self.client = TradingClient(
            api_key=api_key,
            secret_key=secret_key,
            paper=paper,
        )
        self._paper = paper

    @property
    def is_paper(self) -> bool:
        """Check if using paper trading."""
        return self._paper

    # ==================== Market Orders ====================

    def buy_market(
        self,
        symbol: str,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY,
    ) -> OrderInfo:
        """
        Place a market buy order.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to buy. Use either qty or notional, not both.
            notional: Dollar amount to buy. Use either qty or notional, not both.
            time_in_force: Order duration (DAY, GTC, IOC, FOK). Defaults to DAY.

        Returns:
            OrderInfo with order details.

        Raises:
            ValueError: If neither qty nor notional is provided, or both are.

        Example:
            >>> order = helper.buy_market("SPY", qty=10)
            >>> order = helper.buy_market("SPY", notional=1000.0)
        """
        if (qty is None and notional is None) or (
            qty is not None and notional is not None
        ):
            raise ValueError("Must provide exactly one of qty or notional")

        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=OrderSide.BUY,
            time_in_force=time_in_force,
        )

        order = self.client.submit_order(request)
        return OrderInfo.from_order(order)

    def sell_market(
        self,
        symbol: str,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY,
    ) -> OrderInfo:
        """
        Place a market sell order.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to sell. Use either qty or notional, not both.
            notional: Dollar amount to sell. Use either qty or notional, not both.
            time_in_force: Order duration (DAY, GTC, IOC, FOK). Defaults to DAY.

        Returns:
            OrderInfo with order details.

        Raises:
            ValueError: If neither qty nor notional is provided, or both are.

        Example:
            >>> order = helper.sell_market("SPY", qty=10)
        """
        if (qty is None and notional is None) or (
            qty is not None and notional is not None
        ):
            raise ValueError("Must provide exactly one of qty or notional")

        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=OrderSide.SELL,
            time_in_force=time_in_force,
        )

        order = self.client.submit_order(request)
        return OrderInfo.from_order(order)

    # ==================== Limit Orders ====================

    def buy_limit(
        self,
        symbol: str,
        qty: float,
        limit_price: float,
        time_in_force: TimeInForce = TimeInForce.DAY,
    ) -> OrderInfo:
        """
        Place a limit buy order.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to buy.
            limit_price: Maximum price to pay per share.
            time_in_force: Order duration (DAY, GTC, IOC, FOK). Defaults to DAY.

        Returns:
            OrderInfo with order details.

        Example:
            >>> order = helper.buy_limit("SPY", qty=10, limit_price=450.00)
        """
        request = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            limit_price=limit_price,
            side=OrderSide.BUY,
            time_in_force=time_in_force,
        )

        order = self.client.submit_order(request)
        return OrderInfo.from_order(order)

    def sell_limit(
        self,
        symbol: str,
        qty: float,
        limit_price: float,
        time_in_force: TimeInForce = TimeInForce.DAY,
    ) -> OrderInfo:
        """
        Place a limit sell order.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to sell.
            limit_price: Minimum price to accept per share.
            time_in_force: Order duration (DAY, GTC, IOC, FOK). Defaults to DAY.

        Returns:
            OrderInfo with order details.

        Example:
            >>> order = helper.sell_limit("SPY", qty=10, limit_price=550.00)
        """
        request = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            limit_price=limit_price,
            side=OrderSide.SELL,
            time_in_force=time_in_force,
        )

        order = self.client.submit_order(request)
        return OrderInfo.from_order(order)

    # ==================== Bracket Orders ====================

    def buy_with_bracket(
        self,
        symbol: str,
        qty: float,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        stop_loss_limit: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY,
    ) -> OrderInfo:
        """
        Place a market buy order with stop loss and/or take profit.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to buy.
            take_profit: Price to take profit (optional).
            stop_loss: Stop loss trigger price (required if stop_loss_limit).
            stop_loss_limit: Stop loss limit price (optional, creates stop-limit).
            time_in_force: Order duration (DAY, GTC). Defaults to DAY.

        Returns:
            OrderInfo with order details.

        Raises:
            ValueError: If neither take_profit nor stop_loss is provided.

        Example:
            >>> # Buy with both stop loss and take profit
            >>> order = helper.buy_with_bracket(
            ...     "SPY", qty=10, stop_loss=450.00, take_profit=550.00
            ... )
            >>> # Buy with just stop loss
            >>> order = helper.buy_with_bracket("SPY", qty=10, stop_loss=450.00)
        """
        if stop_loss_limit is not None and stop_loss is None:
            raise ValueError("stop_loss is required when using stop_loss_limit")

        if take_profit is None and stop_loss is None:
            raise ValueError("Must provide at least one of take_profit or stop_loss")

        take_profit_obj = (
            TakeProfitRequest(limit_price=take_profit) if take_profit else None
        )
        stop_loss_obj = None
        if stop_loss is not None:
            if stop_loss_limit is not None:
                stop_loss_obj = StopLossRequest(
                    stop_price=stop_loss, limit_price=stop_loss_limit
                )
            else:
                stop_loss_obj = StopLossRequest(stop_price=stop_loss)

        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=time_in_force,
            order_class=OrderClass.BRACKET,
            take_profit=take_profit_obj,
            stop_loss=stop_loss_obj,
        )

        order = self.client.submit_order(request)
        return OrderInfo.from_order(order)

    def sell_with_bracket(
        self,
        symbol: str,
        qty: float,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        stop_loss_limit: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY,
    ) -> OrderInfo:
        """
        Place a market sell order with stop loss and/or take profit.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to sell (short).
            take_profit: Price to take profit (optional).
            stop_loss: Stop loss trigger price (required if stop_loss_limit).
            stop_loss_limit: Stop loss limit price (optional, creates stop-limit).
            time_in_force: Order duration (DAY, GTC). Defaults to DAY.

        Returns:
            OrderInfo with order details.

        Raises:
            ValueError: If neither take_profit nor stop_loss is provided.

        Example:
            >>> # Sell short with stop loss and take profit
            >>> order = helper.sell_with_bracket(
            ...     "SPY", qty=10, stop_loss=550.00, take_profit=450.00
            ... )
        """
        if stop_loss_limit is not None and stop_loss is None:
            raise ValueError("stop_loss is required when using stop_loss_limit")

        if take_profit is None and stop_loss is None:
            raise ValueError("Must provide at least one of take_profit or stop_loss")

        take_profit_obj = (
            TakeProfitRequest(limit_price=take_profit) if take_profit else None
        )
        stop_loss_obj = None
        if stop_loss is not None:
            if stop_loss_limit is not None:
                stop_loss_obj = StopLossRequest(
                    stop_price=stop_loss, limit_price=stop_loss_limit
                )
            else:
                stop_loss_obj = StopLossRequest(stop_price=stop_loss)

        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=time_in_force,
            order_class=OrderClass.BRACKET,
            take_profit=take_profit_obj,
            stop_loss=stop_loss_obj,
        )

        order = self.client.submit_order(request)
        return OrderInfo.from_order(order)

    # ==================== Position Management ====================

    def get_position(self, symbol: str) -> PositionInfo:
        """
        Get current position for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").

        Returns:
            PositionInfo with position details.

        Raises:
            Exception: If no position exists for the symbol.

        Example:
            >>> position = helper.get_position("SPY")
            >>> print(f"Qty: {position.qty}, P&L: ${position.unrealized_pl:.2f}")
        """
        position = self.client.get_open_position(symbol)
        return PositionInfo.from_position(position)

    def get_all_positions(self) -> List[PositionInfo]:
        """
        Get all current positions.

        Returns:
            List of PositionInfo objects.

        Example:
            >>> positions = helper.get_all_positions()
            >>> for pos in positions:
            ...     print(f"{pos.symbol}: {pos.qty} shares, P&L: ${pos.unrealized_pl}")
        """
        positions = self.client.get_all_positions()
        return [PositionInfo.from_position(p) for p in positions]

    def close_position(
        self,
        symbol: str,
        qty: Optional[float] = None,
        percentage: Optional[float] = None,
    ) -> OrderInfo:
        """
        Close position (all or partial).

        Args:
            symbol: Stock symbol (e.g., "SPY").
            qty: Number of shares to close (optional).
            percentage: Percentage of position to close (optional).

        Returns:
            OrderInfo with order details.

        Raises:
            ValueError: If both qty and percentage are provided, or neither.

        Example:
            >>> # Close entire position
            >>> order = helper.close_position("SPY")
            >>> # Close half the position
            >>> order = helper.close_position("SPY", percentage=50)
            >>> # Close specific quantity
            >>> order = helper.close_position("SPY", qty=5)
        """
        if qty is None and percentage is None:
            # Close entire position
            response = self.client.close_position(symbol)
        else:
            if qty is not None and percentage is not None:
                raise ValueError("Cannot specify both qty and percentage")

            request = ClosePositionRequest(
                qty=str(qty) if qty is not None else None,
                percentage=str(percentage) if percentage is not None else None,
            )
            response = self.client.close_position(symbol, request)

        return OrderInfo.from_order(response)

    # ==================== Order Management ====================

    def get_order(self, order_id: Union[str, UUID]) -> OrderInfo:
        """
        Get order by ID.

        Args:
            order_id: Order ID (string or UUID).

        Returns:
            OrderInfo with order details.

        Example:
            >>> order = helper.get_order("a1b2c3d4-...")
        """
        order = self.client.get_order_by_id(order_id)
        return OrderInfo.from_order(order)

    def get_orders(
        self,
        status: Optional[QueryOrderStatus] = None,
        symbols: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[OrderInfo]:
        """
        Get orders with optional filtering.

        Args:
            status: Filter by status (OPEN, CLOSED, ALL). Defaults to OPEN.
            symbols: Filter by symbols (optional).
            limit: Maximum number of orders to return (optional).

        Returns:
            List of OrderInfo objects.

        Example:
            >>> # Get all open orders
            >>> orders = helper.get_orders()
            >>> # Get all orders for SPY
            >>> orders = helper.get_orders(status=QueryOrderStatus.ALL, symbols=["SPY"])
        """
        if status is None:
            status = QueryOrderStatus.OPEN

        request = GetOrdersRequest(status=status, symbols=symbols, limit=limit)
        orders = self.client.get_orders(request)
        return [OrderInfo.from_order(o) for o in orders]

    def cancel_order(self, order_id: Union[str, UUID]) -> None:
        """
        Cancel an order.

        Args:
            order_id: Order ID (string or UUID).

        Example:
            >>> helper.cancel_order("a1b2c3d4-...")
        """
        self.client.cancel_order_by_id(order_id)

    def cancel_all_orders(self) -> None:
        """
        Cancel all open orders.

        Example:
            >>> helper.cancel_all_orders()
        """
        self.client.cancel_orders()

    # ==================== Account Info ====================

    def get_buying_power(self) -> float:
        """
        Get current buying power.

        Returns:
            Buying power as float.

        Example:
            >>> bp = helper.get_buying_power()
            >>> print(f"Buying power: ${bp:,.2f}")
        """
        from alpaca.trading.models import TradeAccount
        account = self.client.get_account()
        if isinstance(account, TradeAccount):
            return float(account.buying_power) if account.buying_power else 0.0
        return 0.0

    def get_cash(self) -> float:
        """
        Get current cash balance.

        Returns:
            Cash balance as float.

        Example:
            >>> cash = helper.get_cash()
            >>> print(f"Cash: ${cash:,.2f}")
        """
        from alpaca.trading.models import TradeAccount
        account = self.client.get_account()
        if isinstance(account, TradeAccount):
            return float(account.cash) if account.cash else 0.0
        return 0.0

    def get_portfolio_value(self) -> float:
        """
        Get total portfolio value.

        Returns:
            Portfolio value as float.

        Example:
            >>> value = helper.get_portfolio_value()
            >>> print(f"Portfolio: ${value:,.2f}")
        """
        from alpaca.trading.models import TradeAccount
        account = self.client.get_account()
        if isinstance(account, TradeAccount):
            return float(account.portfolio_value) if account.portfolio_value else 0.0
        return 0.0
