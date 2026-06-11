import pytest
from dram_sentry.analytics.competitor import CompetitorAnalytics
from dram_sentry.settings import SUPPLIERS, CACHE_TTL

def test_competitor_analytics_initialization():
    analytics = CompetitorAnalytics()
    assert analytics is not None
    assert SUPPLIERS  # Ensure settings are loaded

def test_get_top_suppliers_returns_list():
    analytics = CompetitorAnalytics()
    top_suppliers = analytics.get_top_suppliers()
    assert isinstance(top_suppliers, list)
    assert len(top_suppliers) <= 5  # Top 5 suppliers

def test_get_price_trends_returns_dict():
    analytics = CompetitorAnalytics()
    trends = analytics.get_price_trends(period="1m")
    assert isinstance(trends, dict)
    assert "supplier" in trends and "price" in trends

def test_get_price_trends_invalid_period():
    analytics = CompetitorAnalytics()
    with pytest.raises(ValueError):
        analytics.get_price_trends(period="invalid")