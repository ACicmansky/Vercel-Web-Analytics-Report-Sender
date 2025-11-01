"""AI-powered analytics summarization."""

from typing import Optional

from google import genai
from google.genai import types
from loguru import logger

from src.ai.prompts import create_summary_prompt, create_system_prompt
from src.config import Settings
from src.processing.analyzer import AnalyticsSummary
from src.utils.retry import retry_on_api_error


class AISummarizerError(Exception):
    """Custom exception for AI summarizer errors."""

    pass


class AISummarizer:
    """AI-powered analytics summarizer using Google Gemini."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize AI summarizer.

        Args:
            settings: Application settings containing AI API credentials
        """
        self.settings = settings
        self.model = settings.ai_model
        self.client = genai.Client(api_key=settings.google_api_key)

        logger.info(f"AI summarizer initialized with Google Gemini model: {self.model}")

    @retry_on_api_error
    def generate_summary(
        self,
        analytics_summary: AnalyticsSummary,
        website: str,
    ) -> str:
        """
        Generate AI-powered summary from analytics data.

        Args:
            analytics_summary: Processed analytics summary
            website: Website name

        Returns:
            Generated summary text

        Raises:
            AISummarizerError: If summary generation fails
        """
        logger.info(f"Generating AI summary for {website}")

        try:
            system_prompt = create_system_prompt()
            user_prompt = create_summary_prompt(analytics_summary, website)

            logger.debug(f"Sending request to Google Gemini with model: {self.model}")

            # Generate content with system instruction
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=1000,
                ),
            )

            summary = response.text

            logger.info(
                f"Successfully generated summary ({len(summary)} chars)"
            )

            return summary

        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise AISummarizerError(f"Summary generation failed: {e}") from e

    def test_connection(self) -> bool:
        """
        Test AI API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test request
            response = self.client.models.generate_content(
                model=self.model,
                contents="Test connection. Reply with 'OK'.",
                config=types.GenerateContentConfig(
                    max_output_tokens=10,
                ),
            )
            logger.info("Google Gemini API connection test successful")
            return True

        except Exception as e:
            logger.error(f"Google Gemini API connection test failed: {e}")
            return False
