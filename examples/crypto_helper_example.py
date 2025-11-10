"""
CryptoHelper - Simplified Cryptocurrency Data API Examples

This file demonstrates how to use the CryptoHelper class to fetch
cryptocurrency market data with a clean, simple API.
"""

from alpaca.data.crypto_helper import CryptoHelper

# Initialize helper (auto-loads API keys from environment)
helper = CryptoHelper()

# Alternative: explicit credentials
# helper = CryptoHelper(api_key="your_key", secret_key="your_secret")

print("=" * 70)
print("CryptoHelper Examples - Simplified Cryptocurrency Data API")
print("=" * 70)

# ============================================================================
# Example 1: Get Latest Quote
# ============================================================================
print("\n1. Latest Quote for BTC/USD:")
print("-" * 70)

quote = helper.get_latest_quote("BTC/USD")
if quote:
    print(f"Symbol: {quote.symbol}")
    print(f"Time: {quote.timestamp}")
    print(f"Bid: ${quote.bid_price:,.2f} x {quote.bid_size}")
    print(f"Ask: ${quote.ask_price:,.2f} x {quote.ask_size}")
    spread = quote.ask_price - quote.bid_price
    print(f"Spread: ${spread:,.2f}")

# ============================================================================
# Example 2: Get Latest Quotes for Multiple Cryptos
# ============================================================================
print("\n2. Latest Quotes for Multiple Cryptocurrencies:")
print("-" * 70)

quotes = helper.get_latest_quotes(["BTC/USD", "ETH/USD", "DOGE/USD"])
for symbol, quote in quotes.items():
    mid = (quote.bid_price + quote.ask_price) / 2
    print(f"{symbol:10} Mid: ${mid:>10,.2f}")

# ============================================================================
# Example 3: Get Latest Bar
# ============================================================================
print("\n3. Latest Minute Bar for BTC/USD:")
print("-" * 70)

bar = helper.get_latest_bar("BTC/USD")
if bar:
    print(f"Time: {bar.timestamp}")
    print(f"Open:   ${bar.open:>10,.2f}")
    print(f"High:   ${bar.high:>10,.2f}")
    print(f"Low:    ${bar.low:>10,.2f}")
    print(f"Close:  ${bar.close:>10,.2f}")
    print(f"Volume: {bar.volume:>10.4f} BTC")
    change = bar.close - bar.open
    pct = (change / bar.open) * 100
    print(f"Change: ${change:>+10,.2f} ({pct:>+6.2f}%)")

# ============================================================================
# Example 4: Get Hourly Bars for Past 24 Hours
# ============================================================================
print("\n4. Hourly Bars for BTC/USD (Last 24 Hours):")
print("-" * 70)

bars = helper.get_bars("BTC/USD", timeframe="1H", days_back=1)
print(f"Retrieved {len(bars)} bars")
for bar in bars[-5:]:  # Show last 5 bars
    change = bar.close - bar.open
    arrow = "▲" if change >= 0 else "▼"
    print(
        f"{bar.timestamp.strftime('%Y-%m-%d %H:%M')} | "
        f"Close: ${bar.close:>10,.2f} {arrow} ${abs(change):>6,.2f} | "
        f"Vol: {bar.volume:>8.4f}"
    )

# ============================================================================
# Example 5: Get Multi-Symbol Bars
# ============================================================================
print("\n5. Daily Bars for Multiple Cryptos (Last 7 Days):")
print("-" * 70)

multi_bars = helper.get_bars_multi(
    ["BTC/USD", "ETH/USD"], timeframe="1D", days_back=7
)

for symbol, bars in multi_bars.items():
    if bars:
        first = bars[0]
        last = bars[-1]
        change = last.close - first.open
        pct = (change / first.open) * 100
        print(
            f"{symbol:10} | Start: ${first.open:>10,.2f} | "
            f"End: ${last.close:>10,.2f} | "
            f"Change: {pct:>+6.2f}%"
        )

# ============================================================================
# Example 6: Get Recent Trades
# ============================================================================
print("\n6. Recent Trades for BTC/USD (Last 10):")
print("-" * 70)

trades = helper.get_trades("BTC/USD", limit=10)
print(f"Retrieved {len(trades)} trades")
for trade in trades[:5]:  # Show first 5
    side = trade.taker_side if trade.taker_side else "N/A"
    print(
        f"{trade.timestamp.strftime('%H:%M:%S')} | "
        f"${trade.price:>10,.2f} | "
        f"Size: {trade.size:>8.6f} | "
        f"Side: {side:>4}"
    )

# ============================================================================
# Example 7: Get Snapshot (All Latest Data)
# ============================================================================
print("\n7. Complete Snapshot for BTC/USD:")
print("-" * 70)

snapshot = helper.get_snapshot("BTC/USD")
if snapshot:
    print("Latest Quote:")
    if snapshot.latest_quote:
        print(
            f"  Bid: ${snapshot.latest_quote.bid_price:,.2f} x "
            f"{snapshot.latest_quote.bid_size}"
        )
        print(
            f"  Ask: ${snapshot.latest_quote.ask_price:,.2f} x "
            f"{snapshot.latest_quote.ask_size}"
        )

    print("\nLatest Trade:")
    if snapshot.latest_trade:
        print(f"  Price: ${snapshot.latest_trade.price:,.2f}")
        print(f"  Size: {snapshot.latest_trade.size} BTC")

    print("\nLatest Minute Bar:")
    if snapshot.latest_bar:
        print(f"  Close: ${snapshot.latest_bar.close:,.2f}")
        print(f"  Volume: {snapshot.latest_bar.volume} BTC")

    print("\nPrevious Daily Bar:")
    if snapshot.prev_daily_bar:
        print(f"  Close: ${snapshot.prev_daily_bar.close:,.2f}")
        print(f"  Volume: {snapshot.prev_daily_bar.volume} BTC")

# ============================================================================
# Example 8: Get Snapshots for Multiple Cryptos
# ============================================================================
print("\n8. Snapshots for Multiple Cryptocurrencies:")
print("-" * 70)

snapshots = helper.get_snapshots(["BTC/USD", "ETH/USD", "SOL/USD"])
for symbol, snap in snapshots.items():
    if snap.latest_bar:
        print(f"{symbol:10} Close: ${snap.latest_bar.close:>10,.2f}")

# ============================================================================
# Example 9: Different Timeframes
# ============================================================================
print("\n9. Different Timeframe Options:")
print("-" * 70)

timeframes = ["1Min", "5Min", "15Min", "1H", "4H", "1D"]
print("Supported timeframes:")
for tf in timeframes:
    bars = helper.get_bars("BTC/USD", timeframe=tf, limit=1)
    if bars:
        print(f"  {tf:6} - Latest: ${bars[0].close:,.2f}")

# ============================================================================
# Example 10: Old API vs New API Comparison
# ============================================================================
print("\n10. Old API vs New API Comparison:")
print("-" * 70)

print("\nOLD WAY (Complex):")
print("""
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

client = CryptoHistoricalDataClient(api_key="...", secret_key="...")
request = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD",
    timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Hour),
    start=datetime.now() - timedelta(days=7),
    end=datetime.now()
)
response = client.get_crypto_bars(request)
bars = response["BTC/USD"]
for bar in bars:
    close = float(bar.close)  # Convert string to float
    print(f"Close: {close}")
""")

print("\nNEW WAY (Simple):")
print("""
from alpaca.data.crypto_helper import CryptoHelper

helper = CryptoHelper()  # Auto-loads from env
bars = helper.get_bars("BTC/USD", timeframe="1H", days_back=7)
for bar in bars:
    print(f"Close: {bar.close}")  # Already a float!
""")

print("\n" + "=" * 70)
print("Key Benefits:")
print("  - Simple timeframe strings (no TimeFrame objects)")
print("  - Automatic date calculations (days_back parameter)")
print("  - Native Python types (float, int, not strings)")
print("  - No complex request objects")
print("  - Environment variable loading")
print("  - Multi-symbol support built-in")
print("=" * 70)
