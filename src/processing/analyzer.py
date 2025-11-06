"""Analytics data processing and analysis."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from src.google_analytics.models import GAAnalyticsData


class MetricChange(BaseModel):
    """Model for metric change comparison."""

    current: float = Field(..., description="Current period value")
    previous: Optional[float] = Field(None, description="Previous period value")
    change: Optional[float] = Field(None, description="Absolute change")
    change_percent: Optional[float] = Field(None, description="Percentage change")
    trend: str = Field(default="stable", description="Trend direction (up/down/stable)")

    def calculate_trend(self) -> None:
        """Calculate trend based on change percentage."""
        if self.change_percent is None:
            self.trend = "stable"
        elif self.change_percent > 5:
            self.trend = "up"
        elif self.change_percent < -5:
            self.trend = "down"
        else:
            self.trend = "stable"


class AnalyticsSummary(BaseModel):
    """Processed analytics summary with insights."""

    # Period information
    period_start: datetime
    period_end: datetime
    period_days: int

    # Key metrics with trends
    total_views: MetricChange
    unique_visitors: MetricChange
    avg_session_duration: Optional[MetricChange] = None
    bounce_rate: Optional[MetricChange] = None

    # Top performers
    top_pages: List[Dict[str, Any]] = Field(default_factory=list)
    top_sources: List[Dict[str, Any]] = Field(default_factory=list)
    device_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    geographic_breakdown: List[Dict[str, Any]] = Field(default_factory=list)

    # Insights
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    # Conversion metrics
    total_conversions: Optional[MetricChange] = None
    conversion_rate: Optional[MetricChange] = None
    engagement_rate: Optional[MetricChange] = None

    # Raw data reference
    raw_analytics: Optional[GAAnalyticsData] = None


class AnalyticsAnalyzer:
    """Analyzer for processing and comparing analytics data."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        logger.info("Analytics analyzer initialized")

    def analyze(
        self,
        current_data: GAAnalyticsData,
        previous_data: Optional[GAAnalyticsData] = None,
    ) -> AnalyticsSummary:
        """
        Analyze analytics data and generate summary with insights.

        Args:
            current_data: Current period analytics data
            previous_data: Previous period analytics data for comparison

        Returns:
            AnalyticsSummary with processed metrics and insights
        """
        logger.info("Starting analytics analysis")

        # Calculate period duration
        period_days = (current_data.end_date - current_data.start_date).days

        # Process metrics with comparisons
        # Map GA sessions to total_views for compatibility
        total_views = self._compare_metric(
            current_data.audience.sessions,
            previous_data.audience.sessions if previous_data else None,
            "Sessions",
        )

        # Map GA total_users to unique_visitors
        unique_visitors = self._compare_metric(
            current_data.audience.total_users,
            previous_data.audience.total_users if previous_data else None,
            "Total Users",
        )

        # Map GA average_engagement_time to avg_session_duration
        avg_session_duration = self._compare_metric(
            current_data.engagement.average_engagement_time,
            (
                previous_data.engagement.average_engagement_time
                if previous_data
                else None
            ),
            "Avg Engagement Time",
        )

        # Calculate bounce rate from engagement rate (inverse)
        bounce_rate = None
        if current_data.engagement.engagement_rate is not None:
            current_bounce = 100 - current_data.engagement.engagement_rate
            previous_bounce = (
                100 - previous_data.engagement.engagement_rate
                if previous_data
                else None
            )
            bounce_rate = self._compare_metric(
                current_bounce,
                previous_bounce,
                "Bounce Rate",
            )

        # Process conversion metrics
        total_conversions = self._compare_metric(
            current_data.total_conversions,
            previous_data.total_conversions if previous_data else None,
            "Total Conversions",
        )

        conversion_rate = self._compare_metric(
            current_data.conversion_rate,
            previous_data.conversion_rate if previous_data else None,
            "Conversion Rate",
        )

        engagement_rate = self._compare_metric(
            current_data.engagement.engagement_rate,
            previous_data.engagement.engagement_rate if previous_data else None,
            "Engagement Rate",
        )

        # Top pages not available in GA4 basic metrics
        # Could be added later with page_path dimension
        top_pages = []

        # Process traffic sources (acquisition)
        top_sources = [
            {
                "source": f"{source.source}/{source.medium}",
                "visitors": source.users,
                "percentage": source.percentage,
            }
            for source in current_data.acquisition[:5]
        ]

        # Device breakdown not included in basic GA4 metrics
        # Could be added later if needed
        device_breakdown = []

        # Process geographic breakdown (cities)
        geographic_breakdown = [
            {
                "location": f"{geo.city}, {geo.country}",
                "visitors": geo.users,
                "percentage": geo.percentage,
            }
            for geo in current_data.geographic[:10]
        ]

        # Generate insights
        insights = self._generate_insights(
            current_data,
            previous_data,
            total_views,
            unique_visitors,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_data,
            total_views,
            bounce_rate,
        )

        summary = AnalyticsSummary(
            period_start=current_data.start_date,
            period_end=current_data.end_date,
            period_days=period_days,
            total_views=total_views,
            unique_visitors=unique_visitors,
            avg_session_duration=avg_session_duration,
            bounce_rate=bounce_rate,
            total_conversions=total_conversions,
            conversion_rate=conversion_rate,
            engagement_rate=engagement_rate,
            top_pages=top_pages,
            top_sources=top_sources,
            device_breakdown=device_breakdown,
            geographic_breakdown=geographic_breakdown,
            key_insights=insights,
            recommendations=recommendations,
            raw_analytics=current_data,
        )

        logger.info("Analytics analysis completed")
        return summary

    def _compare_metric(
        self,
        current: float,
        previous: Optional[float],
        metric_name: str,
    ) -> MetricChange:
        """Compare current and previous metric values."""
        change = None
        change_percent = None

        if previous is not None and previous > 0:
            change = current - previous
            change_percent = (change / previous) * 100

        metric_change = MetricChange(
            current=current,
            previous=previous,
            change=change,
            change_percent=round(change_percent, 2) if change_percent else None,
        )
        metric_change.calculate_trend()

        logger.debug(
            f"{metric_name}: {current} "
            f"(trend: {metric_change.trend}, "
            f"change: {metric_change.change_percent}%)"
        )

        return metric_change

    def _generate_insights(
        self,
        current_data: GAAnalyticsData,
        previous_data: Optional[GAAnalyticsData],
        views_change: MetricChange,
        visitors_change: MetricChange,
    ) -> List[str]:
        """Generate key insights from analytics data."""
        insights = []

        # Traffic trend insights
        if views_change.trend == "up":
            insights.append(
                f"Traffic increased by {views_change.change_percent:.1f}% "
                f"compared to the previous period"
            )
        elif views_change.trend == "down":
            insights.append(
                f"Traffic decreased by {abs(views_change.change_percent):.1f}% "
                f"compared to the previous period"
            )

        # Engagement insight
        if current_data.engagement.engagement_rate > 70:
            insights.append(
                f"Strong engagement rate of {current_data.engagement.engagement_rate:.1f}% "
                "indicates visitors are finding content valuable"
            )
        elif current_data.engagement.engagement_rate < 40:
            insights.append(
                f"Low engagement rate of {current_data.engagement.engagement_rate:.1f}% "
                "suggests content may need improvement"
            )

        # Conversion insight
        if current_data.total_conversions > 0:
            insights.append(
                f"Total conversions: {current_data.total_conversions} "
                f"(rate: {current_data.conversion_rate:.2f}%)"
            )

        # Traffic source insight
        if current_data.acquisition:
            top_source = current_data.acquisition[0]
            insights.append(
                f"Primary traffic source: {top_source.source}/{top_source.medium} "
                f"({top_source.percentage:.1f}% of users)"
            )

        # Geographic insight
        if current_data.geographic:
            top_location = current_data.geographic[0]
            insights.append(
                f"Top location: {top_location.city}, {top_location.country} "
                f"({top_location.percentage:.1f}% of users)"
            )

        return insights

    def _generate_recommendations(
        self,
        current_data: GAAnalyticsData,
        views_change: MetricChange,
        bounce_rate: Optional[MetricChange],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Traffic recommendations
        if views_change.trend == "down":
            recommendations.append(
                "Consider reviewing recent content changes or SEO optimization"
            )

        # Bounce rate recommendations
        if bounce_rate and bounce_rate.current > 60:
            recommendations.append(
                "High bounce rate detected - consider improving page load times "
                "and content relevance"
            )

        # Engagement recommendations
        if current_data.engagement.engagement_rate < 50:
            recommendations.append(
                "Low engagement rate - consider improving content quality, "
                "page load speed, and user experience"
            )

        # Conversion recommendations
        if current_data.conversion_rate < 1.0 and current_data.audience.sessions > 100:
            recommendations.append(
                "Low conversion rate - review call-to-action placement "
                "and form accessibility"
            )

        # Traffic source recommendations
        if current_data.acquisition:
            direct_traffic = sum(
                s.users
                for s in current_data.acquisition
                if "direct" in s.source.lower()
            )
            if direct_traffic > current_data.audience.total_users * 0.5:
                recommendations.append(
                    "High direct traffic - consider diversifying sources through SEO, "
                    "social media, and content marketing"
                )

        return recommendations
