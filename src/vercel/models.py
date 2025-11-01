"""Data models for Vercel analytics."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PageView(BaseModel):
    """Model for page view data."""

    path: str = Field(..., description="Page path/route")
    views: int = Field(..., description="Number of views")
    unique_visitors: int = Field(..., description="Number of unique visitors")


class TrafficSource(BaseModel):
    """Model for traffic source data."""

    source: str = Field(..., description="Traffic source (referrer)")
    visitors: int = Field(..., description="Number of visitors from this source")
    percentage: float = Field(..., description="Percentage of total traffic")


class DeviceStats(BaseModel):
    """Model for device statistics."""

    device_type: str = Field(..., description="Device type (desktop, mobile, tablet)")
    count: int = Field(..., description="Number of visitors")
    percentage: float = Field(..., description="Percentage of total visitors")


class GeographicData(BaseModel):
    """Model for geographic distribution."""

    country: str = Field(..., description="Country name or code")
    visitors: int = Field(..., description="Number of visitors")
    percentage: float = Field(..., description="Percentage of total visitors")


class AnalyticsData(BaseModel):
    """Complete analytics data model."""

    # Time period
    start_date: datetime = Field(..., description="Start date of the period")
    end_date: datetime = Field(..., description="End date of the period")

    # Overall metrics
    total_views: int = Field(..., description="Total page views")
    unique_visitors: int = Field(..., description="Total unique visitors")
    avg_session_duration: Optional[float] = Field(
        None,
        description="Average session duration in seconds",
    )
    bounce_rate: Optional[float] = Field(None, description="Bounce rate percentage")

    # Detailed breakdowns
    top_pages: List[PageView] = Field(
        default_factory=list,
        description="Top pages by views",
    )
    traffic_sources: List[TrafficSource] = Field(
        default_factory=list,
        description="Traffic sources",
    )
    device_stats: List[DeviceStats] = Field(
        default_factory=list,
        description="Device statistics",
    )
    geographic_data: List[GeographicData] = Field(
        default_factory=list,
        description="Geographic distribution",
    )

    # Raw data for additional processing
    raw_data: Optional[Dict] = Field(
        None,
        description="Raw API response data",
    )

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for reporting."""
        return {
            "period": f"{self.start_date.date()} to {self.end_date.date()}",
            "total_views": self.total_views,
            "unique_visitors": self.unique_visitors,
            "avg_session_duration": self.avg_session_duration,
            "bounce_rate": self.bounce_rate,
            "top_page": self.top_pages[0].path if self.top_pages else "N/A",
            "top_source": (
                self.traffic_sources[0].source if self.traffic_sources else "Direct"
            ),
            "primary_device": (
                self.device_stats[0].device_type if self.device_stats else "Unknown"
            ),
        }
