"""Analytics data processing and analysis."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from src.vercel.models import AnalyticsData


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

    # Raw data reference
    raw_analytics: Optional[AnalyticsData] = None


class AnalyticsAnalyzer:
    """Analyzer for processing and comparing analytics data."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        logger.info("Analytics analyzer initialized")

    def analyze(
        self,
        current_data: AnalyticsData,
        previous_data: Optional[AnalyticsData] = None,
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
        total_views = self._compare_metric(
            current_data.total_views,
            previous_data.total_views if previous_data else None,
            "Total Views",
        )

        unique_visitors = self._compare_metric(
            current_data.unique_visitors,
            previous_data.unique_visitors if previous_data else None,
            "Unique Visitors",
        )

        avg_session_duration = None
        if current_data.avg_session_duration is not None:
            avg_session_duration = self._compare_metric(
                current_data.avg_session_duration,
                (
                    previous_data.avg_session_duration
                    if previous_data and previous_data.avg_session_duration
                    else None
                ),
                "Avg Session Duration",
            )

        bounce_rate = None
        if current_data.bounce_rate is not None:
            bounce_rate = self._compare_metric(
                current_data.bounce_rate,
                (
                    previous_data.bounce_rate
                    if previous_data and previous_data.bounce_rate
                    else None
                ),
                "Bounce Rate",
            )

        # Process top pages
        top_pages = [
            {
                "path": page.path,
                "views": page.views,
                "unique_visitors": page.unique_visitors,
            }
            for page in current_data.top_pages[:5]
        ]

        # Process traffic sources
        top_sources = [
            {
                "source": source.source,
                "visitors": source.visitors,
                "percentage": source.percentage,
            }
            for source in current_data.traffic_sources[:5]
        ]

        # Process device breakdown
        device_breakdown = [
            {
                "device": device.device_type,
                "count": device.count,
                "percentage": device.percentage,
            }
            for device in current_data.device_stats
        ]

        # Process geographic breakdown
        geographic_breakdown = [
            {
                "country": geo.country,
                "visitors": geo.visitors,
                "percentage": geo.percentage,
            }
            for geo in current_data.geographic_data[:5]
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
        current_data: AnalyticsData,
        previous_data: Optional[AnalyticsData],
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

        # Top page insight
        if current_data.top_pages:
            top_page = current_data.top_pages[0]
            insights.append(
                f"Most popular page: '{top_page.path}' "
                f"with {top_page.views} views"
            )

        # Traffic source insight
        if current_data.traffic_sources:
            top_source = current_data.traffic_sources[0]
            insights.append(
                f"Primary traffic source: {top_source.source} "
                f"({top_source.percentage:.1f}% of traffic)"
            )

        # Device insight
        if current_data.device_stats:
            primary_device = current_data.device_stats[0]
            insights.append(
                f"Most visitors use {primary_device.device_type} "
                f"({primary_device.percentage:.1f}%)"
            )

        # Geographic insight
        if current_data.geographic_data:
            top_country = current_data.geographic_data[0]
            insights.append(
                f"Top geographic region: {top_country.country} "
                f"({top_country.percentage:.1f}% of visitors)"
            )

        return insights

    def _generate_recommendations(
        self,
        current_data: AnalyticsData,
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

        # Content recommendations
        if current_data.top_pages and len(current_data.top_pages) > 0:
            recommendations.append(
                "Focus content creation on topics similar to your top-performing pages"
            )

        # Traffic source recommendations
        if current_data.traffic_sources:
            direct_traffic = sum(
                s.visitors
                for s in current_data.traffic_sources
                if "direct" in s.source.lower()
            )
            if direct_traffic > current_data.unique_visitors * 0.5:
                recommendations.append(
                    "Consider diversifying traffic sources through SEO and social media"
                )

        return recommendations
