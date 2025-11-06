"""Tests for analytics analyzer."""

import pytest
from datetime import datetime

from src.processing.analyzer import AnalyticsAnalyzer, MetricChange
from src.google_analytics.models import (
    GAAnalyticsData,
    AudienceMetrics,
    EngagementMetrics,
    ConversionMetrics,
)


@pytest.fixture
def sample_analytics_data():
    """Create sample analytics data for testing."""
    return GAAnalyticsData(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        audience=AudienceMetrics(
            total_users=5000,
            new_users=2000,
            sessions=10000,
        ),
        engagement=EngagementMetrics(
            average_engagement_time=120.5,
            engaged_sessions=7000,
            engagement_rate=70.0,
        ),
        conversions=ConversionMetrics(
            form_submits=50,
            email_clicks=30,
            phone_clicks=20,
        ),
        acquisition=[],
        geographic=[],
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
    
    # total_views maps to sessions
    assert summary.total_views.current == 10000
    # unique_visitors maps to total_users
    assert summary.unique_visitors.current == 5000
    assert summary.period_days == 30
    # Check conversion metrics
    assert summary.total_conversions.current == 100  # 50 + 30 + 20
    assert summary.engagement_rate.current == 70.0
