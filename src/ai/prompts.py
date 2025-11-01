"""AI prompt templates for analytics summarization."""

from typing import Dict

from src.processing.analyzer import AnalyticsSummary


def create_summary_prompt(summary: AnalyticsSummary, website: str) -> str:
    """
    Create a prompt for AI to generate analytics summary.

    Args:
        summary: Processed analytics summary
        website: Website name

    Returns:
        Formatted prompt string
    """
    # Format metrics
    views_trend = _format_trend(summary.total_views)
    visitors_trend = _format_trend(summary.unique_visitors)

    # Format top pages
    top_pages_text = "\n".join(
        f"  - {page['path']}: {page['views']} views, {page['unique_visitors']} unique visitors"
        for page in summary.top_pages[:5]
    )

    # Format traffic sources
    sources_text = "\n".join(
        f"  - {source['source']}: {source['visitors']} visitors ({source['percentage']:.1f}%)"
        for source in summary.top_sources[:5]
    )

    # Format device breakdown
    devices_text = "\n".join(
        f"  - {device['device']}: {device['percentage']:.1f}%"
        for device in summary.device_breakdown
    )

    # Format geographic data
    geo_text = "\n".join(
        f"  - {geo['country']}: {geo['visitors']} visitors ({geo['percentage']:.1f}%)"
        for geo in summary.geographic_breakdown[:5]
    )

    prompt = f"""You are an expert web analytics consultant. Generate a professional, 
concise analytics report for {website} based on the following data.

REPORTING PERIOD:
{summary.period_start.strftime('%B %d, %Y')} to {summary.period_end.strftime('%B %d, %Y')} ({summary.period_days} days)

KEY METRICS:
- Total Page Views: {summary.total_views.current:,} {views_trend}
- Unique Visitors: {summary.unique_visitors.current:,} {visitors_trend}
{_format_optional_metric('Average Session Duration', summary.avg_session_duration)}
{_format_optional_metric('Bounce Rate', summary.bounce_rate, is_percentage=True)}

TOP PAGES:
{top_pages_text}

TRAFFIC SOURCES:
{sources_text}

DEVICE BREAKDOWN:
{devices_text}

GEOGRAPHIC DISTRIBUTION:
{geo_text}

KEY INSIGHTS:
{chr(10).join(f'- {insight}' for insight in summary.key_insights)}

RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in summary.recommendations)}

Please provide a professional summary that:
1. Highlights the most important metrics and trends
2. Explains what the data means in business terms
3. Identifies opportunities and areas of concern
4. Provides 2-3 actionable recommendations
5. Uses a professional but accessible tone
6. Keeps the summary concise (300-400 words)

Format the response in clear sections with headers."""

    return prompt


def _format_trend(metric_change) -> str:
    """Format metric trend for display."""
    if metric_change.change_percent is None:
        return ""

    direction = "↑" if metric_change.trend == "up" else "↓" if metric_change.trend == "down" else "→"
    sign = "+" if metric_change.change_percent > 0 else ""

    return f"({direction} {sign}{metric_change.change_percent:.1f}% vs previous period)"


def _format_optional_metric(
    name: str,
    metric_change,
    is_percentage: bool = False,
) -> str:
    """Format optional metric if available."""
    if metric_change is None:
        return ""

    value = metric_change.current
    if is_percentage:
        formatted_value = f"{value:.1f}%"
    elif name == "Average Session Duration":
        # Convert seconds to minutes:seconds
        minutes = int(value // 60)
        seconds = int(value % 60)
        formatted_value = f"{minutes}m {seconds}s"
    else:
        formatted_value = f"{value:,.0f}"

    trend = _format_trend(metric_change)
    return f"- {name}: {formatted_value} {trend}"


def create_system_prompt() -> str:
    """Create system prompt for AI model."""
    return """You are a professional web analytics consultant with expertise in 
interpreting website traffic data and providing actionable business insights. 
Your reports are clear, concise, and focused on helping website owners understand 
their audience and improve their online presence. You communicate complex data 
in an accessible way while maintaining professional standards."""
