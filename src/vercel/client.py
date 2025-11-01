"""Vercel API client for fetching web analytics data."""

from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx
from loguru import logger

from src.config import Settings
from src.utils.retry import retry_on_api_error
from src.vercel.models import (
    AnalyticsData,
    DeviceStats,
    GeographicData,
    PageView,
    TrafficSource,
)


class VercelAPIError(Exception):
    """Custom exception for Vercel API errors."""

    pass


class VercelClient:
    """Client for interacting with Vercel Web Analytics API."""

    BASE_URL = "https://lemolegal-web.vercel.app"
    ANALYTICS_ENDPOINT = "/_vercel/insights/"

    def __init__(self, settings: Settings) -> None:
        """
        Initialize Vercel API client.

        Args:
            settings: Application settings containing API credentials
        """
        self.settings = settings
        self.api_token = settings.vercel_api_token
        self.team_id = settings.vercel_team_id
        self.project_id = settings.vercel_project_id
        self.target_website = settings.target_website

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        logger.info(f"Vercel client initialized for website: {self.target_website}")

    def __enter__(self) -> "VercelClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close HTTP client."""
        self.client.close()

    @retry_on_api_error
    def fetch_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AnalyticsData:
        """
        Fetch analytics data for the specified time period.

        Args:
            start_date: Start date for analytics (defaults to 30 days ago)
            end_date: End date for analytics (defaults to now)

        Returns:
            AnalyticsData object containing all analytics metrics

        Raises:
            VercelAPIError: If API request fails
        """
        # Default to last 30 days if not specified
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        logger.info(
            f"Fetching analytics from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Build query parameters
            params = self._build_query_params(start_date, end_date)

            # Fetch analytics data
            # Note: This is a placeholder - actual Vercel API endpoints may differ
            # You'll need to adjust based on Vercel's actual API documentation
            response = self.client.get(
                self.ANALYTICS_ENDPOINT,
                params=params,
            )

            response.raise_for_status()
            data = response.json()

            # Parse response into structured data
            analytics = self._parse_analytics_response(data, start_date, end_date)

            logger.info(
                f"Successfully fetched analytics: "
                f"{analytics.total_views} views, "
                f"{analytics.unique_visitors} unique visitors"
            )

            return analytics

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching analytics: {e.response.status_code}")
            raise VercelAPIError(
                f"Failed to fetch analytics: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error fetching analytics: {e}")
            raise VercelAPIError(f"Failed to connect to Vercel API: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error fetching analytics: {e}")
            raise VercelAPIError(f"Unexpected error: {e}") from e

    def _build_query_params(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, str]:
        """Build query parameters for API request."""
        params = {
            "from": int(start_date.timestamp() * 1000),  # Convert to milliseconds
            "to": int(end_date.timestamp() * 1000),
        }

        if self.team_id:
            params["teamId"] = self.team_id

        if self.project_id:
            params["projectId"] = self.project_id

        return params

    def _parse_analytics_response(
        self,
        data: Dict,
        start_date: datetime,
        end_date: datetime,
    ) -> AnalyticsData:
        """
        Parse API response into AnalyticsData model.

        Note: This is a placeholder implementation. The actual structure
        depends on Vercel's API response format.
        """
        # Extract overall metrics
        total_views = data.get("pageviews", 0)
        unique_visitors = data.get("visitors", 0)
        avg_session_duration = data.get("avgSessionDuration")
        bounce_rate = data.get("bounceRate")

        # Parse top pages
        top_pages = []
        for page_data in data.get("pages", [])[:10]:  # Top 10 pages
            top_pages.append(
                PageView(
                    path=page_data.get("path", "/"),
                    views=page_data.get("views", 0),
                    unique_visitors=page_data.get("visitors", 0),
                )
            )

        # Parse traffic sources
        traffic_sources = []
        total_source_visitors = sum(
            s.get("visitors", 0) for s in data.get("sources", [])
        )
        for source_data in data.get("sources", [])[:10]:  # Top 10 sources
            visitors = source_data.get("visitors", 0)
            percentage = (
                (visitors / total_source_visitors * 100) if total_source_visitors else 0
            )
            traffic_sources.append(
                TrafficSource(
                    source=source_data.get("source", "Unknown"),
                    visitors=visitors,
                    percentage=round(percentage, 2),
                )
            )

        # Parse device stats
        device_stats = []
        total_device_visitors = sum(
            d.get("count", 0) for d in data.get("devices", [])
        )
        for device_data in data.get("devices", []):
            count = device_data.get("count", 0)
            percentage = (
                (count / total_device_visitors * 100) if total_device_visitors else 0
            )
            device_stats.append(
                DeviceStats(
                    device_type=device_data.get("type", "Unknown"),
                    count=count,
                    percentage=round(percentage, 2),
                )
            )

        # Parse geographic data
        geographic_data = []
        total_geo_visitors = sum(g.get("visitors", 0) for g in data.get("countries", []))
        for geo_data in data.get("countries", [])[:10]:  # Top 10 countries
            visitors = geo_data.get("visitors", 0)
            percentage = (visitors / total_geo_visitors * 100) if total_geo_visitors else 0
            geographic_data.append(
                GeographicData(
                    country=geo_data.get("country", "Unknown"),
                    visitors=visitors,
                    percentage=round(percentage, 2),
                )
            )

        return AnalyticsData(
            start_date=start_date,
            end_date=end_date,
            total_views=total_views,
            unique_visitors=unique_visitors,
            avg_session_duration=avg_session_duration,
            bounce_rate=bounce_rate,
            top_pages=top_pages,
            traffic_sources=traffic_sources,
            device_stats=device_stats,
            geographic_data=geographic_data,
            raw_data=data,
        )

    def test_connection(self) -> bool:
        """
        Test the connection to Vercel API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple API call to verify credentials
            response = self.client.get("/v9/projects")
            response.raise_for_status()
            logger.info("Vercel API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Vercel API connection test failed: {e}")
            return False
