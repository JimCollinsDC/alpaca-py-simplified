"""
Example usage of the TradingHelper simplified trading API.

This example demonstrates how the TradingHelper class simplifies common
trading operations compared to using the raw API.
"""

import os
from alpaca.trading.trading_helper import TradingHelper
from alpaca.trading.enums import QueryOrderStatus, TimeInForce

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
    """Run trading helper examples."""
    # Initialize the helper (automatically loads from environment)
    helper = TradingHelper()

    print("=" * 60)
    print("TradingHelper Example - Simplified Trading API")
    print("=" * 60)
    print()

    # Check if using paper trading
    mode = "PAPER" if helper.is_paper else "LIVE"
    print(f"Trading Mode: {mode}")
    print()

    # ==================== Account Information ====================
    print("\n" + "=" * 60)
    print("Account Information")
    print("=" * 60)

    cash = helper.get_cash()
    buying_power = helper.get_buying_power()
    portfolio_value = helper.get_portfolio_value()

    print(f"Cash: ${cash:,.2f}")
    print(f"Buying Power: ${buying_power:,.2f}")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")

    # ==================== Simple Market Orders ====================
    print("\n" + "=" * 60)
    print("Simple Market Orders")
    print("=" * 60)

    # Example 1: Buy market order
    print("\nExample 1: Buy 1 share of SPY at market")
    try:
        order = helper.buy_market("SPY", qty=1)
        print(f"✓ Order submitted: {order.id}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Qty: {order.qty}")
        print(f"  Side: {order.side}")
        print(f"  Status: {order.status}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Example 2: Buy with notional amount
    print("\nExample 2: Buy $100 worth of SPY")
    try:
        order = helper.buy_market("SPY", notional=100.0)
        print(f"✓ Order submitted: {order.id}")
        print(f"  Notional: ${order.notional}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Limit Orders ====================
    print("\n" + "=" * 60)
    print("Limit Orders")
    print("=" * 60)

    print("\nExample 3: Buy SPY with limit price")
    try:
        order = helper.buy_limit("SPY", qty=1, limit_price=550.00)
        print(f"✓ Limit order submitted: {order.id}")
        print(f"  Limit Price: ${order.limit_price}")
        print(f"  Status: {order.status}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Bracket Orders ====================
    print("\n" + "=" * 60)
    print("Bracket Orders (with Stop Loss & Take Profit)")
    print("=" * 60)

    print("\nExample 4: Buy with stop loss and take profit")
    try:
        order = helper.buy_with_bracket(
            symbol="SPY",
            qty=1,
            stop_loss=450.00,
            take_profit=650.00,
            time_in_force=TimeInForce.GTC  # Good 'til cancelled
        )
        print(f"✓ Bracket order submitted: {order.id}")
        print(f"  Order Class: {order.order_class}")
        print(f"  Status: {order.status}")
        print("  This creates 3 orders: entry, stop loss, and take profit")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\nExample 5: Buy with just stop loss")
    try:
        order = helper.buy_with_bracket(
            symbol="SPY",
            qty=1,
            stop_loss=450.00,
        )
        print(f"✓ Order with stop loss submitted: {order.id}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # ==================== Position Management ====================
    print("\n" + "=" * 60)
    print("Position Management")
    print("=" * 60)

    # Get all positions
    print("\nExample 6: Get all open positions")
    try:
        positions = helper.get_all_positions()
        if positions:
            print(f"✓ Found {len(positions)} open position(s):")
            for pos in positions:
                pnl_color = "+" if pos.unrealized_pl >= 0 else ""
                print(f"  • {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price:.2f}")
                print(f"    Current: ${pos.current_price:.2f}")
                print(f"    P&L: {pnl_color}${pos.unrealized_pl:.2f} "
                      f"({pnl_color}{pos.unrealized_plpc * 100:.2f}%)")
        else:
            print("✓ No open positions")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Get specific position
    print("\nExample 7: Get position for SPY")
    try:
        position = helper.get_position("SPY")
        print("✓ SPY Position:")
        print(f"  Qty: {position.qty}")
        print(f"  Market Value: ${position.market_value:,.2f}")
        print(f"  Unrealized P&L: ${position.unrealized_pl:.2f}")
    except Exception:
        print("✗ No position found for SPY (this is normal if you don't own any)")

    # Close position examples (commented out to avoid accidental execution)
    print("\nExample 8: Close position (examples - commented out)")
    print("  # Close entire position:")
    print("  # order = helper.close_position('SPY')")
    print("  # Close 50% of position:")
    print("  # order = helper.close_position('SPY', percentage=50)")
    print("  # Close specific quantity:")
    print("  # order = helper.close_position('SPY', qty=5)")

    # ==================== Order Management ====================
    print("\n" + "=" * 60)
    print("Order Management")
    print("=" * 60)

    # Get open orders
    print("\nExample 9: Get all open orders")
    try:
        orders = helper.get_orders()
        if orders:
            print(f"✓ Found {len(orders)} open order(s):")
            for order in orders:
                print(f"  • {order.symbol}: {order.side} {order.qty} @ {order.type}")
                print(f"    Status: {order.status}")
                print(f"    ID: {order.id}")
        else:
            print("✓ No open orders")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Get all orders (including filled)
    print("\nExample 10: Get all orders (including filled)")
    try:
        all_orders = helper.get_orders(status=QueryOrderStatus.ALL, limit=5)
        if all_orders:
            print(f"✓ Found {len(all_orders)} recent order(s):")
            for order in all_orders[:3]:  # Show first 3
                filled_info = ""
                if order.filled_qty > 0:
                    filled_info = f", Filled: {order.filled_qty} @ ${order.filled_avg_price:.2f}"
                print(f"  • {order.symbol}: {order.status}{filled_info}")
        else:
            print("✓ No orders found")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Cancel orders (commented out for safety)
    print("\nExample 11: Cancel orders (examples - commented out)")
    print("  # Cancel specific order:")
    print("  # helper.cancel_order(order_id)")
    print("  # Cancel ALL open orders:")
    print("  # helper.cancel_all_orders()")

    # ==================== Comparison: Old vs New API ====================
    print("\n" + "=" * 60)
    print("API Comparison: Old Way vs New Way")
    print("=" * 60)

    print("\n📛 OLD WAY (Complex):")
    print("""
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest
    from alpaca.trading.enums import OrderSide, OrderClass, TimeInForce

    client = TradingClient(api_key="...", secret_key="...", paper=True)

    # Place bracket order - requires 4 imports, nested objects
    request = MarketOrderRequest(
        symbol="SPY",
        qty=10,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        order_class=OrderClass.BRACKET,
        take_profit=TakeProfitRequest(limit_price=550.00),
        stop_loss=StopLossRequest(stop_price=450.00)
    )
    order = client.submit_order(request)
    """)

    print("\n✅ NEW WAY (Simple):")
    print("""
    from alpaca.trading.trading_helper import TradingHelper

    helper = TradingHelper()  # Auto-loads from .env

    # Same bracket order - one simple call!
    order = helper.buy_with_bracket(
        "SPY", qty=10, stop_loss=450.00, take_profit=550.00
    )
    """)

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
