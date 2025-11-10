"""
Tests for NewsHelper
"""

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from alpaca.data.models.news import News, NewsSet
from alpaca.data.news_helper import NewsArticle, NewsHelper


@pytest.fixture
def mock_news_data():
    """Fixture providing sample news data."""
    return {
        "news": [
            {
                "id": 12345,
                "headline": "Apple announces new iPhone",
                "source": "TechNews",
                "author": "John Smith",
                "summary": "Apple unveils latest iPhone model",
                "content": "Full article content here...",
                "url": "https://example.com/article1",
                "symbols": ["AAPL"],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "images": [
                    {"size": "large", "url": "https://example.com/img1.jpg"},
                    {"size": "thumb", "url": "https://example.com/thumb1.jpg"},
                ],
            },
            {
                "id": 12346,
                "headline": "Tesla reports strong earnings",
                "source": "FinanceDaily",
                "author": "Jane Doe",
                "summary": "Tesla beats earnings estimates",
                "content": "Tesla's Q4 earnings exceeded expectations...",
                "url": "https://example.com/article2",
                "symbols": ["TSLA"],
                "created_at": "2024-01-15T11:00:00Z",
                "updated_at": "2024-01-15T11:15:00Z",
                "images": [],
            },
        ]
    }


@pytest.fixture
def mock_news_set(mock_news_data):
    """Fixture providing a NewsSet object."""
    news_set = MagicMock(spec=NewsSet)
    news_set.data = {"news": [News(raw_data=n) for n in mock_news_data["news"]]}
    news_set.next_page_token = None
    return news_set


class TestNewsArticle:
    """Tests for NewsArticle dataclass."""

    def test_from_news_with_images(self, mock_news_data):
        """Test converting News to NewsArticle with images."""
        news = News(raw_data=mock_news_data["news"][0])
        article = NewsArticle.from_news(news)

        assert article.id == 12345
        assert article.headline == "Apple announces new iPhone"
        assert article.source == "TechNews"
        assert article.author == "John Smith"
        assert article.summary == "Apple unveils latest iPhone model"
        assert article.content == "Full article content here..."
        assert article.url == "https://example.com/article1"
        assert article.symbols == ["AAPL"]
        assert len(article.image_urls) == 2
        assert "https://example.com/img1.jpg" in article.image_urls

    def test_from_news_without_images(self, mock_news_data):
        """Test converting News to NewsArticle without images."""
        news = News(raw_data=mock_news_data["news"][1])
        article = NewsArticle.from_news(news)

        assert article.id == 12346
        assert article.headline == "Tesla reports strong earnings"
        assert len(article.image_urls) == 0


class TestNewsHelperInit:
    """Tests for NewsHelper initialization."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        helper = NewsHelper()
        assert helper._api_key == "test_key"
        assert helper._secret_key == "test_secret"

    def test_init_with_explicit_keys(self):
        """Test initialization with explicit API keys."""
        helper = NewsHelper(api_key="my_key", secret_key="my_secret")
        assert helper._api_key == "my_key"
        assert helper._secret_key == "my_secret"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_credentials_raises_error(self):
        """Test that initialization fails without credentials."""
        with pytest.raises(ValueError, match="API credentials required"):
            NewsHelper()


class TestGetNews:
    """Tests for get_news method."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_basic(self, mock_news_set):
        """Test basic news retrieval."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_news(symbols=["AAPL"], limit=10)

        assert len(articles) == 2
        assert articles[0].headline == "Apple announces new iPhone"
        assert articles[0].symbols == ["AAPL"]
        helper._client.get_news.assert_called_once()

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_with_days_back(self, mock_news_set):
        """Test news retrieval with days_back parameter."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_news(symbols=["TSLA"], days_back=7)

        assert len(articles) == 2
        helper._client.get_news.assert_called_once()
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "TSLA"

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_with_date_range(self, mock_news_set):
        """Test news retrieval with specific date range."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 31, tzinfo=timezone.utc)
        articles = helper.get_news(symbols=["NVDA"], start=start, end=end)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.start == start
        assert request.end == end

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_multiple_symbols(self, mock_news_set):
        """Test news retrieval for multiple symbols."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_news(symbols=["AAPL", "TSLA", "MSFT"], limit=50)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "AAPL,TSLA,MSFT"

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_with_content_options(self, mock_news_set):
        """Test news retrieval with content filtering options."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        helper.get_news(
            symbols=["AAPL"],
            include_content=False,
            exclude_contentless=True,
        )

        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.include_content is False
        assert request.exclude_contentless is True

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_with_sort(self, mock_news_set):
        """Test news retrieval with sort order."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        helper.get_news(symbols=["AAPL"], sort="asc")

        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.sort == "asc"

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_no_symbols(self, mock_news_set):
        """Test news retrieval without symbol filter."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_news(days_back=1, limit=20)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols is None


class TestGetNewsForSymbol:
    """Tests for get_news_for_symbol convenience method."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_news_for_symbol(self, mock_news_set):
        """Test getting news for a single symbol."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_news_for_symbol("AAPL", days_back=7)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "AAPL"
        assert request.limit == 50


class TestGetLatestNews:
    """Tests for get_latest_news method."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_latest_news_with_symbols(self, mock_news_set):
        """Test getting latest news for specific symbols."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_latest_news(symbols=["AAPL", "MSFT"], limit=5)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "AAPL,MSFT"
        assert request.limit == 5
        assert request.sort == "desc"

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_latest_news_all_symbols(self, mock_news_set):
        """Test getting latest news for all symbols."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_latest_news(limit=10)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols is None


class TestGetBreakingNews:
    """Tests for get_breaking_news method."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_breaking_news(self, mock_news_set):
        """Test getting breaking news from the last hour."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.get_breaking_news(hours_back=1, limit=10)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.limit == 10
        assert request.exclude_contentless is True

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_breaking_news_with_symbols(self, mock_news_set):
        """Test getting breaking news for specific symbols."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        helper.get_breaking_news(symbols=["TSLA"], hours_back=2)

        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "TSLA"


class TestSearchNews:
    """Tests for search_news method."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_search_news(self, mock_news_set):
        """Test searching for news articles."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        articles = helper.search_news(["NVDA"], days_back=30, limit=100)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "NVDA"
        assert request.limit == 100
        assert request.exclude_contentless is False


class TestGetMultiSymbolNews:
    """Tests for get_multi_symbol_news method."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_get_multi_symbol_news(self, mock_news_set):
        """Test getting news for multiple symbols."""
        helper = NewsHelper()
        helper._client.get_news = MagicMock(return_value=mock_news_set)

        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        articles = helper.get_multi_symbol_news(symbols, days_back=3, limit=50)

        assert len(articles) == 2
        call_args = helper._client.get_news.call_args
        request = call_args.kwargs["request_params"]
        assert request.symbols == "AAPL,MSFT,GOOGL,AMZN"
        assert request.limit == 50


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_empty_news_response(self):
        """Test handling empty news response."""
        helper = NewsHelper()
        empty_news_set = MagicMock(spec=NewsSet)
        empty_news_set.data = {"news": []}
        helper._client.get_news = MagicMock(return_value=empty_news_set)

        articles = helper.get_news(symbols=["INVALID"])

        assert len(articles) == 0

    @patch.dict(os.environ, {"APCA_API_KEY_ID": "test_key", "APCA_API_SECRET_KEY": "test_secret"})
    def test_news_without_news_key(self):
        """Test handling response without 'news' key."""
        helper = NewsHelper()
        news_set = MagicMock(spec=NewsSet)
        news_set.data = {}
        helper._client.get_news = MagicMock(return_value=news_set)

        articles = helper.get_news(symbols=["AAPL"])

        assert len(articles) == 0
