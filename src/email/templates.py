"""Email templates for analytics reports."""

import markdown
from datetime import date, datetime

from src.processing.analyzer import AnalyticsSummary


def create_html_email(
    summary: AnalyticsSummary,
    ai_summary: str,
    website: str,
) -> str:
    """
    Create HTML email template for analytics report.

    Args:
        summary: Processed analytics summary
        ai_summary: AI-generated summary text
        website: Website name

    Returns:
        HTML email content
    """
    # Format AI summary 
    ai_summary_html = markdown.markdown(ai_summary)

    # Format metrics with trend indicators
    views_trend = _format_trend_html(summary.total_views)
    visitors_trend = _format_trend_html(summary.unique_visitors)

    # Top pages table
    top_pages_rows = "\n".join(
        f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{page['path']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">{page['views']:,}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">{page['unique_visitors']:,}</td>
        </tr>
        """
        for page in summary.top_pages[:5]
    )

    # Traffic sources table
    sources_rows = "\n".join(
        f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{source['source']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">{source['visitors']:,}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">{source['percentage']:.1f}%</td>
        </tr>
        """
        for source in summary.top_sources[:5]
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytická správa - {website}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #374151; margin: 0; padding: 0; background-color: #f9fafb;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 600;">📊 Analytická správa</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{website}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">
                {summary.period_start.strftime('%d. %B %Y')} - {summary.period_end.strftime('%d. %B %Y')}
            </p>
        </div>

        <!-- Key Metrics -->
        <div style="padding: 30px 20px; background-color: #f9fafb;">
            <h2 style="margin: 0 0 20px 0; font-size: 20px; color: #1f2937;">📈 Kľúčové metriky</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 5px;">Celkový počet zobrazení</div>
                    <div style="font-size: 28px; font-weight: 600; color: #1f2937;">{summary.total_views.current:,}</div>
                    <div style="font-size: 12px; margin-top: 5px;">{views_trend}</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #764ba2;">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 5px;">Jedinečných návštevníkov</div>
                    <div style="font-size: 28px; font-weight: 600; color: #1f2937;">{summary.unique_visitors.current:,}</div>
                    <div style="font-size: 12px; margin-top: 5px;">{visitors_trend}</div>
                </div>
            </div>
        </div>

        <!-- AI Summary -->
        <div style="padding: 30px 20px; background-color: #ffffff;">
            <h2 style="margin: 0 0 15px 0; font-size: 20px; color: #1f2937;">🤖 AI prehľad</h2>
            <div style="background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; border-radius: 4px; font-size: 14px; line-height: 1.6;">
                {ai_summary_html}
            </div>
        </div>

        <!-- Top Pages -->
        <!--<div style="padding: 30px 20px; background-color: #f9fafb;">
            <h2 style="margin: 0 0 15px 0; font-size: 20px; color: #1f2937;">🏆 Najnavštevovanejšie stránky</h2>
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background-color: #f3f4f6;">
                        <th style="padding: 12px 8px; text-align: left; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase;">Stránka</th>
                        <th style="padding: 12px 8px; text-align: right; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase;">Zobrazenia</th>
                        <th style="padding: 12px 8px; text-align: right; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase;">Návštevníci</th>
                    </tr>
                </thead>
                <tbody>
                    {top_pages_rows}
                </tbody>
            </table>
        </div>-->

        <!-- Traffic Sources -->
        <div style="padding: 30px 20px; background-color: #ffffff;">
            <h2 style="margin: 0 0 15px 0; font-size: 20px; color: #1f2937;">🌐 Zdroje návštevnosti</h2>
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background-color: #f3f4f6;">
                        <th style="padding: 12px 8px; text-align: left; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase;">Zdroj</th>
                        <th style="padding: 12px 8px; text-align: right; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase;">Návštevníci</th>
                        <th style="padding: 12px 8px; text-align: right; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase;">Podiel</th>
                    </tr>
                </thead>
                <tbody>
                    {sources_rows}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div style="padding: 20px; background-color: #f9fafb; text-align: center; border-top: 1px solid #e5e7eb;">
            <p style="margin: 0; font-size: 12px; color: #6b7280;">
                Vygenerované {datetime.now().strftime('%d. %B %Y o %H:%M')}
            </p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #9ca3af;">
                Automatická analytická správa • Design by &copy; {date.today().year} <a href="mailto:andrej.cicmansky@gmail.com">Andrej Čičmanský</a>
            </p>
        </div>
    </div>
</body>
</html>
    """

    return html


def create_plain_text_email(
    summary: AnalyticsSummary,
    ai_summary: str,
    website: str,
) -> str:
    """
    Create plain text email for analytics report.

    Args:
        summary: Processed analytics summary
        ai_summary: AI-generated summary text
        website: Website name

    Returns:
        Plain text email content
    """
    views_trend = _format_trend_text(summary.total_views)
    visitors_trend = _format_trend_text(summary.unique_visitors)

    # # Top pages
    # top_pages_text = "\n".join(
    #     f"  {i+1}. {page['path']}\n     Views: {page['views']:,} | Visitors: {page['unique_visitors']:,}"
    #     for i, page in enumerate(summary.top_pages[:5])
    # )

    # Traffic sources
    sources_text = "\n".join(
        f"  {i+1}. {source['source']}\n     Visitors: {source['visitors']:,} ({source['percentage']:.1f}%)"
        for i, source in enumerate(summary.top_sources[:5])
    )

    text = f"""
═══════════════════════════════════════════════════════════
  📊 ANALYTICKÝ REPORT - {website.upper()}
═══════════════════════════════════════════════════════════

Obdobie: {summary.period_start.strftime('%d. %B %Y')} - {summary.period_end.strftime('%d. %B %Y')}
Trvanie: {summary.period_days} dní

───────────────────────────────────────────────────────────
📈 KĽÚČOVÉ METRIKY
───────────────────────────────────────────────────────────

Celkový počet zobrazení stránok: {summary.total_views.current:,}
{views_trend}

Jedinečných návštevníkov: {summary.unique_visitors.current:,}
{visitors_trend}

───────────────────────────────────────────────────────────
🤖 AI ZHRNUTIE
───────────────────────────────────────────────────────────

{ai_summary}

───────────────────────────────────────────────────────────
🌐 ZDROJE NÁVŠTEVNOSTI
───────────────────────────────────────────────────────────

{sources_text}

───────────────────────────────────────────────────────────

Vygenerované {datetime.now().strftime('%d. %B %Y o %H:%M')}
Automatický analytický report • Design by &copy; {date.today().year} <a href="mailto:andrej.cicmansky@gmail.com">Andrej Čičmanský</a>

═══════════════════════════════════════════════════════════
    """

    return text.strip()


def _format_trend_html(metric_change) -> str:
    """Format metric trend for HTML display."""
    if metric_change.change_percent is None:
        return '<span style="color: #6b7280;">No comparison data</span>'

    if metric_change.trend == "up":
        color = "#10b981"
        icon = "↑"
    elif metric_change.trend == "down":
        color = "#ef4444"
        icon = "↓"
    else:
        color = "#6b7280"
        icon = "→"

    sign = "+" if metric_change.change_percent > 0 else ""

    return f'<span style="color: {color}; font-weight: 500;">{icon} {sign}{metric_change.change_percent:.1f}% vs previous</span>'


def _format_trend_text(metric_change) -> str:
    """Format metric trend for plain text display."""
    if metric_change.change_percent is None:
        return "  (No comparison data available)"

    direction = "↑" if metric_change.trend == "up" else "↓" if metric_change.trend == "down" else "→"
    sign = "+" if metric_change.change_percent > 0 else ""

    return f"  {direction} {sign}{metric_change.change_percent:.1f}% compared to previous period"
