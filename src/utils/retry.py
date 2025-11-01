"""Retry logic utilities using tenacity."""

from typing import Any, Callable, TypeVar

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


def with_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        exceptions: Tuple of exception types to retry on

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
        def fetch_data():
            # ... code that might fail
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
        )
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.warning(
                    f"Retry attempt for {func.__name__} due to: {type(e).__name__}: {e}"
                )
                raise

        return wrapper

    return decorator


# Predefined retry decorators for common scenarios

def retry_on_network_error(func: Callable[..., T]) -> Callable[..., T]:
    """Retry on network-related errors."""
    return with_retry(
        max_attempts=3,
        min_wait=2,
        max_wait=30,
        exceptions=(ConnectionError, TimeoutError),
    )(func)


def retry_on_api_error(func: Callable[..., T]) -> Callable[..., T]:
    """Retry on API-related errors (rate limiting, temporary failures)."""
    return with_retry(
        max_attempts=5,
        min_wait=5,
        max_wait=60,
        exceptions=(ConnectionError, TimeoutError),
    )(func)
