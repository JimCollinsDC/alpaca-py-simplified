"""
Example: Simplified Option Data Access

This example shows how to use the new OptionHelper class to easily get
complete option information with minimal code.

Before running:
    1. Copy .env.example to .env
    2. Add your Alpaca API keys to .env
    3. Run: uv run python examples/option_helper_example.py
"""

import os
from dotenv import load_dotenv

from alpaca.data.option_helper import OptionHelper

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# OLD WAY (Complex, Multiple Clients & Calls)
# ============================================================================


def old_way_example():
    """The old, complex way requiring multiple clients and requests."""
    from alpaca.data.historical.option import OptionHistoricalDataClient
    from alpaca.data.requests import (
        OptionSnapshotRequest,
        OptionLatestQuoteRequest,
    )

    # Need to create client
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    client = OptionHistoricalDataClient(api_key=api_key, secret_key=secret_key)

    # Need to know about request objects
    symbol = "AAPL250117C00150000"

    # Get quote (bid/ask)
    quote_request = OptionLatestQuoteRequest(symbol_or_symbols=symbol)
    quotes = client.get_option_latest_quote(quote_request)
    bid = quotes[symbol].bid_price
    ask = quotes[symbol].ask_price

    # Get snapshot for Greeks and IV
    snapshot_request = OptionSnapshotRequest(symbol_or_symbols=symbol)
    snapshots = client.get_option_snapshot(snapshot_request)
    snapshot = snapshots[symbol]

    delta = snapshot.greeks.delta if snapshot.greeks else None
    iv = snapshot.implied_volatility

    # Multiple steps, complex objects, lots of code
    print(f"Bid: {bid}, Ask: {ask}, Delta: {delta}, IV: {iv}")


# ============================================================================
# NEW WAY (Simple, Single Call)
# ============================================================================


def new_way_example():
    """The new, simple way with OptionHelper."""

    # Initialize once (reads from environment variables automatically)
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    options = OptionHelper(api_key=api_key, secret_key=secret_key)

    # Get everything in one call!
    data = options.get_option("AAPL250117C00150000")

    # Easy access to all data
    print(f"Symbol: {data.symbol}")
    print(f"Strike: ${data.strike}")
    print(f"Expiration: {data.expiration.strftime('%Y-%m-%d')}")
    print(f"Type: {data.option_type}")
    print("\nPricing:")
    print(f"  Bid: ${data.bid}")
    print(f"  Ask: ${data.ask}")
    print(f"  Mid: ${data.mid}")
    print(f"  Last: ${data.last_price}")
    print("\nGreeks:")
    print(f"  Delta: {data.delta:.4f}")
    print(f"  Gamma: {data.gamma:.4f}")
    print(f"  Theta: {data.theta:.4f}")
    print(f"  Vega: {data.vega:.4f}")
    print("\nVolatility:")
    print(f"  IV: {data.implied_volatility:.2%}")


# ============================================================================
# Multiple Options - Even Simpler
# ============================================================================


def multiple_options_example():
    """Get multiple options at once."""

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    options = OptionHelper(api_key=api_key, secret_key=secret_key)

    # Get multiple options with one call
    symbols = [
        "AAPL250117C00150000",
        "AAPL250117C00155000",
        "AAPL250117C00160000",
    ]

    data_list = options.get_options(symbols)

    # Easy iteration
    for data in data_list:
        print(
            f"{data.symbol}: Strike=${data.strike}, Bid=${data.bid}, Delta={data.delta:.3f}"
        )


# ============================================================================
# Option Chain - Super Simple
# ============================================================================


def option_chain_example():
    """Get entire option chain."""
    from datetime import datetime

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    options = OptionHelper(api_key=api_key, secret_key=secret_key)

    # Get all options for AAPL expiring Jan 17, 2025
    expiration = datetime(2025, 1, 17)
    chain = options.get_option_chain("AAPL", expiration=expiration)

    print(f"Found {len(chain)} options in the chain")

    # Find ATM calls
    atm_calls = [
        opt for opt in chain if opt.option_type == "call" and 0.45 < opt.delta < 0.55
    ]

    print("\nATM Calls:")
    for opt in atm_calls:
        print(
            f"  Strike ${opt.strike}: IV={opt.implied_volatility:.2%}, Delta={opt.delta:.3f}"
        )


# ============================================================================
# Real-World Use Case: Finding Best Options to Trade
# ============================================================================


def find_best_options():
    """Find options with specific criteria."""
    from datetime import datetime

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    options = OptionHelper(api_key=api_key, secret_key=secret_key)

    # Get the chain
    exp = datetime(2025, 2, 21)
    chain = options.get_option_chain("SPY", expiration=exp)

    # Filter for liquid, ATM puts with good IV
    candidates = [
        opt
        for opt in chain
        if (
            opt.option_type == "put"
            and abs(opt.delta) > 0.4
            and opt.implied_volatility > 0.20
            and opt.bid
            and opt.ask
            and (opt.ask - opt.bid) < 0.50  # Tight spread
        )
    ]

    # Sort by IV (highest first)
    candidates.sort(key=lambda x: x.implied_volatility, reverse=True)

    print("Top 5 candidates for selling puts:")
    for i, opt in enumerate(candidates[:5], 1):
        spread = opt.ask - opt.bid
        print(f"{i}. Strike ${opt.strike}:")
        print(f"   Bid/Ask: ${opt.bid:.2f}/${opt.ask:.2f} (spread: ${spread:.2f})")
        print(f"   Delta: {opt.delta:.3f}, IV: {opt.implied_volatility:.2%}")
        print()


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("ALPACA_API_KEY") or not os.getenv("ALPACA_SECRET_KEY"):
        print(
            "Error: Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file"
        )
        print("\nCreate a .env file in the project root with:")
        print("ALPACA_API_KEY=your_key_here")
        print("ALPACA_SECRET_KEY=your_secret_here")
        exit(1)

    print("=" * 70)
    print("NEW SIMPLIFIED OPTION API")
    print("=" * 70)
    print("\n# Simple single option lookup:")
    print("from dotenv import load_dotenv")
    print("load_dotenv()")
    print("options = OptionHelper()")
    print("data = options.get_option('AAPL250117C00150000')")
    print(
        "print(f'Bid: {data.bid}, Ask: {data.ask}, Delta: {data.delta}, IV: {data.iv}')"
    )
    print("\n# That's it! No complex request objects, no multiple calls.")
    print("\nRun the example functions? (uncomment below)")
    print("# new_way_example()")
    print("# multiple_options_example()")
    print("# option_chain_example()")
