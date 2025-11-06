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
    # top_pages_text = "\n".join(
    #     f"  - {page['path']}: {page['views']} views, {page['unique_visitors']} unique visitors"
    #     for page in summary.top_pages[:5]
    # )

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
        f"  - {geo['location']}: {geo['visitors']} visitors ({geo['percentage']:.1f}%)"
        for geo in summary.geographic_breakdown[:5]
    )

    prompt = f"""Vytvor veľmi stručnú analytickú správu pre {website} (obdobie: {summary.period_start.strftime('%d.%m.')} - {summary.period_end.strftime('%d.%m.%Y')}).

DÁTA:
- Zobrazenia: {summary.total_views.current:,} {views_trend}
- Návštevníci: {summary.unique_visitors.current:,} {visitors_trend}
- Top zdroje: {', '.join(source['source'] for source in summary.top_sources[:3])}
- Top lokality: {', '.join(geo['location'] for geo in summary.geographic_breakdown[:3])}

KĽÚČOVÉ POZNATKY:
{chr(10).join(f'- {insight}' for insight in summary.key_insights[:3])}

ODPORÚČANIA:
{chr(10).join(f'- {rec}' for rec in summary.recommendations[:2])}

POŽIADAVKY:
- Cieľová skupina: zaneprázdnení právnici
- Bez úvodnej hlavičky - začni priamo zhrnutím (1-2 vety o celkovom stave)
- Potom sekcia "## Kľúčové zistenia" s 1-3 bodmi (každý max 1 veta)
- Potom sekcia "## Odporúčania" s 1-2 bodmi (každý max 1 veta)
- Celková dĺžka: max 150 slov
- Tón: profesionálny, priamy, bez zbytočných slov
- Bez tabuliek, bez opakovaní metrík z emailu
- Zameraj sa na to, čo je DÔLEŽITÉ pre rozhodovanie"""

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
    return """Si konzultant pre webovú analytiku špecializujúci sa na právnické kancelárie. 
Tvoje správy sú extrémne stručné, priame a zamerané na akčné poznatky. 
Píšeš pre zaneprázdnených právnikov, ktorí potrebujú vedieť len to najdôležitejšie. 
Žiadne zbytočné slová, žiadne opakované informácie, len kľúčové zistenia a konkrétne odporúčania."""
