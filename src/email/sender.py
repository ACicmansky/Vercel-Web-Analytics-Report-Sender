"""Email sending functionality using SMTP."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from loguru import logger

from src.config import Settings
from src.email.templates import create_html_email, create_plain_text_email
from src.processing.analyzer import AnalyticsSummary
from src.utils.retry import retry_on_network_error


class EmailSendError(Exception):
    """Custom exception for email sending errors."""

    pass


class EmailSender:
    """Email sender for analytics reports."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize email sender.

        Args:
            settings: Application settings containing SMTP configuration
        """
        self.settings = settings
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_use_tls = settings.smtp_use_tls
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from
        self.email_from_name = settings.email_from_name
        self.email_to = settings.email_to
        self.subject_prefix = settings.email_subject_prefix

        logger.info(f"Email sender initialized (SMTP: {self.smtp_host}:{self.smtp_port})")

    @retry_on_network_error
    def send_report(
        self,
        summary: AnalyticsSummary,
        ai_summary: str,
        website: str,
    ) -> bool:
        """
        Send analytics report via email.

        Args:
            summary: Processed analytics summary
            ai_summary: AI-generated summary text
            website: Website name

        Returns:
            True if email sent successfully

        Raises:
            EmailSendError: If email sending fails
        """
        logger.info(f"Preparing to send analytics report for {website}")

        try:
            # Create email message
            msg = self._create_message(summary, ai_summary, website)

            # Send email
            self._send_smtp(msg)

            logger.info(f"Analytics report sent successfully to {self.email_to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise EmailSendError(f"Email sending failed: {e}") from e

    def send_error_notification(
        self,
        error_message: str,
        error_details: Optional[str] = None,
    ) -> bool:
        """
        Send error notification email.

        Args:
            error_message: Brief error description
            error_details: Detailed error information

        Returns:
            True if notification sent successfully
        """
        if not self.settings.error_notification_email:
            logger.debug("Error notification email not configured, skipping")
            return False

        logger.info("Sending error notification email")

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"{self.subject_prefix} Error Notification"
            msg["From"] = f"{self.email_from_name} <{self.email_from}>"
            msg["To"] = self.settings.error_notification_email

            # Create plain text version
            text_content = f"""
ERROR NOTIFICATION
==================

An error occurred while generating the analytics report.

Error: {error_message}

Details:
{error_details or 'No additional details available'}

Please check the application logs for more information.
            """

            # Create HTML version
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #fee; border-left: 4px solid #f00; padding: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0 0 10px 0; color: #c00;">⚠️ Error Notification</h2>
            <p style="margin: 0;">An error occurred while generating the analytics report.</p>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px;">
            <h3 style="margin: 0 0 10px 0;">Error:</h3>
            <p style="margin: 0; font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                {error_message}
            </p>
        </div>
        
        {f'''
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin-top: 15px;">
            <h3 style="margin: 0 0 10px 0;">Details:</h3>
            <pre style="margin: 0; font-family: monospace; background: white; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px;">
{error_details}
            </pre>
        </div>
        ''' if error_details else ''}
        
        <p style="margin-top: 20px; font-size: 14px; color: #666;">
            Please check the application logs for more information.
        </p>
    </div>
</body>
</html>
            """

            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Send email
            self._send_smtp(msg)

            logger.info("Error notification sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            return False

    def _create_message(
        self,
        summary: AnalyticsSummary,
        ai_summary: str,
        website: str,
    ) -> MIMEMultipart:
        """Create email message with HTML and plain text versions."""
        # Create message
        msg = MIMEMultipart("alternative")
        
        # Set headers
        subject = (
            f"{self.subject_prefix} {website} - "
            f"{summary.period_start.strftime('%b %d')} to "
            f"{summary.period_end.strftime('%b %d, %Y')}"
        )
        msg["Subject"] = subject
        msg["From"] = f"{self.email_from_name} <{self.email_from}>"
        msg["To"] = self.email_to

        # Create plain text version
        text_content = create_plain_text_email(summary, ai_summary, website)
        text_part = MIMEText(text_content, "plain")

        # Create HTML version
        html_content = create_html_email(summary, ai_summary, website)
        html_part = MIMEText(html_content, "html")

        # Attach parts (plain text first, then HTML)
        msg.attach(text_part)
        msg.attach(html_part)

        logger.debug(f"Email message created: {subject}")
        return msg

    def _send_smtp(self, msg: MIMEMultipart) -> None:
        """Send email via SMTP."""
        logger.debug(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")

        try:
            # Create SMTP connection
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)

            # Login
            server.login(self.smtp_username, self.smtp_password)
            logger.debug("SMTP authentication successful")

            # Send email
            server.send_message(msg)
            server.quit()

            logger.debug("Email sent via SMTP")

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise EmailSendError(
                "SMTP authentication failed. Check username/password."
            ) from e
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise EmailSendError(f"SMTP error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise EmailSendError(f"Unexpected error: {e}") from e

    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing SMTP connection...")

            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)

            server.login(self.smtp_username, self.smtp_password)
            server.quit()

            logger.info("SMTP connection test successful")
            return True

        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
