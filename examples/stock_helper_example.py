"""
Example usage of the StockHelper simplified stock data API.

This example demonstrates how the StockHelper class simplifies fetching
stock market data compared to using the raw API.
"""

import os
from datetime import datetime, timedelta
from alpaca.data.stock_helper import StockHelper

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Validate required environment variables
required_vars = ["ALPACA_API_KEY", "ALPACA_SECRET_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}\n"
        "Please create a .env file with ALPACA_API_KEY and ALPACA_SECRET_KEY"
    )


def main():
    """Run stock helper examples."""
    # Initialize the helper (automatically loads from environment)
    helper = StockHelper()

    print("=" * 60)
    print("StockHelper Example - Simplified Stock Data API")
    print("=" * 60)
    print()

    # ==================== Latest Quote ====================
    print("\n" + "=" * 60)
    print("Latest Quote Data")
    print("=" * 60)

    print("\nExample 1: Get latest quote for SPY")
    try:
        quote = helper.get_latest_quote("SPY")
        spread = quote.ask_price - quote.bid_price
        midpoint = (quote.bid_price + quote.ask_price) / 2
        
        print(f"✓ SPY Quote at {quote.timestamp}")
        print(f"  Bid: ${quote.bid_price:.2f} (size: {quote.bid_size})")
        print(f"  Ask: ${quote.ask_price:.2f} (size: {quote.ask_size})")
        print(f"  Spread: ${spread:.2f}")
        print(f"  Midpoint: ${midpoint:.2f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Multiple Quotes ====================
    print("\nExample 2: Get latest quotes for multiple symbols")
    try:
        quotes = helper.get_latest_quotes(["SPY", "QQQ", "IWM"])
        print(f"✓ Retrieved quotes for {len(quotes)} symbols:")
        for symbol, quote in quotes.items():
            print(f"  • {symbol}: Bid ${quote.bid_price:.2f} / Ask ${quote.ask_price:.2f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Latest Bar ====================
    print("\n" + "=" * 60)
    print("Latest Bar (OHLCV) Data")
    print("=" * 60)

    print("\nExample 3: Get latest bar for SPY")
    try:
        bar = helper.get_latest_bar("SPY")
        change = bar.close - bar.open
        change_pct = (change / bar.open) * 100
        
        print(f"✓ SPY Bar at {bar.timestamp}")
        print(f"  Open:   ${bar.open:.2f}")
        print(f"  High:   ${bar.high:.2f}")
        print(f"  Low:    ${bar.low:.2f}")
        print(f"  Close:  ${bar.close:.2f}")
        print(f"  Volume: {bar.volume:,}")
        print(f"  Change: ${change:+.2f} ({change_pct:+.2f}%)")
        if bar.vwap:
            print(f"  VWAP:   ${bar.vwap:.2f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Historical Bars ====================
    print("\n" + "=" * 60)
    print("Historical Bar Data")
    print("=" * 60)

    print("\nExample 4: Get hourly bars for last 5 days")
    try:
        bars = helper.get_bars("SPY", timeframe="1H", days_back=5, limit=10)
        print(f"✓ Retrieved {len(bars)} hourly bars:")
        for bar in bars[:5]:  # Show first 5
            print(f"  {bar.timestamp}: Close ${bar.close:.2f}, Vol {bar.volume:,}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\nExample 5: Get daily bars with specific date range")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        bars = helper.get_bars(
            "SPY",
            timeframe="1D",
            start=start_date,
            end=end_date
        )
        
        print(f"✓ Retrieved {len(bars)} daily bars from {start_date.date()} to {end_date.date()}")
        if bars:
            first_bar = bars[0]
            last_bar = bars[-1]
            total_return = ((last_bar.close - first_bar.open) / first_bar.open) * 100
            print(f"  First: ${first_bar.open:.2f} on {first_bar.timestamp.date()}")
            print(f"  Last:  ${last_bar.close:.2f} on {last_bar.timestamp.date()}")
            print(f"  Return: {total_return:+.2f}%")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Multi-Symbol Bars ====================
    print("\nExample 6: Get bars for multiple symbols")
    try:
        symbols = ["SPY", "QQQ", "IWM"]
        bars_dict = helper.get_bars_multi(
            symbols,
            timeframe="1D",
            days_back=5
        )
        
        print(f"✓ Retrieved bars for {len(bars_dict)} symbols:")
        for symbol, bars in bars_dict.items():
            if bars:
                latest = bars[-1]
                print(f"  • {symbol}: {len(bars)} bars, latest close ${latest.close:.2f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Historical Quotes ====================
    print("\n" + "=" * 60)
    print("Historical Quote Data (Bid/Ask)")
    print("=" * 60)

    print("\nExample 7: Get recent quotes")
    try:
        quotes = helper.get_quotes("SPY", days_back=1, limit=5)
        print(f"✓ Retrieved {len(quotes)} recent quotes:")
        for quote in quotes[:3]:
            spread = quote.ask_price - quote.bid_price
            print(f"  {quote.timestamp}: Bid ${quote.bid_price:.2f} / "
                  f"Ask ${quote.ask_price:.2f} (spread: ${spread:.2f})")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Historical Trades ====================
    print("\n" + "=" * 60)
    print("Historical Trade Data (Ticks)")
    print("=" * 60)

    print("\nExample 8: Get recent trades")
    try:
        trades = helper.get_trades("SPY", days_back=1, limit=5)
        print(f"✓ Retrieved {len(trades)} recent trades:")
        for trade in trades[:3]:
            print(f"  {trade.timestamp}: ${trade.price:.2f} x {trade.size}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Snapshots ====================
    print("\n" + "=" * 60)
    print("Snapshot Data (Latest Everything)")
    print("=" * 60)

    print("\nExample 9: Get snapshot for SPY")
    try:
        snapshot = helper.get_snapshot("SPY")
        print("✓ SPY Snapshot:")
        
        if snapshot.latest_quote:
            print(f"  Latest Quote: Bid ${snapshot.latest_quote.bid_price:.2f} / "
                  f"Ask ${snapshot.latest_quote.ask_price:.2f}")
        
        if snapshot.latest_trade:
            print(f"  Latest Trade: ${snapshot.latest_trade.price:.2f} x "
                  f"{snapshot.latest_trade.size}")
        
        if snapshot.latest_bar:
            print(f"  Latest Bar: ${snapshot.latest_bar.close:.2f} "
                  f"(Vol: {snapshot.latest_bar.volume:,})")
        
        if snapshot.prev_daily_bar:
            change = (
                (snapshot.latest_bar.close - snapshot.prev_daily_bar.close)
                / snapshot.prev_daily_bar.close * 100
            )
            print(f"  Daily Change: {change:+.2f}%")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\nExample 10: Get snapshots for multiple symbols")
    try:
        snapshots = helper.get_snapshots(["SPY", "QQQ", "IWM"])
        print(f"✓ Retrieved snapshots for {len(snapshots)} symbols:")
        for symbol, snapshot in snapshots.items():
            if snapshot.latest_quote:
                print(f"  • {symbol}: ${snapshot.latest_quote.bid_price:.2f} / "
                      f"${snapshot.latest_quote.ask_price:.2f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Timeframe Examples ====================
    print("\n" + "=" * 60)
    print("Supported Timeframes")
    print("=" * 60)

    print("\nAvailable timeframe formats:")
    print("  • Minutes: '1Min', '5Min', '15Min', '30Min'")
    print("  • Hours:   '1H', '1Hour', '4H'")
    print("  • Days:    '1D', '1Day'")
    print("  • Weeks:   '1W', '1Week'")
    print("  • Months:  '1M', '1Month'")

    # ==================== Comparison: Old vs New API ====================
    print("\n" + "=" * 60)
    print("API Comparison: Old Way vs New Way")
    print("=" * 60)

    print("\n📛 OLD WAY (Complex):")
    print("""
    from alpaca.data.historical.stock import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from datetime import datetime, timedelta

    client = StockHistoricalDataClient(api_key="...", secret_key="...")
    
    # Get hourly bars - requires complex setup
    request = StockBarsRequest(
        symbol_or_symbols="SPY",
        timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Hour),
        start=datetime.now() - timedelta(days=5)
    )
    response = client.get_stock_bars(request)
    
    # Extract and convert data
    bars = []
    for bar in response.data["SPY"]:
        bars.append({
            'timestamp': bar.timestamp,
            'close': float(bar.close),
            'volume': int(bar.volume)
        })
    """)

    print("\n✅ NEW WAY (Simple):")
    print("""
    from alpaca.data.stock_helper import StockHelper

    helper = StockHelper()  # Auto-loads from .env

    # Same data - one simple call!
    bars = helper.get_bars("SPY", timeframe="1H", days_back=5)
    
    # Data already in clean format
    for bar in bars:
        print(f"{bar.timestamp}: ${bar.close}, Vol: {bar.volume}")
    """)

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
