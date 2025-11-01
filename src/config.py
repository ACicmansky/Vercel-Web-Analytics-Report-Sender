"""Configuration management using pydantic-settings."""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Vercel Configuration
    vercel_api_token: str = Field(..., description="Vercel API authentication token")
    vercel_team_id: Optional[str] = Field(None, description="Vercel team ID")
    vercel_project_id: Optional[str] = Field(None, description="Vercel project ID")
    target_website: str = Field(..., description="Target website to track")

    # AI Configuration
    google_api_key: str = Field(..., description="Google Gemini API key")
    ai_model: str = Field(
        default="gemini-2.5-flash",
        description="AI model to use for summaries",
    )

    # Email Configuration
    smtp_host: str = Field(..., description="SMTP server hostname")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    smtp_username: str = Field(..., description="SMTP username")
    smtp_password: str = Field(..., description="SMTP password")

    email_from: str = Field(..., description="Sender email address")
    email_from_name: str = Field(
        default="Vercel Analytics Reporter",
        description="Sender name",
    )
    email_to: str = Field(..., description="Recipient email address")
    email_subject_prefix: str = Field(
        default="[Analytics Report]",
        description="Email subject prefix",
    )

    # Scheduling Configuration
    report_interval_days: int = Field(
        default=30,
        description="Report interval in days",
        ge=1,
    )
    report_time: str = Field(
        default="09:00",
        description="Time to send report (HH:MM format)",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for scheduling",
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    log_rotation: str = Field(default="10 MB", description="Log rotation size")
    log_retention: str = Field(default="30 days", description="Log retention period")

    # Optional: Error Notification
    error_notification_email: Optional[str] = Field(
        None,
        description="Email for error notifications",
    )

    @field_validator("report_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time format is HH:MM."""
        try:
            hours, minutes = v.split(":")
            if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
                raise ValueError
            return v
        except (ValueError, AttributeError):
            raise ValueError("report_time must be in HH:MM format (24-hour)")

    @field_validator("ai_model")
    @classmethod
    def validate_ai_model(cls, v: str, info) -> str:
        """Validate AI model is supported."""
        gemini_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ]

        if v in gemini_models or v.startswith("gemini"):
            return v

        raise ValueError(
            f"Unsupported AI model: {v}. "
            f"Supported models: {gemini_models}"
        )


def load_settings() -> Settings:
    """Load and validate application settings."""
    try:
        settings = Settings()  # type: ignore
        return settings
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}") from e
