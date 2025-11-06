"""Main entry point for Google Analytics Report Sender."""

import sys
from datetime import datetime, timedelta

from loguru import logger

from src.ai.summarizer import AISummarizer
from src.config import load_settings
from src.email.sender import EmailSender
from src.processing.analyzer import AnalyticsAnalyzer
from src.scheduler import ReportScheduler
from src.utils.logger import setup_logger
from src.google_analytics.client import GoogleAnalyticsClient


def generate_report() -> None:
    """Generate and send analytics report."""
    logger.info("=" * 60)
    logger.info("Starting analytics report generation")
    logger.info("=" * 60)

    try:
        # Load configuration
        settings = load_settings()
        logger.info(f"Configuration loaded for website: {settings.target_website}")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=settings.report_interval_days)
        logger.info(
            f"Report period: {start_date.date()} to {end_date.date()} "
            f"({settings.report_interval_days} days)"
        )

        # Fetch analytics data
        logger.info("Fetching analytics data from Google Analytics...")
        with GoogleAnalyticsClient(settings) as ga_client:
            analytics_data = ga_client.fetch_analytics(start_date, end_date)
        logger.info(
            f"Analytics data fetched: {analytics_data.audience.sessions} sessions, "
            f"{analytics_data.audience.total_users} users, "
            f"{analytics_data.total_conversions} conversions"
        )

        # Process and analyze data
        logger.info("Processing analytics data...")
        analyzer = AnalyticsAnalyzer()
        summary = analyzer.analyze(analytics_data)
        logger.info(
            f"Analysis complete: {len(summary.key_insights)} insights, "
            f"{len(summary.recommendations)} recommendations"
        )

        # Generate AI summary
        logger.info("Generating AI-powered summary...")
        ai_summarizer = AISummarizer(settings)
        ai_summary = ai_summarizer.generate_summary(
            summary,
            settings.target_website,
        )
        logger.info(f"AI summary generated ({len(ai_summary)} characters)")

        # Send email report
        logger.info("Sending email report...")
        email_sender = EmailSender(settings)
        email_sender.send_report(summary, ai_summary, settings.target_website)
        logger.info(f"Report sent successfully to {settings.email_to}")

        logger.info("=" * 60)
        logger.info("Analytics report generation completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)

        # Try to send error notification
        # try:
        #     settings = load_settings()
        #     email_sender = EmailSender(settings)
        #     email_sender.send_error_notification(
        #         error_message=str(e),
        #         error_details=f"Error type: {type(e).__name__}\n\nSee logs for full details.",
        #     )
        # except Exception as notify_error:
        #     logger.error(f"Failed to send error notification: {notify_error}")

        raise


def test_connections() -> bool:
    """
    Test all external connections (Google Analytics API, AI API, SMTP).

    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("Testing external connections...")

    try:
        settings = load_settings()
        all_passed = True

        # Test Google Analytics API
        logger.info("Testing Google Analytics API connection...")
        with GoogleAnalyticsClient(settings) as ga_client:
            if ga_client.test_connection():
                logger.info("✓ Google Analytics API connection successful")
            else:
                logger.error("✗ Google Analytics API connection failed")
                all_passed = False

        # Test AI API
        logger.info("Testing AI API connection...")
        ai_summarizer = AISummarizer(settings)
        if ai_summarizer.test_connection():
            logger.info("✓ AI API connection successful")
        else:
            logger.error("✗ AI API connection failed")
            all_passed = False

        # Test SMTP
        logger.info("Testing SMTP connection...")
        email_sender = EmailSender(settings)
        if email_sender.test_connection():
            logger.info("✓ SMTP connection successful")
        else:
            logger.error("✗ SMTP connection failed")
            all_passed = False

        if all_passed:
            logger.info("All connection tests passed!")
        else:
            logger.warning("Some connection tests failed. Check configuration.")

        return all_passed

    except Exception as e:
        logger.error(f"Connection test failed: {e}", exc_info=True)
        return False


def main() -> None:
    """Main entry point."""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Google Analytics Report Sender"
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run report generation once and exit (no scheduling)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test connections to external services and exit",
    )
    parser.add_argument(
        "--run-immediately",
        action="store_true",
        help="Run report immediately before starting scheduler",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    args = parser.parse_args()

    try:
        # Load settings to get log configuration
        settings = load_settings()

        # Setup logging
        setup_logger(
            log_level=args.log_level or settings.log_level,
            log_file=settings.log_file,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
        )

        logger.info("Google Analytics Report Sender started")
        logger.info(f"Python version: {sys.version}")

        # Test connections mode
        if args.test:
            success = test_connections()
            sys.exit(0 if success else 1)

        # Run once mode
        if args.run_once:
            generate_report()
            sys.exit(0)

        # Scheduled mode (default)
        scheduler = ReportScheduler(settings, generate_report)
        scheduler.start(run_immediately=args.run_immediately)

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
