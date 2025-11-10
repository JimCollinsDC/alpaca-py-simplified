"""
NewsHelper: Simplified interface for Alpaca News API.

This module provides an easy-to-use interface for accessing financial news data
without requiring complex request objects. It handles environment variables,
type conversions, and provides clean dataclass-based responses.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv

from alpaca.data.historical.news import NewsClient
from alpaca.data.models.news import News, NewsSet
from alpaca.data.requests import NewsRequest


@dataclass
class NewsArticle:
    """
    Simplified news article data.

    Attributes:
        id: Unique article ID
        headline: Article headline/title
        source: News source (e.g., "Benzinga", "Reuters")
        author: Article author
        summary: Brief summary of the article
        content: Full article content (may contain HTML)
        url: Link to original article
        symbols: List of ticker symbols mentioned in the article
        created_at: When the article was created (UTC)
        updated_at: When the article was last updated (UTC)
        image_urls: List of image URLs associated with the article
    """

    id: int
    headline: str
    source: str
    author: str
    summary: str
    content: str
    url: Optional[str]
    symbols: List[str]
    created_at: datetime
    updated_at: datetime
    image_urls: List[str]

    @classmethod
    def from_news(cls, news: News) -> "NewsArticle":
        """
        Convert News model to NewsArticle dataclass.

        Args:
            news: News object from the API

        Returns:
            NewsArticle with simplified data
        """
        image_urls = []
        if news.images:
            # Get all image URLs from the images list
            image_urls = [img.url for img in news.images]

        return cls(
            id=news.id,
            headline=news.headline,
            source=news.source,
            author=news.author,
            summary=news.summary,
            content=news.content,
            url=news.url,
            symbols=news.symbols,
            created_at=news.created_at,
            updated_at=news.updated_at,
            image_urls=image_urls,
        )


class NewsHelper:
    """
    Simplified interface for Alpaca News API.

    This helper provides easy access to financial news data without requiring
    complex request objects. All methods accept simple Python types and return
    clean dataclass instances.

    Environment Variables:
        APCA_API_KEY_ID: Your Alpaca API key
        APCA_API_SECRET_KEY: Your Alpaca API secret

    Example:
        >>> helper = NewsHelper()
        >>> # Get latest news for Apple
        >>> articles = helper.get_news(symbols=["AAPL"], limit=5)
        >>> for article in articles:
        ...     print(f"{article.headline} - {article.source}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: bool = False,
    ):
        """
        Initialize NewsHelper.

        Args:
            api_key: Alpaca API key (if None, loads from APCA_API_KEY_ID env var)
            secret_key: Alpaca secret key (if None, loads from APCA_API_SECRET_KEY env var)
            paper: Whether to use paper trading (default: False, not applicable for news data)

        Raises:
            ValueError: If API credentials are not provided and not found in environment
        """
        # Load environment variables
        load_dotenv()

        # Get credentials from parameters or environment
        self._api_key = api_key or os.getenv("APCA_API_KEY_ID")
        self._secret_key = secret_key or os.getenv("APCA_API_SECRET_KEY")

        if not self._api_key or not self._secret_key:
            raise ValueError(
                "API credentials required. Provide api_key and secret_key parameters "
                "or set APCA_API_KEY_ID and APCA_API_SECRET_KEY environment variables."
            )

        # Initialize the news client
        self._client = NewsClient(
            api_key=self._api_key,
            secret_key=self._secret_key,
        )

    def get_news(
        self,
        symbols: Optional[List[str]] = None,
        days_back: Optional[int] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 50,
        include_content: bool = True,
        exclude_contentless: bool = False,
        sort: str = "desc",
    ) -> List[NewsArticle]:
        """
        Get news articles with optional filtering.

        Args:
            symbols: List of ticker symbols to filter by (e.g., ["AAPL", "TSLA"])
            days_back: Number of days back to fetch news (alternative to start)
            start: Start datetime for news range (UTC)
            end: End datetime for news range (UTC, default: now)
            limit: Maximum number of articles to return (default: 50)
            include_content: Whether to include full article content (default: True)
            exclude_contentless: Exclude articles without content (default: False)
            sort: Sort order - "asc" or "desc" by updated_at (default: "desc")

        Returns:
            List of NewsArticle objects

        Example:
            >>> # Get latest 10 articles for AAPL
            >>> articles = helper.get_news(symbols=["AAPL"], limit=10)
            >>> # Get news from the past week
            >>> articles = helper.get_news(symbols=["TSLA"], days_back=7)
            >>> # Get news for specific date range
            >>> start = datetime(2024, 1, 1, tzinfo=timezone.utc)
            >>> end = datetime(2024, 1, 31, tzinfo=timezone.utc)
            >>> articles = helper.get_news(symbols=["NVDA"], start=start, end=end)
        """
        # Handle date range
        if days_back is not None:
            end = end or datetime.now(timezone.utc)
            start = end - timedelta(days=days_back)
        elif start is None:
            # Default to last 7 days if no time range specified
            end = end or datetime.now(timezone.utc)
            start = end - timedelta(days=7)

        # Convert symbols list to comma-separated string
        symbols_str = None
        if symbols:
            symbols_str = ",".join(symbols)

        # Create request
        request = NewsRequest(
            symbols=symbols_str,
            start=start,
            end=end,
            limit=limit,
            include_content=include_content,
            exclude_contentless=exclude_contentless,
            sort=sort,
        )

        # Get news data
        news_set: NewsSet = self._client.get_news(request_params=request)

        # Convert to NewsArticle list
        articles = []
        if "news" in news_set.data:
            for news_item in news_set.data["news"]:
                articles.append(NewsArticle.from_news(news_item))

        return articles

    def get_news_for_symbol(
        self,
        symbol: str,
        days_back: int = 7,
        limit: int = 50,
        include_content: bool = True,
    ) -> List[NewsArticle]:
        """
        Get recent news articles for a single symbol.

        This is a convenience method for getting news for one symbol.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")
            days_back: Number of days back to fetch news (default: 7)
            limit: Maximum number of articles to return (default: 50)
            include_content: Whether to include full article content (default: True)

        Returns:
            List of NewsArticle objects

        Example:
            >>> # Get last week's news for Apple
            >>> articles = helper.get_news_for_symbol("AAPL", days_back=7)
            >>> for article in articles:
            ...     print(f"{article.headline}")
        """
        return self.get_news(
            symbols=[symbol],
            days_back=days_back,
            limit=limit,
            include_content=include_content,
        )

    def get_latest_news(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 10,
        include_content: bool = True,
    ) -> List[NewsArticle]:
        """
        Get the most recent news articles.

        Args:
            symbols: Optional list of symbols to filter by
            limit: Maximum number of articles to return (default: 10)
            include_content: Whether to include full article content (default: True)

        Returns:
            List of NewsArticle objects sorted by most recent

        Example:
            >>> # Get 5 most recent articles for tech stocks
            >>> articles = helper.get_latest_news(
            ...     symbols=["AAPL", "GOOGL", "MSFT"],
            ...     limit=5
            ... )
        """
        # Get news from the last 24 hours
        return self.get_news(
            symbols=symbols,
            days_back=1,
            limit=limit,
            include_content=include_content,
            sort="desc",
        )

    def get_breaking_news(
        self,
        symbols: Optional[List[str]] = None,
        hours_back: int = 1,
        limit: int = 20,
    ) -> List[NewsArticle]:
        """
        Get very recent "breaking" news articles.

        Args:
            symbols: Optional list of symbols to filter by
            hours_back: Number of hours back to search (default: 1)
            limit: Maximum number of articles to return (default: 20)

        Returns:
            List of NewsArticle objects from the last few hours

        Example:
            >>> # Get news from the last hour
            >>> breaking = helper.get_breaking_news(hours_back=1, limit=10)
            >>> # Get breaking news for specific stock
            >>> breaking = helper.get_breaking_news(symbols=["TSLA"], hours_back=2)
        """
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=hours_back)

        symbols_str = None
        if symbols:
            symbols_str = ",".join(symbols)

        request = NewsRequest(
            symbols=symbols_str,
            start=start,
            end=end,
            limit=limit,
            include_content=True,
            exclude_contentless=True,
            sort="desc",
        )

        news_set: NewsSet = self._client.get_news(request_params=request)

        articles = []
        if "news" in news_set.data:
            for news_item in news_set.data["news"]:
                articles.append(NewsArticle.from_news(news_item))

        return articles

    def search_news(
        self,
        symbols: List[str],
        days_back: int = 30,
        limit: int = 100,
        include_content: bool = True,
    ) -> List[NewsArticle]:
        """
        Search for news articles mentioning specific symbols.

        This is useful for building a news database or performing analysis
        on historical news coverage.

        Args:
            symbols: List of ticker symbols to search for
            days_back: Number of days back to search (default: 30)
            limit: Maximum number of articles to return (default: 100)
            include_content: Whether to include full article content (default: True)

        Returns:
            List of NewsArticle objects

        Example:
            >>> # Search for NVDA news from the past month
            >>> articles = helper.search_news(["NVDA"], days_back=30, limit=100)
            >>> # Analyze news volume
            >>> print(f"Found {len(articles)} articles in the past month")
        """
        return self.get_news(
            symbols=symbols,
            days_back=days_back,
            limit=limit,
            include_content=include_content,
            exclude_contentless=False,
            sort="desc",
        )

    def get_multi_symbol_news(
        self,
        symbols: List[str],
        days_back: int = 7,
        limit: int = 50,
    ) -> List[NewsArticle]:
        """
        Get news for multiple symbols efficiently.

        Retrieves news that mentions any of the provided symbols. Useful for
        monitoring a portfolio or watchlist.

        Args:
            symbols: List of ticker symbols (e.g., ["AAPL", "MSFT", "GOOGL"])
            days_back: Number of days back to fetch news (default: 7)
            limit: Maximum number of articles to return (default: 50)

        Returns:
            List of NewsArticle objects

        Example:
            >>> # Monitor portfolio companies
            >>> portfolio = ["AAPL", "MSFT", "GOOGL", "AMZN"]
            >>> articles = helper.get_multi_symbol_news(portfolio, days_back=3)
            >>> for article in articles:
            ...     print(f"{article.headline} - mentions {article.symbols}")
        """
        return self.get_news(
            symbols=symbols,
            days_back=days_back,
            limit=limit,
            include_content=True,
            sort="desc",
        )
