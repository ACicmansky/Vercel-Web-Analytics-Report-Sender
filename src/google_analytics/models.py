"""Data models for Google Analytics 4."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AudienceMetrics(BaseModel):
    """Model for audience overview metrics."""

    total_users: int = Field(..., description="Total number of users")
    new_users: int = Field(..., description="Number of new users")
    sessions: int = Field(..., description="Total number of sessions")


class EngagementMetrics(BaseModel):
    """Model for user engagement metrics."""

    average_engagement_time: float = Field(
        ...,
        description="Average engagement time per session in seconds",
    )
    engaged_sessions: int = Field(
        ...,
        description="Number of engaged sessions (>10s, conversion, or 2+ pageviews)",
    )
    engagement_rate: float = Field(
        ...,
        description="Percentage of engaged sessions",
        ge=0.0,
        le=100.0,
    )


class AcquisitionSource(BaseModel):
    """Model for traffic acquisition source/medium."""

    source: str = Field(..., description="Traffic source (e.g., google, direct)")
    medium: str = Field(..., description="Traffic medium (e.g., organic, cpc)")
    users: int = Field(..., description="Number of users from this source/medium")
    percentage: float = Field(
        ...,
        description="Percentage of total users",
        ge=0.0,
        le=100.0,
    )


class ConversionMetrics(BaseModel):
    """Model for conversion events."""

    form_submits: int = Field(
        default=0,
        description="Number of contact form submissions",
    )
    email_clicks: int = Field(
        default=0,
        description="Number of email link clicks",
    )
    phone_clicks: int = Field(
        default=0,
        description="Number of phone number clicks",
    )


class GeographicData(BaseModel):
    """Model for geographic distribution."""

    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    users: int = Field(..., description="Number of users from this location")
    percentage: float = Field(
        ...,
        description="Percentage of total users",
        ge=0.0,
        le=100.0,
    )


class GAAnalyticsData(BaseModel):
    """Complete Google Analytics data model."""

    # Time period
    start_date: datetime = Field(..., description="Start date of the period")
    end_date: datetime = Field(..., description="End date of the period")

    # Core metrics
    audience: AudienceMetrics = Field(..., description="Audience overview metrics")
    engagement: EngagementMetrics = Field(..., description="User engagement metrics")
    conversions: ConversionMetrics = Field(
        default_factory=ConversionMetrics,
        description="Conversion event metrics",
    )

    # Detailed breakdowns
    acquisition: List[AcquisitionSource] = Field(
        default_factory=list,
        description="Traffic acquisition sources (top 5)",
    )
    geographic: List[GeographicData] = Field(
        default_factory=list,
        description="Geographic distribution (top 10 cities)",
    )

    # Raw data for additional processing
    raw_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw API response data",
    )

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for reporting."""
        return {
            "period": f"{self.start_date.date()} to {self.end_date.date()}",
            "total_users": self.audience.total_users,
            "new_users": self.audience.new_users,
            "sessions": self.audience.sessions,
            "engagement_rate": f"{self.engagement.engagement_rate:.1f}%",
            "avg_engagement_time": f"{self.engagement.average_engagement_time:.0f}s",
            "top_source": (
                f"{self.acquisition[0].source}/{self.acquisition[0].medium}"
                if self.acquisition
                else "N/A"
            ),
            "total_conversions": (
                self.conversions.form_submits
                + self.conversions.email_clicks
                + self.conversions.phone_clicks
            ),
            "top_city": (
                f"{self.geographic[0].city}, {self.geographic[0].country}"
                if self.geographic
                else "N/A"
            ),
        }

    @property
    def total_conversions(self) -> int:
        """Calculate total conversions across all types."""
        return (
            self.conversions.form_submits
            + self.conversions.email_clicks
            + self.conversions.phone_clicks
        )

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate as percentage of sessions."""
        if self.audience.sessions == 0:
            return 0.0
        return (self.total_conversions / self.audience.sessions) * 100
