"""Tests for Google Analytics client."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.google_analytics.client import GoogleAnalyticsClient, GoogleAnalyticsAPIError
from src.google_analytics.models import (
    GAAnalyticsData,
    AudienceMetrics,
    EngagementMetrics,
)


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock()
    settings.ga_property_id = "123456789"
    settings.ga_credentials_file = "test_credentials.json"
    settings.GA_CREDENTIALS_JSON_BASE64 = None
    return settings


@pytest.fixture
def mock_credentials_file(tmp_path):
    """Create a temporary credentials file."""
    creds_file = tmp_path / "test_credentials.json"
    creds_file.write_text('{"type":"service_account","project_id":"test"}')
    return str(creds_file)


def test_client_initialization_with_file(mock_settings, mock_credentials_file):
    """Test client initialization with credentials file."""
    mock_settings.ga_credentials_file = mock_credentials_file
    
    with patch("src.google_analytics.client.service_account.Credentials.from_service_account_file") as mock_creds:
        with patch("src.google_analytics.client.BetaAnalyticsDataClient"):
            mock_creds.return_value = Mock()
            client = GoogleAnalyticsClient(mock_settings)
            assert client.property_id == "123456789"


def test_client_initialization_with_json(mock_settings):
    """Test client initialization with JSON credentials."""
    mock_settings.ga_credentials_file = None
    mock_settings.GA_CREDENTIALS_JSON_BASE64 = '{"type":"service_account","project_id":"test"}'
    
    with patch("src.google_analytics.client.service_account.Credentials.from_service_account_info") as mock_creds:
        with patch("src.google_analytics.client.BetaAnalyticsDataClient"):
            mock_creds.return_value = Mock()
            client = GoogleAnalyticsClient(mock_settings)
            assert client.property_id == "123456789"


def test_client_initialization_no_credentials(mock_settings):
    """Test client initialization fails without credentials."""
    mock_settings.ga_credentials_file = None
    mock_settings.GA_CREDENTIALS_JSON_BASE64 = None
    
    with pytest.raises(GoogleAnalyticsAPIError, match="No Google Analytics credentials"):
        GoogleAnalyticsClient(mock_settings)


@patch("src.google_analytics.client.BetaAnalyticsDataClient")
@patch("src.google_analytics.client.service_account.Credentials.from_service_account_file")
def test_fetch_audience_metrics(mock_creds, mock_client_class, mock_settings, mock_credentials_file):
    """Test fetching audience metrics."""
    mock_settings.ga_credentials_file = mock_credentials_file
    
    # Mock API response
    mock_response = Mock()
    mock_row = Mock()
    mock_row.metric_values = [
        Mock(value="5000"),  # total_users
        Mock(value="2000"),  # new_users
        Mock(value="10000"),  # sessions
    ]
    mock_response.rows = [mock_row]
    
    mock_client = Mock()
    mock_client.run_report.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    client = GoogleAnalyticsClient(mock_settings)
    metrics = client._fetch_audience_metrics(
        datetime(2024, 1, 1),
        datetime(2024, 1, 31),
    )
    
    assert metrics.total_users == 5000
    assert metrics.new_users == 2000
    assert metrics.sessions == 10000


@patch("src.google_analytics.client.BetaAnalyticsDataClient")
@patch("src.google_analytics.client.service_account.Credentials.from_service_account_file")
def test_fetch_engagement_metrics(mock_creds, mock_client_class, mock_settings, mock_credentials_file):
    """Test fetching engagement metrics."""
    mock_settings.ga_credentials_file = mock_credentials_file
    
    # Mock API response
    mock_response = Mock()
    mock_row = Mock()
    mock_row.metric_values = [
        Mock(value="120000"),  # total engagement duration
        Mock(value="7000"),    # engaged_sessions
        Mock(value="10000"),   # total sessions
    ]
    mock_response.rows = [mock_row]
    
    mock_client = Mock()
    mock_client.run_report.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    client = GoogleAnalyticsClient(mock_settings)
    metrics = client._fetch_engagement_metrics(
        datetime(2024, 1, 1),
        datetime(2024, 1, 31),
    )
    
    assert metrics.engaged_sessions == 7000
    assert metrics.engagement_rate == 70.0
    assert metrics.average_engagement_time == 12.0  # 120000 / 10000


@patch("src.google_analytics.client.BetaAnalyticsDataClient")
@patch("src.google_analytics.client.service_account.Credentials.from_service_account_file")
def test_test_connection_success(mock_creds, mock_client_class, mock_settings, mock_credentials_file):
    """Test successful connection test."""
    mock_settings.ga_credentials_file = mock_credentials_file
    
    mock_client = Mock()
    mock_client.run_report.return_value = Mock()
    mock_client_class.return_value = mock_client
    
    client = GoogleAnalyticsClient(mock_settings)
    assert client.test_connection() is True


@patch("src.google_analytics.client.BetaAnalyticsDataClient")
@patch("src.google_analytics.client.service_account.Credentials.from_service_account_file")
def test_test_connection_failure(mock_creds, mock_client_class, mock_settings, mock_credentials_file):
    """Test failed connection test."""
    mock_settings.ga_credentials_file = mock_credentials_file
    
    mock_client = Mock()
    mock_client.run_report.side_effect = Exception("API Error")
    mock_client_class.return_value = mock_client
    
    client = GoogleAnalyticsClient(mock_settings)
    assert client.test_connection() is False


@patch("src.google_analytics.client.BetaAnalyticsDataClient")
@patch("src.google_analytics.client.service_account.Credentials.from_service_account_file")
def test_context_manager(mock_creds, mock_client_class, mock_settings, mock_credentials_file):
    """Test context manager usage."""
    mock_settings.ga_credentials_file = mock_credentials_file
    mock_client_class.return_value = Mock()
    
    with GoogleAnalyticsClient(mock_settings) as client:
        assert client is not None
        assert client.property_id == "123456789"
