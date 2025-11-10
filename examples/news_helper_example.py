"""
NewsHelper Examples

This script demonstrates how to use NewsHelper to access financial news
data from Alpaca's News API.
"""

from datetime import datetime, timezone

from alpaca.data.news_helper import NewsHelper


def example_1_latest_news():
    """Example 1: Get latest news articles."""
    print("\n=== Example 1: Latest News ===")

    helper = NewsHelper()

    # Get 10 most recent articles
    articles = helper.get_latest_news(limit=10)

    print(f"Found {len(articles)} recent articles:")
    for article in articles[:3]:  # Show first 3
        print(f"  - {article.headline}")
        print(f"    Source: {article.source} | Symbols: {', '.join(article.symbols)}")


def example_2_symbol_specific_news():
    """Example 2: Get news for a specific stock."""
    print("\n=== Example 2: Symbol-Specific News ===")

    helper = NewsHelper()

    # Get last week's news for Apple
    articles = helper.get_news_for_symbol("AAPL", days_back=7)

    print(f"Found {len(articles)} articles about AAPL in the past week:")
    for article in articles[:5]:
        print(f"  - {article.headline}")
        print(f"    {article.created_at.strftime('%Y-%m-%d %H:%M')} UTC")


def example_3_multi_symbol_news():
    """Example 3: Monitor news for a portfolio of stocks."""
    print("\n=== Example 3: Portfolio News Monitoring ===")

    helper = NewsHelper()

    # Monitor FAANG stocks
    portfolio = ["META", "AAPL", "AMZN", "NFLX", "GOOGL"]
    articles = helper.get_multi_symbol_news(portfolio, days_back=3, limit=20)

    print(f"Found {len(articles)} articles about portfolio stocks:")
    for article in articles[:5]:
        print(f"  - {article.headline}")
        print(f"    Mentions: {', '.join(article.symbols)}")


def example_4_breaking_news():
    """Example 4: Get breaking news from the last hour."""
    print("\n=== Example 4: Breaking News ===")

    helper = NewsHelper()

    # Get very recent news
    breaking = helper.get_breaking_news(hours_back=1, limit=10)

    print(f"Found {len(breaking)} breaking news articles:")
    for article in breaking[:3]:
        print(f"  - {article.headline}")
        print(f"    Source: {article.source}")
        print(f"    Time: {article.created_at.strftime('%Y-%m-%d %H:%M')} UTC")


def example_5_date_range_search():
    """Example 5: Search news for a specific date range."""
    print("\n=== Example 5: Date Range Search ===")

    helper = NewsHelper()

    # Get news for NVDA in January 2024
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 31, tzinfo=timezone.utc)
    articles = helper.get_news(
        symbols=["NVDA"],
        start=start,
        end=end,
        limit=50
    )

    print(f"Found {len(articles)} NVDA articles in January 2024:")
    for article in articles[:5]:
        print(f"  - {article.headline}")
        print(f"    {article.created_at.strftime('%Y-%m-%d')}")


def example_6_news_with_content():
    """Example 6: Access full article content."""
    print("\n=== Example 6: Full Article Content ===")

    helper = NewsHelper()

    # Get news with full content
    articles = helper.get_news_for_symbol(
        "TSLA",
        days_back=1,
        include_content=True
    )

    if articles:
        article = articles[0]
        print(f"Headline: {article.headline}")
        print(f"Source: {article.source}")
        print(f"Author: {article.author}")
        print(f"Summary: {article.summary}")
        print(f"Content preview: {article.content[:200]}...")
        print(f"URL: {article.url}")
        print(f"Images: {len(article.image_urls)} images")


def example_7_news_filtering():
    """Example 7: Filter news by content availability."""
    print("\n=== Example 7: Content Filtering ===")

    helper = NewsHelper()

    # Only get articles that have full content
    articles = helper.get_news(
        symbols=["MSFT"],
        days_back=7,
        include_content=True,
        exclude_contentless=True,
        limit=20
    )

    print(f"Found {len(articles)} MSFT articles with full content:")
    for article in articles[:3]:
        print(f"  - {article.headline}")
        print(f"    Content length: {len(article.content)} characters")


def example_8_search_historical_news():
    """Example 8: Search historical news for analysis."""
    print("\n=== Example 8: Historical News Search ===")

    helper = NewsHelper()

    # Search for news mentions over the past month
    articles = helper.search_news(
        ["AMD"],
        days_back=30,
        limit=100
    )

    print(f"Found {len(articles)} AMD articles in the past month")

    # Analyze by source
    sources = {}
    for article in articles:
        sources[article.source] = sources.get(article.source, 0) + 1

    print("Articles by source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {source}: {count} articles")


def example_9_sector_news_monitoring():
    """Example 9: Monitor news for an entire sector."""
    print("\n=== Example 9: Sector News Monitoring ===")

    helper = NewsHelper()

    # Tech sector stocks
    tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
    articles = helper.get_multi_symbol_news(tech_stocks, days_back=1, limit=30)

    print(f"Found {len(articles)} tech sector articles in the past day:")

    # Show most mentioned stocks
    mentions = {}
    for article in articles:
        for symbol in article.symbols:
            if symbol in tech_stocks:
                mentions[symbol] = mentions.get(symbol, 0) + 1

    print("\nMost mentioned tech stocks:")
    for symbol, count in sorted(mentions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {symbol}: {count} articles")


def example_10_old_vs_new_api():
    """Example 10: Compare old API vs NewsHelper."""
    print("\n=== Example 10: Old API vs NewsHelper Comparison ===")

    print("OLD WAY (Complex):")
    print("""
    from alpaca.data.historical.news import NewsClient
    from alpaca.data.requests import NewsRequest
    from datetime import datetime, timedelta, timezone

    # Initialize client
    client = NewsClient(api_key="...", secret_key="...")

    # Create complex request object
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    request = NewsRequest(
        symbols="AAPL,MSFT",
        start=start,
        end=end,
        limit=50,
        include_content=True
    )

    # Get news and parse response
    news_set = client.get_news(request_params=request)
    articles = []
    for news_item in news_set.data["news"]:
        articles.append({
            "headline": news_item.headline,
            "source": news_item.source,
            # ... manual field extraction
        })
    """)

    print("\nNEW WAY (Simple):")
    print("""
    from alpaca.data.news_helper import NewsHelper

    # Auto-loads credentials from environment
    helper = NewsHelper()

    # Get news with simple parameters
    articles = helper.get_news(
        symbols=["AAPL", "MSFT"],
        days_back=7,
        limit=50
    )

    # Clean dataclass objects ready to use
    for article in articles:
        print(f"{article.headline} - {article.source}")
    """)

    print("\n✅ 70% less code with NewsHelper!")


def main():
    """Run all examples."""
    print("NewsHelper Examples")
    print("=" * 60)

    examples = [
        example_1_latest_news,
        example_2_symbol_specific_news,
        example_3_multi_symbol_news,
        example_4_breaking_news,
        example_5_date_range_search,
        example_6_news_with_content,
        example_7_news_filtering,
        example_8_search_historical_news,
        example_9_sector_news_monitoring,
        example_10_old_vs_new_api,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")

    print("\n" + "=" * 60)
    print("Examples complete!")


if __name__ == "__main__":
    main()
