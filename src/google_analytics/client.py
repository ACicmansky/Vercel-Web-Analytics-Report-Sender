"""Google Analytics 4 API client for fetching web analytics data."""

import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
from loguru import logger

from src.config import Settings
from src.google_analytics.models import (
    AcquisitionSource,
    AudienceMetrics,
    ConversionMetrics,
    EngagementMetrics,
    GAAnalyticsData,
    GeographicData,
)
from src.utils.retry import retry_on_api_error


class GoogleAnalyticsAPIError(Exception):
    """Custom exception for Google Analytics API errors."""

    pass


class GoogleAnalyticsClient:
    """Client for interacting with Google Analytics 4 Data API."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize Google Analytics API client.

        Args:
            settings: Application settings containing GA credentials
        """
        self.settings = settings
        self.property_id = settings.ga_property_id

        # Initialize API client with credentials
        self.client = self._initialize_client()

        logger.info(f"Google Analytics client initialized for property: {self.property_id}")

    def _initialize_client(self) -> BetaAnalyticsDataClient:
        """
        Initialize the Google Analytics Data API client with credentials.

        Returns:
            Initialized BetaAnalyticsDataClient

        Raises:
            GoogleAnalyticsAPIError: If credentials are invalid or missing
        """
        try:
            credentials = None

            # Try loading from file first
            if self.settings.ga_credentials_file:
                credentials_path = Path(self.settings.ga_credentials_file)
                if not credentials_path.exists():
                    raise GoogleAnalyticsAPIError(
                        f"Credentials file not found: {self.settings.ga_credentials_file}"
                    )
                credentials = service_account.Credentials.from_service_account_file(
                    str(credentials_path),
                    scopes=["https://www.googleapis.com/auth/analytics.readonly"],
                )
                logger.info(f"Loaded credentials from file: {credentials_path}")

            # Try loading from JSON string (environment variable)
            elif self.settings.GA_CREDENTIALS_JSON_BASE64:
                credentials_info = json.loads(base64.b64decode(self.settings.GA_CREDENTIALS_JSON_BASE64))
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=["https://www.googleapis.com/auth/analytics.readonly"],
                )
                logger.info("Loaded credentials from environment variable")

            else:
                raise GoogleAnalyticsAPIError(
                    "No Google Analytics credentials provided. "
                    "Set GA_CREDENTIALS_FILE or GA_CREDENTIALS_JSON_BASE64"
                )

            return BetaAnalyticsDataClient(credentials=credentials)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GA_CREDENTIALS_JSON_BASE64: {e}")
            raise GoogleAnalyticsAPIError(
                f"Invalid credentials JSON format: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize Google Analytics client: {e}")
            raise GoogleAnalyticsAPIError(
                f"Failed to initialize client: {e}"
            ) from e

    def __enter__(self) -> "GoogleAnalyticsClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        # BetaAnalyticsDataClient doesn't require explicit cleanup
        pass

    @retry_on_api_error
    def fetch_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> GAAnalyticsData:
        """
        Fetch analytics data for the specified time period.

        Args:
            start_date: Start date for analytics
            end_date: End date for analytics

        Returns:
            GAAnalyticsData object containing all analytics metrics

        Raises:
            GoogleAnalyticsAPIError: If API request fails
        """
        logger.info(
            f"Fetching analytics from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Fetch all metrics
            audience = self._fetch_audience_metrics(start_date, end_date)
            engagement = self._fetch_engagement_metrics(start_date, end_date)
            acquisition = self._fetch_acquisition_data(start_date, end_date)
            conversions = self._fetch_conversion_metrics(start_date, end_date)
            geographic = self._fetch_geographic_data(start_date, end_date)

            analytics = GAAnalyticsData(
                start_date=start_date,
                end_date=end_date,
                audience=audience,
                engagement=engagement,
                acquisition=acquisition,
                conversions=conversions,
                geographic=geographic,
            )

            logger.info(
                f"Successfully fetched analytics: "
                f"{analytics.audience.total_users} users, "
                f"{analytics.audience.sessions} sessions, "
                f"{analytics.total_conversions} conversions"
            )

            return analytics

        except Exception as e:
            logger.error(f"Failed to fetch analytics: {e}")
            raise GoogleAnalyticsAPIError(f"Failed to fetch analytics: {e}") from e

    def _fetch_audience_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> AudienceMetrics:
        """Fetch audience overview metrics."""
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                ],
                metrics=[
                    Metric(name="totalUsers"),
                    Metric(name="newUsers"),
                    Metric(name="sessions"),
                ],
            )

            response = self.client.run_report(request)

            if not response.rows:
                logger.warning("No audience data returned from API")
                return AudienceMetrics(
                    total_users=0,
                    new_users=0,
                    sessions=0,
                )

            row = response.rows[0]
            return AudienceMetrics(
                total_users=int(row.metric_values[0].value),
                new_users=int(row.metric_values[1].value),
                sessions=int(row.metric_values[2].value),
            )

        except Exception as e:
            logger.error(f"Failed to fetch audience metrics: {e}")
            raise GoogleAnalyticsAPIError(
                f"Failed to fetch audience metrics: {e}"
            ) from e

    def _fetch_engagement_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> EngagementMetrics:
        """Fetch user engagement metrics."""
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                ],
                metrics=[
                    Metric(name="userEngagementDuration"),
                    Metric(name="engagedSessions"),
                    Metric(name="sessions"),
                ],
            )

            response = self.client.run_report(request)

            if not response.rows:
                logger.warning("No engagement data returned from API")
                return EngagementMetrics(
                    average_engagement_time=0.0,
                    engaged_sessions=0,
                    engagement_rate=0.0,
                )

            row = response.rows[0]
            total_engagement_duration = float(row.metric_values[0].value)
            engaged_sessions = int(row.metric_values[1].value)
            total_sessions = int(row.metric_values[2].value)

            # Calculate average engagement time per session
            avg_engagement_time = (
                total_engagement_duration / total_sessions if total_sessions > 0 else 0.0
            )

            # Calculate engagement rate
            engagement_rate = (
                (engaged_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
            )

            return EngagementMetrics(
                average_engagement_time=avg_engagement_time,
                engaged_sessions=engaged_sessions,
                engagement_rate=engagement_rate,
            )

        except Exception as e:
            logger.error(f"Failed to fetch engagement metrics: {e}")
            raise GoogleAnalyticsAPIError(
                f"Failed to fetch engagement metrics: {e}"
            ) from e

    def _fetch_acquisition_data(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[AcquisitionSource]:
        """Fetch traffic acquisition sources (top 5)."""
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                ],
                dimensions=[
                    Dimension(name="sessionSource"),
                    Dimension(name="sessionMedium"),
                ],
                metrics=[
                    Metric(name="totalUsers"),
                ],
                order_bys=[{"metric": {"metric_name": "totalUsers"}, "desc": True}],
                limit=5,  # Top 5 sources
            )

            response = self.client.run_report(request)

            if not response.rows:
                logger.warning("No acquisition data returned from API")
                return []

            # Calculate total users for percentage
            total_users = sum(int(row.metric_values[0].value) for row in response.rows)

            sources = []
            for row in response.rows:
                source = row.dimension_values[0].value
                medium = row.dimension_values[1].value
                users = int(row.metric_values[0].value)
                percentage = (users / total_users * 100) if total_users > 0 else 0.0

                sources.append(
                    AcquisitionSource(
                        source=source,
                        medium=medium,
                        users=users,
                        percentage=round(percentage, 2),
                    )
                )

            return sources

        except Exception as e:
            logger.error(f"Failed to fetch acquisition data: {e}")
            raise GoogleAnalyticsAPIError(
                f"Failed to fetch acquisition data: {e}"
            ) from e

    def _fetch_conversion_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> ConversionMetrics:
        """Fetch conversion event metrics."""
        try:
            # Define custom event names
            event_names = {
                "form_submit": "form_submits",
                "email_click": "email_clicks",
                "phone_click": "phone_clicks",
            }

            conversions = ConversionMetrics()

            for event_name, attr_name in event_names.items():
                try:
                    request = RunReportRequest(
                        property=f"properties/{self.property_id}",
                        date_ranges=[
                            DateRange(
                                start_date=start_date.strftime("%Y-%m-%d"),
                                end_date=end_date.strftime("%Y-%m-%d"),
                            )
                        ],
                        dimensions=[Dimension(name="eventName")],
                        metrics=[Metric(name="eventCount")],
                        dimension_filter={
                            "filter": {
                                "field_name": "eventName",
                                "string_filter": {
                                    "match_type": "EXACT",
                                    "value": event_name,
                                },
                            }
                        },
                    )

                    response = self.client.run_report(request)

                    if response.rows:
                        count = int(response.rows[0].metric_values[0].value)
                        setattr(conversions, attr_name, count)
                        logger.debug(f"Event '{event_name}': {count}")
                    else:
                        logger.debug(f"No data for event '{event_name}'")

                except Exception as event_error:
                    # Don't fail if a specific event is not configured
                    logger.warning(
                        f"Could not fetch event '{event_name}': {event_error}. "
                        "Event may not be configured in GA4."
                    )
                    setattr(conversions, attr_name, 0)

            return conversions

        except Exception as e:
            logger.error(f"Failed to fetch conversion metrics: {e}")
            # Return empty conversions rather than failing
            return ConversionMetrics()

    def _fetch_geographic_data(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[GeographicData]:
        """Fetch geographic distribution (top 10 cities)."""
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                ],
                dimensions=[
                    Dimension(name="city"),
                    Dimension(name="country"),
                ],
                metrics=[
                    Metric(name="totalUsers"),
                ],
                order_bys=[{"metric": {"metric_name": "totalUsers"}, "desc": True}],
                limit=10,  # Top 10 cities
            )

            response = self.client.run_report(request)

            if not response.rows:
                logger.warning("No geographic data returned from API")
                return []

            # Calculate total users for percentage
            total_users = sum(int(row.metric_values[0].value) for row in response.rows)

            locations = []
            for row in response.rows:
                city = row.dimension_values[0].value
                country = row.dimension_values[1].value
                users = int(row.metric_values[0].value)
                percentage = (users / total_users * 100) if total_users > 0 else 0.0

                # Skip "(not set)" entries
                if city != "(not set)" and country != "(not set)":
                    locations.append(
                        GeographicData(
                            city=city,
                            country=country,
                            users=users,
                            percentage=round(percentage, 2),
                        )
                    )

            return locations

        except Exception as e:
            logger.error(f"Failed to fetch geographic data: {e}")
            raise GoogleAnalyticsAPIError(
                f"Failed to fetch geographic data: {e}"
            ) from e

    def test_connection(self) -> bool:
        """
        Test the connection to Google Analytics API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple API call to verify credentials and property access
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
                metrics=[Metric(name="totalUsers")],
            )

            response = self.client.run_report(request)
            logger.info("Google Analytics API connection test successful")
            return True

        except Exception as e:
            logger.error(f"Google Analytics API connection test failed: {e}")
            return False
