"""
Simplified Crypto Data API for Alpaca.

This module provides a simplified interface for fetching cryptocurrency
market data, eliminating the need to work with multiple request classes
and complex API calls.

Example:
    >>> from alpaca.data.crypto_helper import CryptoHelper
    >>> helper = CryptoHelper()  # Auto-loads API keys from environment
    >>> quote = helper.get_latest_quote("BTC/USD")
    >>> bars = helper.get_bars("BTC/USD", timeframe="1H", days_back=5)
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.models import Bar, Quote, Snapshot, Trade
from alpaca.data.requests import (
    CryptoBarsRequest,
    CryptoLatestBarRequest,
    CryptoLatestQuoteRequest,
    CryptoLatestTradeRequest,
    CryptoSnapshotRequest,
    CryptoTradesRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


@dataclass
class CryptoBarData:
    """Simplified cryptocurrency bar (OHLCV) data."""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: Optional[int] = None
    vwap: Optional[float] = None

    @classmethod
    def from_bar(cls, symbol: str, bar: Bar) -> "CryptoBarData":
        """Create CryptoBarData from API Bar object."""
        return cls(
            symbol=symbol,
            timestamp=bar.timestamp,
            open=float(bar.open),
            high=float(bar.high),
            low=float(bar.low),
            close=float(bar.close),
            volume=float(bar.volume),
            trade_count=int(bar.trade_count) if bar.trade_count else None,
            vwap=float(bar.vwap) if bar.vwap else None,
        )


@dataclass
class CryptoQuoteData:
    """Simplified cryptocurrency quote (bid/ask) data."""

    symbol: str
    timestamp: datetime
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float

    @classmethod
    def from_quote(cls, symbol: str, quote: Quote) -> "CryptoQuoteData":
        """Create CryptoQuoteData from API Quote object."""
        return cls(
            symbol=symbol,
            timestamp=quote.timestamp,
            bid_price=float(quote.bid_price),
            bid_size=float(quote.bid_size),
            ask_price=float(quote.ask_price),
            ask_size=float(quote.ask_size),
        )


@dataclass
class CryptoTradeData:
    """Simplified cryptocurrency trade (tick) data."""

    symbol: str
    timestamp: datetime
    price: float
    size: float
    taker_side: Optional[str] = None

    @classmethod
    def from_trade(cls, symbol: str, trade: Trade) -> "CryptoTradeData":
        """Create CryptoTradeData from API Trade object."""
        return cls(
            symbol=symbol,
            timestamp=trade.timestamp,
            price=float(trade.price),
            size=float(trade.size),
            taker_side=trade.taker_side if hasattr(trade, 'taker_side') else None,
        )


@dataclass
class CryptoSnapshotData:
    """Simplified cryptocurrency snapshot (latest market data)."""

    symbol: str
    latest_trade: Optional[CryptoTradeData] = None
    latest_quote: Optional[CryptoQuoteData] = None
    latest_bar: Optional[CryptoBarData] = None
    prev_daily_bar: Optional[CryptoBarData] = None

    @classmethod
    def from_snapshot(cls, symbol: str, snapshot: Snapshot) -> "CryptoSnapshotData":
        """Create CryptoSnapshotData from API Snapshot object."""
        return cls(
            symbol=symbol,
            latest_trade=(
                CryptoTradeData.from_trade(symbol, snapshot.latest_trade)
                if snapshot.latest_trade else None
            ),
            latest_quote=(
                CryptoQuoteData.from_quote(symbol, snapshot.latest_quote)
                if snapshot.latest_quote else None
            ),
            latest_bar=(
                CryptoBarData.from_bar(symbol, snapshot.minute_bar)
                if snapshot.minute_bar else None
            ),
            prev_daily_bar=(
                CryptoBarData.from_bar(symbol, snapshot.previous_daily_bar)
                if snapshot.previous_daily_bar else None
            ),
        )


class CryptoHelper:
    """
    Simplified helper for cryptocurrency market data from Alpaca.

    This class eliminates the complexity of working with request objects
    and provides a clean, simple API for fetching crypto market data.

    Features:
        - Automatic API key loading from environment variables
        - Simple timeframe strings (e.g., "1Min", "5Min", "1H", "1D")
        - Clean dataclass returns with Python native types (float, int)
        - Automatic date range calculation with `days_back` parameter
        - Multi-symbol support for all data types
        - Latest data (real-time) access

    Environment Variables:
        - ALPACA_API_KEY: Your Alpaca API key
        - ALPACA_SECRET_KEY: Your Alpaca secret key

    Example:
        >>> helper = CryptoHelper()
        >>> # Get latest quote for Bitcoin
        >>> quote = helper.get_latest_quote("BTC/USD")
        >>> print(f"BTC: ${quote.ask_price:,.2f}")
        >>>
        >>> # Get hourly bars for the past 7 days
        >>> bars = helper.get_bars("ETH/USD", timeframe="1H", days_back=7)
        >>> for bar in bars:
        ...     print(f"{bar.timestamp}: ${bar.close:,.2f}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize the CryptoHelper.

        Args:
            api_key: Alpaca API key (if None, loads from ALPACA_API_KEY env)
            secret_key: Alpaca secret key (if None, loads from env)

        Note:
            Crypto data does not require authentication, but authenticating
            increases your data rate limit.
        """
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")

        self.client = CryptoHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
        )

    def _parse_timeframe(self, timeframe: str) -> TimeFrame:
        """
        Parse a simple timeframe string into a TimeFrame object.

        Args:
            timeframe: Simple string like "1Min", "5Min", "1H", "1D"

        Returns:
            TimeFrame object for API requests

        Raises:
            ValueError: If timeframe format is invalid
        """
        timeframe = timeframe.strip()

        # Parse amount and unit
        if timeframe.endswith("Min"):
            amount = int(timeframe[:-3])
            unit = TimeFrameUnit.Minute
        elif timeframe.endswith("H") or timeframe.endswith("Hour"):
            amount = int(timeframe[:-1] if timeframe.endswith("H") else timeframe[:-4])
            unit = TimeFrameUnit.Hour
        elif timeframe.endswith("D") or timeframe.endswith("Day"):
            amount = int(timeframe[:-1] if timeframe.endswith("D") else timeframe[:-3])
            unit = TimeFrameUnit.Day
        elif timeframe.endswith("W") or timeframe.endswith("Week"):
            amount = int(timeframe[:-1] if timeframe.endswith("W") else timeframe[:-4])
            unit = TimeFrameUnit.Week
        elif timeframe.endswith("M") or timeframe.endswith("Month"):
            amount = int(timeframe[:-1] if timeframe.endswith("M") else timeframe[:-5])
            unit = TimeFrameUnit.Month
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        return TimeFrame(amount=amount, unit=unit)

    def get_latest_quote(self, symbol: str) -> Optional[CryptoQuoteData]:
        """
        Get the latest quote (bid/ask) for a cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., "BTC/USD", "ETH/USD")

        Returns:
            CryptoQuoteData with latest bid/ask, or None if not available
        """
        request = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
        response = self.client.get_crypto_latest_quote(request)

        if symbol in response:
            return CryptoQuoteData.from_quote(symbol, response[symbol])
        return None

    def get_latest_quotes(
        self, symbols: List[str]
    ) -> Dict[str, CryptoQuoteData]:
        """
        Get the latest quotes for multiple cryptocurrencies.

        Args:
            symbols: List of crypto symbols

        Returns:
            Dictionary mapping symbol to CryptoQuoteData
        """
        request = CryptoLatestQuoteRequest(symbol_or_symbols=symbols)
        response = self.client.get_crypto_latest_quote(request)

        return {
            symbol: CryptoQuoteData.from_quote(symbol, quote)
            for symbol, quote in response.items()
        }

    def get_latest_bar(self, symbol: str) -> Optional[CryptoBarData]:
        """
        Get the latest bar (OHLCV) for a cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., "BTC/USD")

        Returns:
            CryptoBarData with latest OHLCV, or None if not available
        """
        request = CryptoLatestBarRequest(symbol_or_symbols=symbol)
        response = self.client.get_crypto_latest_bar(request)

        if symbol in response:
            return CryptoBarData.from_bar(symbol, response[symbol])
        return None

    def get_latest_trade(self, symbol: str) -> Optional[CryptoTradeData]:
        """
        Get the latest trade for a cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., "BTC/USD")

        Returns:
            CryptoTradeData with latest trade, or None if not available
        """
        request = CryptoLatestTradeRequest(symbol_or_symbols=symbol)
        response = self.client.get_crypto_latest_trade(request)

        if symbol in response:
            return CryptoTradeData.from_trade(symbol, response[symbol])
        return None

    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[CryptoBarData]:
        """
        Get historical bars (OHLCV) for a cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., "BTC/USD")
            timeframe: Simple timeframe string (e.g., "1Min", "1H", "1D")
            start: Start datetime (if None and days_back provided, auto-calc)
            end: End datetime (defaults to now)
            days_back: Number of days to look back (alternative to start/end)
            limit: Maximum number of bars to return

        Returns:
            List of CryptoBarData objects

        Example:
            >>> # Get 5 days of hourly bars
            >>> bars = helper.get_bars("BTC/USD", "1H", days_back=5)
        """
        tf = self._parse_timeframe(timeframe)

        # Auto-calculate date range if days_back provided
        if days_back and not start:
            end = end or datetime.now()
            start = end - timedelta(days=days_back)

        request = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=start,
            end=end,
            limit=limit,
        )

        response = self.client.get_crypto_bars(request)

        if symbol not in response:
            return []

        return [
            CryptoBarData.from_bar(symbol, bar)
            for bar in response[symbol]
        ]

    def get_bars_multi(
        self,
        symbols: List[str],
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, List[CryptoBarData]]:
        """
        Get historical bars for multiple cryptocurrencies.

        Args:
            symbols: List of crypto symbols
            timeframe: Simple timeframe string (e.g., "1Min", "1H", "1D")
            start: Start datetime
            end: End datetime
            days_back: Number of days to look back
            limit: Maximum number of bars per symbol

        Returns:
            Dictionary mapping symbol to list of CryptoBarData
        """
        tf = self._parse_timeframe(timeframe)

        if days_back and not start:
            end = end or datetime.now()
            start = end - timedelta(days=days_back)

        request = CryptoBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=tf,
            start=start,
            end=end,
            limit=limit,
        )

        response = self.client.get_crypto_bars(request)

        return {
            symbol: [CryptoBarData.from_bar(symbol, bar) for bar in bars]
            for symbol, bars in response.items()
        }

    def get_quotes(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[CryptoQuoteData]:
        """
        Get historical quotes (bid/ask) for a cryptocurrency.

        Args:
            symbol: Crypto symbol
            start: Start datetime
            end: End datetime
            days_back: Number of days to look back
            limit: Maximum number of quotes to return

        Returns:
            List of CryptoQuoteData objects
        """
        if days_back and not start:
            end = end or datetime.now()
            start = end - timedelta(days=days_back)

        request = CryptoTradesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end,
            limit=limit,
        )

        response = self.client.get_crypto_quotes(request)

        if symbol not in response:
            return []

        return [
            CryptoQuoteData.from_quote(symbol, quote)
            for quote in response[symbol]
        ]

    def get_trades(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        days_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[CryptoTradeData]:
        """
        Get historical trades (ticks) for a cryptocurrency.

        Args:
            symbol: Crypto symbol
            start: Start datetime
            end: End datetime
            days_back: Number of days to look back
            limit: Maximum number of trades to return

        Returns:
            List of CryptoTradeData objects
        """
        if days_back and not start:
            end = end or datetime.now()
            start = end - timedelta(days=days_back)

        request = CryptoTradesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end,
            limit=limit,
        )

        response = self.client.get_crypto_trades(request)

        if symbol not in response:
            return []

        return [
            CryptoTradeData.from_trade(symbol, trade)
            for trade in response[symbol]
        ]

    def get_snapshot(self, symbol: str) -> Optional[CryptoSnapshotData]:
        """
        Get a complete snapshot of latest market data for a cryptocurrency.

        A snapshot includes:
        - Latest trade
        - Latest quote (bid/ask)
        - Latest minute bar
        - Previous daily bar

        Args:
            symbol: Crypto symbol (e.g., "BTC/USD")

        Returns:
            CryptoSnapshotData with all latest data, or None if not available
        """
        request = CryptoSnapshotRequest(symbol_or_symbols=symbol)
        response = self.client.get_crypto_snapshot(request)

        if symbol in response:
            return CryptoSnapshotData.from_snapshot(symbol, response[symbol])
        return None

    def get_snapshots(
        self, symbols: List[str]
    ) -> Dict[str, CryptoSnapshotData]:
        """
        Get snapshots for multiple cryptocurrencies.

        Args:
            symbols: List of crypto symbols

        Returns:
            Dictionary mapping symbol to CryptoSnapshotData
        """
        request = CryptoSnapshotRequest(symbol_or_symbols=symbols)
        response = self.client.get_crypto_snapshot(request)

        return {
            symbol: CryptoSnapshotData.from_snapshot(symbol, snapshot)
            for symbol, snapshot in response.items()
        }
