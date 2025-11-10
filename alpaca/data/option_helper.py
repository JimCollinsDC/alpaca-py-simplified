"""
Simplified Option Data API

This module provides an easy-to-use interface for fetching complete option information
with a single call, eliminating the need to manage multiple clients and requests.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionSnapshotRequest


@dataclass
class OptionData:
    """
    Complete option information in a single, easy-to-use object.

    Attributes:
        symbol: The option contract symbol
        strike: Strike price
        expiration: Expiration date
        option_type: 'call' or 'put'

        # Pricing
        bid: Current bid price
        ask: Current ask price
        mid: Mid price (bid + ask) / 2
        last_price: Last trade price

        # Greeks
        delta: Delta greek
        gamma: Gamma greek
        theta: Theta greek
        vega: Vega greek
        rho: Rho greek

        # Volume & Interest
        volume: Trading volume
        open_interest: Open interest

        # Volatility
        implied_volatility: Implied volatility

        # Additional Info
        bid_size: Bid size
        ask_size: Ask size
        last_size: Last trade size
        timestamp: Data timestamp
    """

    symbol: str
    strike: Optional[float] = None
    expiration: Optional[datetime] = None
    option_type: Optional[str] = None

    # Pricing
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid: Optional[float] = None
    last_price: Optional[float] = None

    # Greeks
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None

    # Volume & Interest
    volume: Optional[int] = None
    open_interest: Optional[int] = None

    # Volatility
    implied_volatility: Optional[float] = None

    # Additional Info
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    last_size: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Calculate mid price if not provided."""
        if self.mid is None and self.bid is not None and self.ask is not None:
            self.mid = (self.bid + self.ask) / 2

    def __repr__(self) -> str:
        iv_str = f"{self.implied_volatility:.2%}" if self.implied_volatility else "N/A"
        return (
            f"OptionData({self.symbol}, "
            f"Strike={self.strike}, "
            f"Bid={self.bid}, Ask={self.ask}, "
            f"IV={iv_str}, "
            f"Delta={self.delta}, Volume={self.volume})"
        )


class OptionHelper:
    """
    Simplified interface for option data.

    Example usage:
        ```python
        from alpaca.data.option_helper import OptionHelper

        # Initialize once
        options = OptionHelper(api_key="your_key", secret_key="your_secret")

        # Get complete option info with one call
        data = options.get_option("AAPL250117C00150000")
        print(f"Strike: {data.strike}")
        print(f"Bid/Ask: {data.bid}/{data.ask}")
        print(f"IV: {data.implied_volatility:.2%}")
        print(f"Delta: {data.delta}")
        print(f"Volume: {data.volume}")

        # Get multiple options at once
        chain = options.get_options([
            "AAPL250117C00150000",
            "AAPL250117C00155000",
            "AAPL250117P00150000"
        ])
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        oauth_token: Optional[str] = None,
        sandbox: bool = False,
    ):
        """
        Initialize the Option Helper.

        If api_key/secret_key are not provided, they will be read from
        environment variables ALPACA_API_KEY and ALPACA_SECRET_KEY.

        Args:
            api_key: Alpaca API key (defaults to ALPACA_API_KEY env var)
            secret_key: Alpaca API secret key (defaults to ALPACA_SECRET_KEY env var)
            oauth_token: OAuth token (alternative to api_key/secret_key)
            sandbox: Use sandbox environment (defaults to ALPACA_PAPER env var or False)

        Example:
            ```python
            # Option 1: Provide keys directly
            options = OptionHelper(api_key="your_key", secret_key="your_secret")

            # Option 2: Use environment variables (recommended)
            # Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file
            from dotenv import load_dotenv
            load_dotenv()
            options = OptionHelper()  # Will read from env vars
            ```
        """
        # Read from environment variables if not provided
        if api_key is None:
            api_key = os.getenv("ALPACA_API_KEY")
        if secret_key is None:
            secret_key = os.getenv("ALPACA_SECRET_KEY")

        # Check if sandbox should be enabled from env var
        if os.getenv("ALPACA_PAPER", "").lower() in ("true", "1", "yes"):
            sandbox = True

        self._client = OptionHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key,
            oauth_token=oauth_token,
            sandbox=sandbox,
        )

    def get_option(self, symbol: str) -> Optional[OptionData]:
        """
        Get complete option information with a single call.

        Args:
            symbol: Option contract symbol (e.g., "AAPL250117C00150000")

        Returns:
            OptionData object with all available information, or None if not found

        Example:
            ```python
            data = options.get_option("AAPL250117C00150000")
            if data:
                print(f"Bid: ${data.bid}, Ask: ${data.ask}")
                print(f"Delta: {data.delta}, IV: {data.implied_volatility:.2%}")
            ```
        """
        result = self.get_options([symbol])
        return result[0] if result else None

    def get_options(self, symbols: List[str]) -> List[OptionData]:
        """
        Get complete information for multiple options with a single call.

        Args:
            symbols: List of option contract symbols

        Returns:
            List of OptionData objects

        Example:
            ```python
            symbols = ["AAPL250117C00150000", "AAPL250117C00155000"]
            data_list = options.get_options(symbols)
            for data in data_list:
                print(f"{data.symbol}: Bid={data.bid}, Ask={data.ask}")
            ```
        """
        if not symbols:
            return []

        request = OptionSnapshotRequest(symbol_or_symbols=symbols)
        snapshots = self._client.get_option_snapshot(request)

        results = []
        for symbol, snapshot in snapshots.items():
            option_data = OptionData(symbol=symbol)

            # Parse symbol for strike/expiration/type
            parsed = self._parse_option_symbol(symbol)
            option_data.strike = parsed["strike"]
            option_data.expiration = parsed["expiration"]
            option_data.option_type = parsed["option_type"]

            # Latest quote (bid/ask)
            if snapshot.latest_quote:
                option_data.bid = snapshot.latest_quote.bid_price
                option_data.ask = snapshot.latest_quote.ask_price
                option_data.bid_size = snapshot.latest_quote.bid_size
                option_data.ask_size = snapshot.latest_quote.ask_size

                if option_data.bid and option_data.ask:
                    option_data.mid = (option_data.bid + option_data.ask) / 2

                option_data.timestamp = snapshot.latest_quote.timestamp

            # Latest trade (price/volume)
            if snapshot.latest_trade:
                option_data.last_price = snapshot.latest_trade.price
                option_data.last_size = snapshot.latest_trade.size
                # Note: Volume requires aggregation from trades endpoint
                # Open interest requires separate data source

            # Greeks
            if snapshot.greeks:
                option_data.delta = snapshot.greeks.delta
                option_data.gamma = snapshot.greeks.gamma
                option_data.theta = snapshot.greeks.theta
                option_data.vega = snapshot.greeks.vega
                option_data.rho = snapshot.greeks.rho

            # Implied Volatility
            option_data.implied_volatility = snapshot.implied_volatility

            results.append(option_data)

        return results

    def get_option_chain(
        self, underlying: str, expiration: Optional[datetime] = None
    ) -> List[OptionData]:
        """
        Get complete option chain for an underlying symbol.

        Args:
            underlying: Underlying stock symbol (e.g., "AAPL")
            expiration: Optional filter by expiration date

        Returns:
            List of OptionData for all options in the chain

        Example:
            ```python
            from datetime import datetime

            # Get all AAPL options
            chain = options.get_option_chain("AAPL")

            # Filter by expiration
            exp_date = datetime(2025, 1, 17)
            chain = options.get_option_chain("AAPL", expiration=exp_date)

            # Find ATM options
            for opt in chain:
                if abs(opt.delta) > 0.45 and abs(opt.delta) < 0.55:
                    print(f"{opt.symbol}: Strike={opt.strike}, Delta={opt.delta}")
            ```
        """
        from alpaca.data.requests import OptionChainRequest

        request_params = {"underlying_symbol": underlying}
        if expiration:
            request_params["expiration_date"] = expiration.strftime("%Y-%m-%d")

        request = OptionChainRequest(**request_params)
        snapshots = self._client.get_option_chain(request)

        results = []
        for symbol, snapshot in snapshots.items():
            option_data = OptionData(symbol=symbol)

            # Parse symbol
            parsed = self._parse_option_symbol(symbol)
            option_data.strike = parsed["strike"]
            option_data.expiration = parsed["expiration"]
            option_data.option_type = parsed["option_type"]

            # Quote data
            if snapshot.latest_quote:
                option_data.bid = snapshot.latest_quote.bid_price
                option_data.ask = snapshot.latest_quote.ask_price
                option_data.bid_size = snapshot.latest_quote.bid_size
                option_data.ask_size = snapshot.latest_quote.ask_size

                if option_data.bid and option_data.ask:
                    option_data.mid = (option_data.bid + option_data.ask) / 2

            # Trade data
            if snapshot.latest_trade:
                option_data.last_price = snapshot.latest_trade.price
                option_data.last_size = snapshot.latest_trade.size

            # Greeks
            if snapshot.greeks:
                option_data.delta = snapshot.greeks.delta
                option_data.gamma = snapshot.greeks.gamma
                option_data.theta = snapshot.greeks.theta
                option_data.vega = snapshot.greeks.vega
                option_data.rho = snapshot.greeks.rho

            # IV
            option_data.implied_volatility = snapshot.implied_volatility

            # Filter by expiration if specified
            if expiration is None or option_data.expiration == expiration:
                results.append(option_data)

        return results

    @staticmethod
    def _parse_option_symbol(symbol: str) -> dict:
        """
        Parse OCC option symbol format.

        Format: TICKER[variable]YYMMDD[C/P]STRIKE[8]
        Example: AAPL250117C00150000 or SPY241220P00450000

        Returns:
            dict with keys: 'underlying', 'strike', 'expiration', 'option_type'
        """
        try:
            # Find where the date starts (6 digits for YYMMDD)
            # Work backwards from the end to find C or P
            cp_index = -1
            for i, char in enumerate(symbol):
                if char in ("C", "P"):
                    # Check if this looks like a valid position
                    # Should have 6 digits before it and 8 after it
                    if i >= 6 and len(symbol) - i == 9:
                        cp_index = i
                        break

            if cp_index == -1:
                raise ValueError("Could not find C/P indicator")

            # Extract underlying (everything before date)
            underlying = symbol[: cp_index - 6]

            # Extract expiration date (6 chars before C/P)
            exp_str = symbol[cp_index - 6 : cp_index]
            year = 2000 + int(exp_str[:2])
            month = int(exp_str[2:4])
            day = int(exp_str[4:6])
            expiration = datetime(year, month, day)

            # Extract option type (C or P)
            option_type = "call" if symbol[cp_index] == "C" else "put"

            # Extract strike (8 digits after C/P, divide by 1000 for decimal)
            strike_str = symbol[cp_index + 1 : cp_index + 9]
            strike = float(strike_str) / 1000

            return {
                "underlying": underlying,
                "strike": strike,
                "expiration": expiration,
                "option_type": option_type,
            }
        except (ValueError, IndexError):
            return {
                "underlying": symbol,
                "strike": None,
                "expiration": None,
                "option_type": None,
            }
