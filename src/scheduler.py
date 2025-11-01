"""Job scheduling using APScheduler."""

from datetime import datetime, timedelta
from typing import Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from pytz import timezone as pytz_timezone

from src.config import Settings


class ReportScheduler:
    """Scheduler for periodic analytics report generation."""

    def __init__(self, settings: Settings, report_job: Callable) -> None:
        """
        Initialize the scheduler.

        Args:
            settings: Application settings
            report_job: Callable function to execute for report generation
        """
        self.settings = settings
        self.report_job = report_job
        self.timezone = pytz_timezone(settings.timezone)
        
        # Parse report time
        hour, minute = map(int, settings.report_time.split(":"))
        self.report_hour = hour
        self.report_minute = minute
        
        # Initialize scheduler
        self.scheduler = BlockingScheduler(timezone=self.timezone)
        
        logger.info(
            f"Scheduler initialized (interval: {settings.report_interval_days} days, "
            f"time: {settings.report_time}, timezone: {settings.timezone})"
        )

    def start(self, run_immediately: bool = False) -> None:
        """
        Start the scheduler.

        Args:
            run_immediately: If True, run the job immediately before starting schedule
        """
        logger.info("Starting scheduler...")

        # Add the scheduled job
        # Run every N days at specified time
        trigger = CronTrigger(
            hour=self.report_hour,
            minute=self.report_minute,
            timezone=self.timezone,
        )

        self.scheduler.add_job(
            self.report_job,
            trigger=trigger,
            id="analytics_report",
            name="Generate Analytics Report",
            replace_existing=True,
        )

        # Calculate next run time
        next_run = self.scheduler.get_jobs()[0].next_run_time
        logger.info(f"Next report scheduled for: {next_run}")

        # Run immediately if requested
        if run_immediately:
            logger.info("Running report immediately as requested...")
            try:
                self.report_job()
            except Exception as e:
                logger.error(f"Immediate report execution failed: {e}")

        # Start the scheduler (blocking)
        try:
            logger.info("Scheduler started. Press Ctrl+C to exit.")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.shutdown()

    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        logger.info("Shutting down scheduler...")
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        logger.info("Scheduler shutdown complete")

    def run_once(self) -> None:
        """Run the report job once without scheduling."""
        logger.info("Running report job once (no scheduling)...")
        try:
            self.report_job()
            logger.info("Report job completed successfully")
        except Exception as e:
            logger.error(f"Report job failed: {e}")
            raise

    def get_next_run_time(self) -> datetime:
        """
        Get the next scheduled run time.

        Returns:
            Next run datetime
        """
        jobs = self.scheduler.get_jobs()
        if jobs:
            return jobs[0].next_run_time
        return None

    def calculate_date_range(self) -> tuple[datetime, datetime]:
        """
        Calculate the date range for the report.

        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = datetime.now(self.timezone)
        start_date = end_date - timedelta(days=self.settings.report_interval_days)
        
        logger.debug(
            f"Report date range: {start_date.date()} to {end_date.date()} "
            f"({self.settings.report_interval_days} days)"
        )
        
        return start_date, end_date
