# NewsHelper - Simplified News API

A streamlined interface for accessing financial news data from Alpaca's News API.

## Quick Start

```python
from alpaca.data.news_helper import NewsHelper

# Auto-loads credentials from environment variables
helper = NewsHelper()

# Get latest news for Apple
articles = helper.get_news_for_symbol("AAPL", days_back=7)

for article in articles:
    print(f"{article.headline}")
    print(f"  Source: {article.source}")
    print(f"  Symbols: {', '.join(article.symbols)}")
```

## Why NewsHelper?

**Before (Complex):**
```python
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from datetime import datetime, timedelta, timezone

# Manual initialization
client = NewsClient(api_key="...", secret_key="...")

# Complex request object
end = datetime.now(timezone.utc)
start = end - timedelta(days=7)
request = NewsRequest(
    symbols="AAPL",
    start=start,
    end=end,
    limit=50,
    include_content=True
)

# Parse nested response
news_set = client.get_news(request_params=request)
articles = []
for news_item in news_set.data["news"]:
    # Manual field extraction
    articles.append({
        "headline": news_item.headline,
        "source": news_item.source,
        # ... more fields
    })
```

**After (Simple):**
```python
from alpaca.data.news_helper import NewsHelper

helper = NewsHelper()  # Auto-loads credentials

# Simple method call
articles = helper.get_news_for_symbol("AAPL", days_back=7)

# Clean dataclass objects
for article in articles:
    print(f"{article.headline} - {article.source}")
```

## Configuration

### Environment Variables

The helper automatically loads credentials from your environment:

```bash
# .env file
APCA_API_KEY_ID=your_api_key
APCA_API_SECRET_KEY=your_secret_key
```

### Explicit Credentials

```python
helper = NewsHelper(
    api_key="your_api_key",
    secret_key="your_secret_key"
)
```

## Features

### ✅ Automatic Environment Loading
- Reads `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` from environment
- No manual client initialization required

### ✅ Simple Parameters
- `days_back` instead of datetime calculations
- Lists of symbols instead of comma-separated strings
- Native Python types throughout

### ✅ Clean Data Models
- `NewsArticle` dataclass with all fields
- Direct access to headlines, content, images
- Parsed datetime objects

### ✅ Convenience Methods
- `get_latest_news()` - Most recent articles
- `get_breaking_news()` - News from the last hour
- `get_news_for_symbol()` - Single-symbol convenience
- `search_news()` - Historical news search

## API Reference

### NewsArticle Dataclass

```python
@dataclass
class NewsArticle:
    id: int                      # Unique article ID
    headline: str                # Article headline/title
    source: str                  # News source (e.g., "Benzinga")
    author: str                  # Article author
    summary: str                 # Brief summary
    content: str                 # Full content (may contain HTML)
    url: Optional[str]           # Link to original article
    symbols: List[str]           # Ticker symbols mentioned
    created_at: datetime         # Creation time (UTC)
    updated_at: datetime         # Last update time (UTC)
    image_urls: List[str]        # Associated image URLs
```

### get_news()

Get news articles with flexible filtering.

```python
articles = helper.get_news(
    symbols=["AAPL", "TSLA"],     # Optional: filter by symbols
    days_back=7,                   # Optional: days back from now
    start=datetime(...),           # Optional: specific start time
    end=datetime(...),             # Optional: specific end time
    limit=50,                      # Max articles (default: 50)
    include_content=True,          # Include full content (default: True)
    exclude_contentless=False,     # Exclude articles without content
    sort="desc"                    # Sort order: "asc" or "desc"
)
```

**Examples:**

```python
# Get news for AAPL from the past week
articles = helper.get_news(symbols=["AAPL"], days_back=7)

# Get news for multiple symbols
articles = helper.get_news(symbols=["AAPL", "MSFT", "GOOGL"], limit=20)

# Get all market news (no symbol filter)
articles = helper.get_news(days_back=1, limit=50)

# Specific date range
from datetime import datetime, timezone
start = datetime(2024, 1, 1, tzinfo=timezone.utc)
end = datetime(2024, 1, 31, tzinfo=timezone.utc)
articles = helper.get_news(symbols=["NVDA"], start=start, end=end)
```

### get_news_for_symbol()

Convenience method for getting news for a single stock.

```python
articles = helper.get_news_for_symbol(
    symbol="AAPL",                 # Stock ticker
    days_back=7,                   # Days back (default: 7)
    limit=50,                      # Max articles (default: 50)
    include_content=True           # Include content (default: True)
)
```

**Examples:**

```python
# Last week's Apple news
articles = helper.get_news_for_symbol("AAPL", days_back=7)

# Yesterday's Tesla news
articles = helper.get_news_for_symbol("TSLA", days_back=1, limit=10)
```

### get_latest_news()

Get the most recent news articles.

```python
articles = helper.get_latest_news(
    symbols=None,                  # Optional: filter by symbols
    limit=10,                      # Max articles (default: 10)
    include_content=True           # Include content (default: True)
)
```

**Examples:**

```python
# Latest 5 articles for tech stocks
articles = helper.get_latest_news(
    symbols=["AAPL", "GOOGL", "MSFT"],
    limit=5
)

# Latest general market news
articles = helper.get_latest_news(limit=10)
```

### get_breaking_news()

Get very recent "breaking" news from the last few hours.

```python
articles = helper.get_breaking_news(
    symbols=None,                  # Optional: filter by symbols
    hours_back=1,                  # Hours back (default: 1)
    limit=20                       # Max articles (default: 20)
)
```

**Examples:**

```python
# News from the last hour
breaking = helper.get_breaking_news(hours_back=1)

# Breaking Tesla news from last 2 hours
breaking = helper.get_breaking_news(symbols=["TSLA"], hours_back=2)
```

### search_news()

Search for news articles over a longer period (useful for analysis).

```python
articles = helper.search_news(
    symbols=["NVDA"],              # Symbols to search for
    days_back=30,                  # Days back (default: 30)
    limit=100,                     # Max articles (default: 100)
    include_content=True           # Include content (default: True)
)
```

**Examples:**

```python
# NVDA news from the past month
articles = helper.search_news(["NVDA"], days_back=30, limit=100)

# Analyze news volume
print(f"Found {len(articles)} articles in the past month")
```

### get_multi_symbol_news()

Get news mentioning any of multiple symbols (portfolio monitoring).

```python
articles = helper.get_multi_symbol_news(
    symbols=["AAPL", "MSFT", "GOOGL"],  # List of symbols
    days_back=7,                         # Days back (default: 7)
    limit=50                             # Max articles (default: 50)
)
```

**Examples:**

```python
# Monitor FAANG stocks
faang = ["META", "AAPL", "AMZN", "NFLX", "GOOGL"]
articles = helper.get_multi_symbol_news(faang, days_back=3)

for article in articles:
    print(f"{article.headline}")
    print(f"  Mentions: {', '.join(article.symbols)}")
```

## Practical Examples

### Example 1: Latest News Feed

```python
from alpaca.data.news_helper import NewsHelper

helper = NewsHelper()

# Get latest 10 articles
articles = helper.get_latest_news(limit=10)

for article in articles:
    print(f"{article.headline}")
    print(f"  Source: {article.source}")
    print(f"  Time: {article.created_at}")
    print()
```

### Example 2: Stock-Specific News

```python
# Monitor Tesla news
articles = helper.get_news_for_symbol("TSLA", days_back=7)

print(f"Found {len(articles)} TSLA articles this week")
for article in articles[:5]:
    print(f"- {article.headline}")
```

### Example 3: Portfolio News Monitoring

```python
# Monitor your portfolio
portfolio = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
articles = helper.get_multi_symbol_news(portfolio, days_back=1)

# Group by symbol
by_symbol = {}
for article in articles:
    for symbol in article.symbols:
        if symbol in portfolio:
            by_symbol.setdefault(symbol, []).append(article)

for symbol, symbol_articles in by_symbol.items():
    print(f"{symbol}: {len(symbol_articles)} articles")
```

### Example 4: Breaking News Alerts

```python
# Check for breaking news every hour
breaking = helper.get_breaking_news(hours_back=1, limit=20)

if breaking:
    print(f"🚨 {len(breaking)} breaking news articles!")
    for article in breaking:
        print(f"- {article.headline}")
        print(f"  Symbols: {', '.join(article.symbols)}")
```

### Example 5: Historical Analysis

```python
from datetime import datetime, timezone

# Analyze NVDA news coverage in Q1 2024
start = datetime(2024, 1, 1, tzinfo=timezone.utc)
end = datetime(2024, 3, 31, tzinfo=timezone.utc)
articles = helper.get_news(symbols=["NVDA"], start=start, end=end, limit=200)

# Count by source
sources = {}
for article in articles:
    sources[article.source] = sources.get(article.source, 0) + 1

print(f"Q1 2024 NVDA News Analysis:")
print(f"Total articles: {len(articles)}")
print(f"Sources: {len(sources)}")
for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {source}: {count} articles")
```

### Example 6: Sentiment Data Collection

```python
# Collect news for sentiment analysis
articles = helper.search_news(
    ["AAPL"],
    days_back=30,
    limit=100,
    include_content=True
)

# Extract text for analysis
texts = []
for article in articles:
    texts.append({
        "headline": article.headline,
        "summary": article.summary,
        "content": article.content,
        "date": article.created_at,
    })

print(f"Collected {len(texts)} articles for sentiment analysis")
```

## Date Range Parameters

You can specify time ranges in three ways:

1. **days_back** - Simple days back from now:
   ```python
   articles = helper.get_news(symbols=["AAPL"], days_back=7)
   ```

2. **start and end** - Specific datetime range:
   ```python
   from datetime import datetime, timezone
   start = datetime(2024, 1, 1, tzinfo=timezone.utc)
   end = datetime(2024, 1, 31, tzinfo=timezone.utc)
   articles = helper.get_news(symbols=["AAPL"], start=start, end=end)
   ```

3. **hours_back** - For breaking news:
   ```python
   breaking = helper.get_breaking_news(hours_back=2)
   ```

## News Sources

Articles come from various financial news sources including:
- Benzinga
- Reuters
- Bloomberg
- MarketWatch
- And many others

Use the `source` field to filter or group articles:

```python
articles = helper.get_news(symbols=["AAPL"], days_back=7)

by_source = {}
for article in articles:
    by_source.setdefault(article.source, []).append(article)

for source, source_articles in by_source.items():
    print(f"{source}: {len(source_articles)} articles")
```

## Content and Images

### Full Article Content

Set `include_content=True` to get full article text:

```python
articles = helper.get_news_for_symbol(
    "TSLA",
    days_back=1,
    include_content=True
)

for article in articles:
    print(f"Headline: {article.headline}")
    print(f"Content: {article.content[:500]}...")  # First 500 chars
```

### Exclude Articles Without Content

```python
articles = helper.get_news(
    symbols=["MSFT"],
    days_back=7,
    include_content=True,
    exclude_contentless=True
)
```

### Images

Access article images via the `image_urls` list:

```python
for article in articles:
    if article.image_urls:
        print(f"{article.headline}")
        print(f"  Images: {len(article.image_urls)}")
        for url in article.image_urls:
            print(f"    - {url}")
```

## Migration Guide

### From NewsClient to NewsHelper

**Before:**
```python
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from datetime import datetime, timedelta, timezone

client = NewsClient(api_key="...", secret_key="...")

end = datetime.now(timezone.utc)
start = end - timedelta(days=7)
request = NewsRequest(
    symbols="AAPL,MSFT",
    start=start,
    end=end,
    limit=50,
    include_content=True
)

news_set = client.get_news(request_params=request)
articles = []
for news_item in news_set.data["news"]:
    articles.append({
        "headline": news_item.headline,
        "source": news_item.source,
        "created_at": news_item.created_at,
        # ... manual extraction
    })
```

**After:**
```python
from alpaca.data.news_helper import NewsHelper

helper = NewsHelper()  # Auto-loads credentials

articles = helper.get_news(
    symbols=["AAPL", "MSFT"],
    days_back=7,
    limit=50
)

# articles is a list of NewsArticle dataclasses
for article in articles:
    print(f"{article.headline} - {article.source}")
```

## Error Handling

```python
from alpaca.data.news_helper import NewsHelper

try:
    helper = NewsHelper()
    articles = helper.get_news_for_symbol("AAPL", days_back=7)
    
    if not articles:
        print("No articles found")
    else:
        for article in articles:
            print(article.headline)
            
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## See Also

- [StockHelper](./simplified_stock_data_api.md) - Stock market data
- [CryptoHelper](./simplified_crypto_data_api.md) - Cryptocurrency data
- [TradingHelper](./simplified_trading_api.md) - Order execution
- [AccountHelper](./simplified_account_api.md) - Account management
- [OptionHelper](../README.md#optionhelper) - Options trading

## Complete Example

```python
from alpaca.data.news_helper import NewsHelper

def monitor_portfolio_news():
    """Monitor news for a portfolio of stocks."""
    helper = NewsHelper()
    
    # Your portfolio
    portfolio = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    # Get today's news
    articles = helper.get_multi_symbol_news(
        symbols=portfolio,
        days_back=1,
        limit=50
    )
    
    print(f"📰 Portfolio News Update ({len(articles)} articles)")
    print("=" * 60)
    
    # Group by symbol
    by_symbol = {}
    for article in articles:
        for symbol in article.symbols:
            if symbol in portfolio:
                by_symbol.setdefault(symbol, []).append(article)
    
    # Display by stock
    for symbol in portfolio:
        if symbol in by_symbol:
            print(f"\n{symbol} ({len(by_symbol[symbol])} articles):")
            for article in by_symbol[symbol][:3]:
                print(f"  • {article.headline}")
                print(f"    {article.source} - {article.created_at.strftime('%H:%M')}")
    
    # Show breaking news
    breaking = helper.get_breaking_news(
        symbols=portfolio,
        hours_back=1,
        limit=10
    )
    
    if breaking:
        print(f"\n🚨 BREAKING NEWS ({len(breaking)} articles):")
        for article in breaking:
            print(f"  • {article.headline}")
            print(f"    Symbols: {', '.join(article.symbols)}")

if __name__ == "__main__":
    monitor_portfolio_news()
```

---

**Benefits of NewsHelper:**
- ✅ 70% less boilerplate code
- ✅ Automatic credential loading
- ✅ Simple date handling with `days_back`
- ✅ Clean dataclass responses
- ✅ Convenience methods for common tasks
- ✅ No complex request objects
