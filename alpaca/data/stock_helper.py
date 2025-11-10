"""
Simplified Stock Data API for Alpaca.

This module provides a simplified interface for fetching stock market data,
eliminating the need to work with multiple request classes and complex API calls.

Example:
    >>> from alpaca.data.stock_helper import StockHelper
    >>> helper = StockHelper()  # Auto-loads API keys from environment
    >>> quote = helper.get_latest_quote("SPY")
    >>> bars = helper.get_bars("SPY", timeframe="1H", days_back=5)
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.models import Bar, Quote, Snapshot, Trade
from alpaca.data.requests import (
    StockBarsRequest,
    StockLatestBarRequest,
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockQuotesRequest,
    StockSnapshotRequest,
    StockTradesRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


@dataclass
class BarData:
    """Simplified bar (OHLCV) data."""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    trade_count: Optional[int] = None
    vwap: Optional[float] = None

    @classmethod
    def from_bar(cls, symbol: str, bar: Bar) -> "BarData":
        """Create BarData from API Bar object."""
        return cls(
            symbol=symbol,
            timestamp=bar.timestamp,
            open=float(bar.open),
            high=float(bar.high),
            low=float(bar.low),
            close=float(bar.close),
            volume=int(bar.volume),
            trade_count=int(bar.trade_count) if bar.trade_count else None,
            vwap=float(bar.vwap) if bar.vwap else None,
        )


@dataclass
class QuoteData:
    """Simplified quote (bid/ask) data."""

    symbol: str
    timestamp: datetime
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int
    conditions: Optional[List[str]] = None

    @classmethod
    def from_quote(cls, symbol: str, quote: Quote) -> "QuoteData":
        """Create QuoteData from API Quote object."""
        return cls(
            symbol=symbol,
            timestamp=quote.timestamp,
            bid_price=float(quote.bid_price),
            bid_size=int(quote.bid_size),
            ask_price=float(quote.ask_price),
            ask_size=int(quote.ask_size),
            conditions=quote.conditions if quote.conditions else None,
        )


@dataclass
class TradeData:
    """Simplified trade (tick) data."""

    symbol: str
    timestamp: datetime
    price: float
    size: int
    conditions: Optional[List[str]] = None
    exchange: Optional[str] = None

    @classmethod
    def from_trade(cls, symbol: str, trade: Trade) -> "TradeData":
        """Create TradeData from API Trade object."""
        return cls(
            symbol=symbol,
            timestamp=trade.timestamp,
            price=float(trade.price),
            size=int(trade.size),
            conditions=trade.conditions if trade.conditions else None,
            exchange=trade.exchange if hasattr(trade, "exchange") else None,
        )


@dataclass
class SnapshotData:
    """Simplified snapshot data with latest bar, quote, and trade."""

    symbol: str
    latest_trade: Optional[TradeData] = None
    latest_quote: Optional[QuoteData] = None
    latest_bar: Optional[BarData] = None
    prev_daily_bar: Optional[BarData] = None

    @classmethod
    def from_snapshot(cls, symbol: str, snapshot: Snapshot) -> "SnapshotData":
        """Create SnapshotData from API Snapshot object."""
        return cls(
            symbol=symbol,
            latest_trade=(
                TradeData.from_trade(symbol, snapshot.latest_trade)
                if snapshot.latest_trade
                else None
            ),
            latest_quote=(
                QuoteData.from_quote(symbol, snapshot.latest_quote)
                if snapshot.latest_quote
                else None
            ),
            latest_bar=(
                BarData.from_bar(symbol, snapshot.latest_bar)
                if snapshot.latest_bar
                else None
            ),
            prev_daily_bar=(
                BarData.from_bar(symbol, snapshot.prev_daily_bar)
                if snapshot.prev_daily_bar
                else None
            ),
        )


class StockHelper:
    """
    Simplified interface for Alpaca stock market data.

    This class provides easy-to-use methods for fetching stock data
    without requiring knowledge of the underlying request objects.

    Attributes:
        client: The underlying StockHistoricalDataClient instance.

    Example:
        >>> helper = StockHelper()
        >>> quote = helper.get_latest_quote("SPY")
        >>> print(f"Bid: ${quote.bid_price}, Ask: ${quote.ask_price}")
        >>> bars = helper.get_bars("SPY", timeframe="1H", days_back=5)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize StockHelper.

        Args:
            api_key: Alpaca API key. If None, reads from ALPACA_API_KEY env var.
            secret_key: Alpaca secret key. If None, reads from ALPACA_SECRET_KEY.

        Raises:
            ValueError: If API credentials are not provided and not in env vars.
        """
        # Load from environment if not provided
        if api_key is None:
            api_key = os.getenv("ALPACA_API_KEY")
        if secret_key is None:
            secret_key = os.getenv("ALPACA_SECRET_KEY")

        if not api_key or not secret_key:
            raise ValueError(
                "API key and secret key must be provided either as arguments "
                "or via ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables"
            )

        self.client = StockHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key,
        )

    def _parse_timeframe(self, timeframe: str) -> TimeFrame:
        """
        Parse simple timeframe string into TimeFrame object.

        Args:
            timeframe: Simple string like "1Min", "5Min", "1H", "1D"

        Returns:
            TimeFrame object

        Raises:
            ValueError: If timeframe format is invalid
        """
        timeframe = timeframe.strip()

        # Map of valid units
        unit_map = {
            "Min": TimeFrameUnit.Minute,
            "Hour": TimeFrameUnit.Hour,
            "H": TimeFrameUnit.Hour,
            "Day": TimeFrameUnit.Day,
            "D": TimeFrameUnit.Day,
            "Week": TimeFrameUnit.Week,
            "W": TimeFrameUnit.Week,
            "Month": TimeFrameUnit.Month,
            "M": TimeFrameUnit.Month,
        }

        # Try to parse amount and unit
        for unit_str, unit_enum in unit_map.items():
            if timeframe.endswith(unit_str):
                amount_str = timeframe[: -len(unit_str)]
                try:
                    amount = int(amount_str)
                    return TimeFrame(amount=amount, unit=unit_enum)
                except ValueError:
                    pass

        raise ValueError(
            f"Invalid timeframe '{timeframe}'. "
            "Use format like '1Min', '5Min', '1H', '1D', etc."
        )

    # ==================== Latest Data Methods ====================

    def get_latest_quote(self, symbol: str) -> QuoteData:
        """
        Get the latest quote for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").

        Returns:
            QuoteData with latest bid/ask.

        Example:
            >>> quote = helper.get_latest_quote("SPY")
            >>> print(f"Spread: ${quote.ask_price - quote.bid_price:.2f}")
        """
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        response = self.client.get_stock_latest_quote(request)

        if isinstance(response, dict) and symbol in response:
            return QuoteData.from_quote(symbol, response[symbol])

        raise ValueError(f"No quote data returned for {symbol}")

    def get_latest_quotes(self, symbols: List[str]) -> Dict[str, QuoteData]:
        """
        Get latest quotes for multiple symbols.

        Args:
            symbols: List of stock symbols.

        Returns:
            Dictionary mapping symbols to QuoteData.

        Example:
            >>> quotes = helper.get_latest_quotes(["SPY", "QQQ", "IWM"])
            >>> for symbol, quote in quotes.items():
            ...     print(f"{symbol}: ${quote.bid_price}")
        """
        request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
        response = self.client.get_stock_latest_quote(request)

        if isinstance(response, dict):
            return {
                symbol: QuoteData.from_quote(symbol, quote)
                for symbol, quote in response.items()
            }

        return {}

    def get_latest_bar(self, symbol: str) -> BarData:
        """
        Get the latest bar for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").

        Returns:
            BarData with latest OHLCV.

        Example:
            >>> bar = helper.get_latest_bar("SPY")
            >>> print(f"Close: ${bar.close:.2f}, Volume: {bar.volume:,}")
        """
        request = StockLatestBarRequest(symbol_or_symbols=symbol)
        response = self.client.get_stock_latest_bar(request)

        if isinstance(response, dict) and symbol in response:
            return BarData.from_bar(symbol, response[symbol])

        raise ValueError(f"No bar data returned for {symbol}")

    def get_latest_trade(self, symbol: str) -> TradeData:
        """
        Get the latest trade for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").

        Returns:
            TradeData with latest trade.

        Example:
            >>> trade = helper.get_latest_trade("SPY")
            >>> print(f"Last: ${trade.price:.2f} @ {trade.timestamp}")
        """
        request = StockLatestTradeRequest(symbol_or_symbols=symbol)
        response = self.client.get_stock_latest_trade(request)

        if isinstance(response, dict) and symbol in response:
            return TradeData.from_trade(symbol, response[symbol])

        raise ValueError(f"No trade data returned for {symbol}")

    # ==================== Historical Bar Methods ====================

    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[BarData]:
        """
        Get historical bars for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            timeframe: Bar interval (e.g., "1Min", "5Min", "1H", "1D").
            start: Start datetime (optional).
            end: End datetime (optional).
            days_back: Days back from now (alternative to start).
            limit: Maximum number of bars to return (optional).

        Returns:
            List of BarData objects.

        Example:
            >>> # Get last 5 days of hourly bars
            >>> bars = helper.get_bars("SPY", timeframe="1H", days_back=5)
            >>> # Get specific date range
            >>> bars = helper.get_bars(
            ...     "SPY",
            ...     timeframe="1D",
            ...     start=datetime(2024, 1, 1),
            ...     end=datetime(2024, 12, 31)
            ... )
        """
        # Handle days_back
        if days_back is not None and start is None:
            start = datetime.now() - timedelta(days=days_back)

        # Parse timeframe
        tf = self._parse_timeframe(timeframe)

        # Create request
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=start,
            end=end,
            limit=limit,
        )

        # Fetch data
        response = self.client.get_stock_bars(request)

        # Extract bars
        bars = []
        if hasattr(response, "data") and symbol in response.data:
            for bar in response.data[symbol]:
                bars.append(BarData.from_bar(symbol, bar))

        return bars

    def get_bars_multi(
        self,
        symbols: List[str],
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, List[BarData]]:
        """
        Get historical bars for multiple symbols.

        Args:
            symbols: List of stock symbols.
            timeframe: Bar interval (e.g., "1Min", "5Min", "1H", "1D").
            start: Start datetime (optional).
            end: End datetime (optional).
            days_back: Days back from now (alternative to start).
            limit: Maximum number of bars per symbol (optional).

        Returns:
            Dictionary mapping symbols to lists of BarData.

        Example:
            >>> bars = helper.get_bars_multi(
            ...     ["SPY", "QQQ", "IWM"],
            ...     timeframe="1H",
            ...     days_back=1
            ... )
        """
        # Handle days_back
        if days_back is not None and start is None:
            start = datetime.now() - timedelta(days=days_back)

        # Parse timeframe
        tf = self._parse_timeframe(timeframe)

        # Create request
        request = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=tf,
            start=start,
            end=end,
            limit=limit,
        )

        # Fetch data
        response = self.client.get_stock_bars(request)

        # Extract bars per symbol
        result = {}
        if hasattr(response, "data"):
            for symbol in symbols:
                if symbol in response.data:
                    result[symbol] = [
                        BarData.from_bar(symbol, bar)
                        for bar in response.data[symbol]
                    ]

        return result

    # ==================== Historical Quote Methods ====================

    def get_quotes(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[QuoteData]:
        """
        Get historical quotes for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            start: Start datetime (optional).
            end: End datetime (optional).
            days_back: Days back from now (alternative to start).
            limit: Maximum number of quotes to return (optional).

        Returns:
            List of QuoteData objects.

        Example:
            >>> quotes = helper.get_quotes("SPY", days_back=1, limit=100)
        """
        # Handle days_back
        if days_back is not None and start is None:
            start = datetime.now() - timedelta(days=days_back)

        # Create request
        request = StockQuotesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end,
            limit=limit,
        )

        # Fetch data
        response = self.client.get_stock_quotes(request)

        # Extract quotes
        quotes = []
        if hasattr(response, "data") and symbol in response.data:
            for quote in response.data[symbol]:
                quotes.append(QuoteData.from_quote(symbol, quote))

        return quotes

    # ==================== Historical Trade Methods ====================

    def get_trades(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[TradeData]:
        """
        Get historical trades for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").
            start: Start datetime (optional).
            end: End datetime (optional).
            days_back: Days back from now (alternative to start).
            limit: Maximum number of trades to return (optional).

        Returns:
            List of TradeData objects.

        Example:
            >>> trades = helper.get_trades("SPY", days_back=1, limit=100)
        """
        # Handle days_back
        if days_back is not None and start is None:
            start = datetime.now() - timedelta(days=days_back)

        # Create request
        request = StockTradesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end,
            limit=limit,
        )

        # Fetch data
        response = self.client.get_stock_trades(request)

        # Extract trades
        trades = []
        if hasattr(response, "data") and symbol in response.data:
            for trade in response.data[symbol]:
                trades.append(TradeData.from_trade(symbol, trade))

        return trades

    # ==================== Snapshot Methods ====================

    def get_snapshot(self, symbol: str) -> SnapshotData:
        """
        Get snapshot (latest bar, quote, and trade) for a symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY").

        Returns:
            SnapshotData with latest data.

        Example:
            >>> snapshot = helper.get_snapshot("SPY")
            >>> if snapshot.latest_quote:
            ...     print(f"Bid: ${snapshot.latest_quote.bid_price:.2f}")
        """
        request = StockSnapshotRequest(symbol_or_symbols=symbol)
        response = self.client.get_stock_snapshot(request)

        if isinstance(response, dict) and symbol in response:
            return SnapshotData.from_snapshot(symbol, response[symbol])

        raise ValueError(f"No snapshot data returned for {symbol}")

    def get_snapshots(self, symbols: List[str]) -> Dict[str, SnapshotData]:
        """
        Get snapshots for multiple symbols.

        Args:
            symbols: List of stock symbols.

        Returns:
            Dictionary mapping symbols to SnapshotData.

        Example:
            >>> snapshots = helper.get_snapshots(["SPY", "QQQ", "IWM"])
        """
        request = StockSnapshotRequest(symbol_or_symbols=symbols)
        response = self.client.get_stock_snapshot(request)

        if isinstance(response, dict):
            return {
                symbol: SnapshotData.from_snapshot(symbol, snapshot)
                for symbol, snapshot in response.items()
            }

        return {}
