"""Tests for analytics analyzer."""

import pytest
from datetime import datetime

from src.processing.analyzer import AnalyticsAnalyzer, MetricChange
from src.vercel.models import AnalyticsData


@pytest.fixture
def sample_analytics_data():
    """Create sample analytics data for testing."""
    return AnalyticsData(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        total_views=10000,
        unique_visitors=5000,
        top_pages=[],
        traffic_sources=[],
        device_stats=[],
        geographic_data=[],
    )


def test_analyzer_initialization():
    """Test analyzer initialization."""
    analyzer = AnalyticsAnalyzer()
    assert analyzer is not None


def test_metric_comparison():
    """Test metric comparison logic."""
    analyzer = AnalyticsAnalyzer()
    
    # Test with previous data
    metric = analyzer._compare_metric(100, 80, "Test Metric")
    assert metric.current == 100
    assert metric.previous == 80
    assert metric.change == 20
    assert metric.change_percent == 25.0
    assert metric.trend == "up"
    
    # Test without previous data
    metric = analyzer._compare_metric(100, None, "Test Metric")
    assert metric.current == 100
    assert metric.previous is None
    assert metric.change is None


def test_analyze_with_data(sample_analytics_data):
    """Test analysis with sample data."""
    analyzer = AnalyticsAnalyzer()
    summary = analyzer.analyze(sample_analytics_data)
    
    assert summary.total_views.current == 10000
    assert summary.unique_visitors.current == 5000
    assert summary.period_days == 30
