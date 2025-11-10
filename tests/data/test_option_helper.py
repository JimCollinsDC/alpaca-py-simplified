"""Tests for the OptionHelper simplified API."""

from datetime import datetime, timezone

import pytest

from alpaca.data import OptionHelper, OptionData
from alpaca.data.historical.option import OptionHistoricalDataClient


def test_parse_option_symbol_call():
    """Test parsing a call option symbol."""
    result = OptionHelper._parse_option_symbol("AAPL250117C00150000")

    assert result["underlying"] == "AAPL"
    assert result["expiration"] == datetime(2025, 1, 17)
    assert result["option_type"] == "call"
    assert result["strike"] == 150.0


def test_parse_option_symbol_put():
    """Test parsing a put option symbol."""
    result = OptionHelper._parse_option_symbol("SPY241220P00450000")

    assert result["underlying"] == "SPY"
    assert result["expiration"] == datetime(2024, 12, 20)
    assert result["option_type"] == "put"
    assert result["strike"] == 450.0


def test_parse_option_symbol_fractional_strike():
    """Test parsing option with fractional strike."""
    result = OptionHelper._parse_option_symbol("TSLA250321C00225500")

    assert result["underlying"] == "TSLA"
    assert result["expiration"] == datetime(2025, 3, 21)
    assert result["option_type"] == "call"
    assert result["strike"] == 225.5


def test_parse_option_symbol_invalid():
    """Test parsing invalid option symbol."""
    result = OptionHelper._parse_option_symbol("INVALID")

    assert result["underlying"] == "INVALID"
    assert result["expiration"] is None
    assert result["option_type"] is None
    assert result["strike"] is None


@pytest.fixture
def option_helper():
    """Create an OptionHelper instance for testing."""
    return OptionHelper(api_key="test-key", secret_key="test-secret")


def test_option_helper_initialization(option_helper):
    """Test OptionHelper is properly initialized."""
    assert option_helper._client is not None
    # The client is properly initialized but doesn't expose api_key/secret_key publicly
    assert isinstance(option_helper._client, OptionHistoricalDataClient)


def test_option_helper_env_vars(monkeypatch):
    """Test OptionHelper reads from environment variables."""
    # Set environment variables
    monkeypatch.setenv("ALPACA_API_KEY", "env-test-key")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "env-test-secret")
    monkeypatch.setenv("ALPACA_PAPER", "True")

    # Create helper without passing keys
    helper = OptionHelper()

    # Verify client was created (we can't directly check the keys)
    assert helper._client is not None
    assert isinstance(helper._client, OptionHistoricalDataClient)


def test_get_option_single(reqmock, option_helper: OptionHelper):
    """Test getting a single option."""
    symbol = "AAPL250117C00150000"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={symbol}&limit=1000",
        text="""
        {
            "snapshots": {
                "AAPL250117C00150000": {
                    "greeks": {
                        "delta": 0.6234,
                        "gamma": 0.0234,
                        "rho": 0.1234,
                        "theta": -0.0512,
                        "vega": 0.2345
                    },
                    "impliedVolatility": 0.2845,
                    "latestQuote": {
                        "ap": 12.75,
                        "as": 50,
                        "ax": "N",
                        "bp": 12.50,
                        "bs": 100,
                        "bx": "N",
                        "c": "A",
                        "t": "2024-11-09T15:30:00.123456789Z"
                    },
                    "latestTrade": {
                        "c": "I",
                        "p": 12.60,
                        "s": 25,
                        "t": "2024-11-09T15:29:45.987654321Z",
                        "x": "N"
                    }
                }
            }
        }
        """,
    )

    data = option_helper.get_option(symbol)

    assert isinstance(data, OptionData)
    assert data.symbol == symbol
    assert data.strike == 150.0
    assert data.expiration == datetime(2025, 1, 17)
    assert data.option_type == "call"
    assert data.bid == 12.50
    assert data.ask == 12.75
    assert data.mid == 12.625
    assert data.last_price == 12.60
    assert data.delta == 0.6234
    assert data.gamma == 0.0234
    assert data.theta == -0.0512
    assert data.vega == 0.2345
    assert data.rho == 0.1234
    assert data.implied_volatility == 0.2845
    assert data.bid_size == 100
    assert data.ask_size == 50
    assert data.last_size == 25
    assert data.volume is None  # Not in snapshot
    assert data.open_interest is None  # Not in snapshot

    assert reqmock.called_once


def test_get_option_minimal_data(reqmock, option_helper: OptionHelper):
    """Test getting option with minimal data (only quote)."""
    symbol = "AAPL250117C00150000"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={symbol}&limit=1000",
        text="""
        {
            "snapshots": {
                "AAPL250117C00150000": {
                    "latestQuote": {
                        "ap": 12.75,
                        "as": 50,
                        "ax": "N",
                        "bp": 12.50,
                        "bs": 100,
                        "bx": "N",
                        "c": "A",
                        "t": "2024-11-09T15:30:00.123456789Z"
                    }
                }
            }
        }
        """,
    )

    data = option_helper.get_option(symbol)

    assert isinstance(data, OptionData)
    assert data.symbol == symbol
    assert data.bid == 12.50
    assert data.ask == 12.75
    assert data.mid == 12.625
    assert data.last_price is None
    assert data.delta is None
    assert data.gamma is None
    assert data.implied_volatility is None


def test_get_option_not_found(reqmock, option_helper: OptionHelper):
    """Test getting option that doesn't exist."""
    symbol = "INVALID250117C00150000"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={symbol}&limit=1000",
        text='{"snapshots": {}}',
    )

    data = option_helper.get_option(symbol)

    assert data is None
    assert reqmock.called_once


def test_get_options_multiple(reqmock, option_helper: OptionHelper):
    """Test getting multiple options at once."""
    symbols = ["AAPL250117C00150000", "AAPL250117P00150000"]
    symbols_encoded = "AAPL250117C00150000%2CAAPL250117P00150000"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={symbols_encoded}&limit=1000",
        text="""
        {
            "snapshots": {
                "AAPL250117C00150000": {
                    "greeks": {
                        "delta": 0.6234,
                        "gamma": 0.0234,
                        "rho": 0.1234,
                        "theta": -0.0512,
                        "vega": 0.2345
                    },
                    "impliedVolatility": 0.2845,
                    "latestQuote": {
                        "ap": 12.75,
                        "as": 50,
                        "ax": "N",
                        "bp": 12.50,
                        "bs": 100,
                        "bx": "N",
                        "c": "A",
                        "t": "2024-11-09T15:30:00Z"
                    }
                },
                "AAPL250117P00150000": {
                    "greeks": {
                        "delta": -0.3766,
                        "gamma": 0.0234,
                        "rho": -0.0987,
                        "theta": -0.0498,
                        "vega": 0.2345
                    },
                    "impliedVolatility": 0.2912,
                    "latestQuote": {
                        "ap": 11.25,
                        "as": 75,
                        "ax": "N",
                        "bp": 11.00,
                        "bs": 125,
                        "bx": "N",
                        "c": "A",
                        "t": "2024-11-09T15:30:00Z"
                    }
                }
            }
        }
        """,
    )

    data_list = option_helper.get_options(symbols)

    assert len(data_list) == 2

    # Check call option
    call_data = data_list[0]
    assert call_data.symbol == "AAPL250117C00150000"
    assert call_data.option_type == "call"
    assert call_data.delta == 0.6234
    assert call_data.bid == 12.50
    assert call_data.ask == 12.75

    # Check put option
    put_data = data_list[1]
    assert put_data.symbol == "AAPL250117P00150000"
    assert put_data.option_type == "put"
    assert put_data.delta == -0.3766
    assert put_data.bid == 11.00
    assert put_data.ask == 11.25

    assert reqmock.called_once


def test_get_options_empty_list(option_helper: OptionHelper):
    """Test getting options with empty list."""
    data_list = option_helper.get_options([])

    assert data_list == []


def test_get_options_partial_results(reqmock, option_helper: OptionHelper):
    """Test getting multiple options when some don't exist."""
    symbols = ["AAPL250117C00150000", "INVALID250117C00150000"]
    symbols_encoded = "AAPL250117C00150000%2CINVALID250117C00150000"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={symbols_encoded}&limit=1000",
        text="""
        {
            "snapshots": {
                "AAPL250117C00150000": {
                    "latestQuote": {
                        "ap": 12.75,
                        "as": 50,
                        "ax": "N",
                        "bp": 12.50,
                        "bs": 100,
                        "bx": "N",
                        "c": "A",
                        "t": "2024-11-09T15:30:00Z"
                    }
                }
            }
        }
        """,
    )

    data_list = option_helper.get_options(symbols)

    # Should only return the valid option
    assert len(data_list) == 1
    assert data_list[0].symbol == "AAPL250117C00150000"


def test_get_option_chain(reqmock, option_helper: OptionHelper):
    """Test getting an entire option chain."""
    underlying = "AAPL"
    expiration = datetime(2025, 1, 17)

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots/{underlying}",
        text="""
        {
            "snapshots": {
                "AAPL250117C00145000": {
                    "greeks": {"delta": 0.7123, "gamma": 0.0198, "rho": 0.1456, "theta": -0.0623, "vega": 0.2134},
                    "impliedVolatility": 0.2678,
                    "latestQuote": {"ap": 15.50, "as": 30, "ax": "N", "bp": 15.25, "bs": 50, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "AAPL250117C00150000": {
                    "greeks": {"delta": 0.6234, "gamma": 0.0234, "rho": 0.1234, "theta": -0.0512, "vega": 0.2345},
                    "impliedVolatility": 0.2845,
                    "latestQuote": {"ap": 12.75, "as": 50, "ax": "N", "bp": 12.50, "bs": 100, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "AAPL250117C00155000": {
                    "greeks": {"delta": 0.5234, "gamma": 0.0245, "rho": 0.0987, "theta": -0.0487, "vega": 0.2398},
                    "impliedVolatility": 0.2956,
                    "latestQuote": {"ap": 10.25, "as": 75, "ax": "N", "bp": 10.00, "bs": 125, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "AAPL250117P00145000": {
                    "greeks": {"delta": -0.2877, "gamma": 0.0198, "rho": -0.0823, "theta": -0.0598, "vega": 0.2134},
                    "impliedVolatility": 0.2701,
                    "latestQuote": {"ap": 8.50, "as": 40, "ax": "N", "bp": 8.25, "bs": 60, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "AAPL250117P00150000": {
                    "greeks": {"delta": -0.3766, "gamma": 0.0234, "rho": -0.0987, "theta": -0.0498, "vega": 0.2345},
                    "impliedVolatility": 0.2912,
                    "latestQuote": {"ap": 11.25, "as": 75, "ax": "N", "bp": 11.00, "bs": 125, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "AAPL250117P00155000": {
                    "greeks": {"delta": -0.4766, "gamma": 0.0245, "rho": -0.1234, "theta": -0.0512, "vega": 0.2398},
                    "impliedVolatility": 0.3045,
                    "latestQuote": {"ap": 14.50, "as": 50, "ax": "N", "bp": 14.25, "bs": 80, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "AAPL250221C00150000": {
                    "greeks": {"delta": 0.5823, "gamma": 0.0189, "rho": 0.1845, "theta": -0.0434, "vega": 0.3234},
                    "impliedVolatility": 0.2734,
                    "latestQuote": {"ap": 18.75, "as": 40, "ax": "N", "bp": 18.50, "bs": 65, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                }
            }
        }
        """,
    )

    chain = option_helper.get_option_chain(underlying, expiration=expiration)

    # Should only get options with matching expiration
    assert len(chain) == 6  # 3 calls + 3 puts for Jan 17, 2025

    # Verify all have correct expiration
    for option in chain:
        assert option.expiration == expiration
        assert option.symbol.startswith("AAPL250117")

    # Verify we have both calls and puts
    calls = [opt for opt in chain if opt.option_type == "call"]
    puts = [opt for opt in chain if opt.option_type == "put"]
    assert len(calls) == 3
    assert len(puts) == 3

    # Verify strikes are parsed correctly
    strikes = sorted({opt.strike for opt in chain})
    assert strikes == [145.0, 150.0, 155.0]


def test_get_option_chain_no_expiration_filter(reqmock, option_helper: OptionHelper):
    """Test getting option chain without expiration filter."""
    underlying = "SPY"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots/{underlying}",
        text="""
        {
            "snapshots": {
                "SPY241220C00450000": {
                    "latestQuote": {"ap": 5.50, "as": 100, "ax": "N", "bp": 5.45, "bs": 150, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                },
                "SPY250117C00450000": {
                    "latestQuote": {"ap": 7.25, "as": 80, "ax": "N", "bp": 7.20, "bs": 120, "bx": "N", "c": "A", "t": "2024-11-09T15:30:00Z"}
                }
            }
        }
        """,
    )

    chain = option_helper.get_option_chain(underlying)

    # Should get all options regardless of expiration
    assert len(chain) == 2
    expirations = sorted({opt.expiration for opt in chain})
    assert expirations == [datetime(2024, 12, 20), datetime(2025, 1, 17)]


def test_get_option_chain_empty(reqmock, option_helper: OptionHelper):
    """Test getting option chain with no results."""
    underlying = "INVALID"

    reqmock.get(
        f"https://data.alpaca.markets/v1beta1/options/snapshots/{underlying}",
        text='{"snapshots": {}}',
    )

    chain = option_helper.get_option_chain(underlying)

    assert chain == []


def test_option_data_mid_calculation():
    """Test that mid price is calculated correctly."""
    data = OptionData(
        symbol="TEST250117C00100000",
        strike=100.0,
        expiration=datetime(2025, 1, 17),
        option_type="call",
        bid=10.0,
        ask=10.50,
        mid=None,  # Should be calculated
        last_price=None,
        delta=None,
        gamma=None,
        theta=None,
        vega=None,
        rho=None,
        volume=None,
        open_interest=None,
        implied_volatility=None,
        bid_size=None,
        ask_size=None,
        last_size=None,
        timestamp=None,
    )

    # Mid should be calculated from bid/ask
    assert data.mid == 10.25


def test_option_data_mid_missing_bid():
    """Test mid calculation when bid is missing."""
    data = OptionData(
        symbol="TEST250117C00100000",
        strike=100.0,
        expiration=datetime(2025, 1, 17),
        option_type="call",
        bid=None,
        ask=10.50,
        mid=None,
        last_price=None,
        delta=None,
        gamma=None,
        theta=None,
        vega=None,
        rho=None,
        volume=None,
        open_interest=None,
        implied_volatility=None,
        bid_size=None,
        ask_size=None,
        last_size=None,
        timestamp=None,
    )

    # Mid should be None if bid or ask is missing
    assert data.mid is None


def test_option_data_repr():
    """Test OptionData string representation."""
    data = OptionData(
        symbol="AAPL250117C00150000",
        strike=150.0,
        expiration=datetime(2025, 1, 17),
        option_type="call",
        bid=12.50,
        ask=12.75,
        mid=12.625,
        last_price=12.60,
        delta=0.6234,
        gamma=0.0234,
        theta=-0.0512,
        vega=0.2345,
        rho=0.1234,
        volume=1000,
        open_interest=5000,
        implied_volatility=0.2845,
        bid_size=100,
        ask_size=50,
        last_size=25,
        timestamp=datetime(2024, 11, 9, 15, 30, tzinfo=timezone.utc),
    )

    repr_str = repr(data)

    # Should include key information
    assert "AAPL250117C00150000" in repr_str
    assert "150.0" in repr_str
    assert "12.50" in repr_str or "12.5" in repr_str
    assert "28.45%" in repr_str  # IV formatted
    assert "0.6234" in repr_str  # Delta
