from typing import Callable, TypeVar, Coroutine, Any
from typing_extensions import ParamSpec

R = TypeVar("R")
P = ParamSpec("P")

# ruff: noqa
import asyncio
import functools
import logging
import random
import time
from pathlib import Path
import importlib.metadata

logger = logging.getLogger("activefence_client_sdk")


def _get_version() -> str:
    return importlib.metadata.version("activefence_client_sdk")


def _should_retry_exception(exception: Exception) -> bool:
    """
    Determine if an exception should trigger a retry.
    Returns True for any exception that isn't explicitly raised from the client,
    except for 4xx HTTP errors which are non-retriable.
    """
    # Don't retry on raw Exception instances (our HTTP error exceptions)
    if type(exception).__name__ == "Exception":
        # Check if this is an HTTP error with a status code
        error_str = str(exception)
        if ":" in error_str:
            try:
                status_code = int(error_str.split(":")[0])
                # Don't retry on 4xx client errors (except 429 which is retriable)
                if 400 <= status_code < 500 and status_code != 429:
                    return False
            except (ValueError, IndexError):
                pass
        return True

    # Retry on all other exceptions (network errors, timeouts, etc.)
    return True


def retry_with_exponential_backoff(
    max_retries: int = 3, base_delay: float = 1.0
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for retrying a function with exponential backoff and jitter.
    Jitter ranges from 50% to 100% of the calculated delay.
    Retries on all exceptions except raw Exception instances (HTTP errors),
    and specifically excludes 4xx client errors (except 429).

    Args:
        max_retries (int): Maximum number of retries
        base_delay (float): Base delay for exponential backoff in seconds
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1

                    # Check if we should retry this exception
                    if not _should_retry_exception(e) or retries > max_retries:
                        if retries > max_retries:
                            logger.error("Failed after %s retries: %s", max_retries, e)
                        else:
                            logger.error("Non-retryable error: %s", e)
                        raise e

                    # Calculate delay with exponential backoff and jitter
                    max_delay = base_delay * (2 ** (retries - 1))
                    delay = random.uniform(max_delay * 0.5, max_delay)

                    logger.warning(
                        "Attempt %s failed with error: %s. Retrying in %.2f seconds...",
                        retries,
                        e,
                        delay,
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


def async_retry_with_exponential_backoff(
    max_retries: int = 3, base_delay: float = 1.0
) -> Callable[[Callable[..., Coroutine[Any, Any, R]]], Callable[..., Coroutine[Any, Any, R]]]:
    """
    Decorator for retrying an async function with exponential backoff and jitter.
    Jitter ranges from 50% to 100% of the calculated delay.
    Retries on all exceptions except raw Exception instances (HTTP errors),
    and specifically excludes 4xx client errors (except 429).

    Args:
        max_retries (int): Maximum number of retries
        base_delay (float): Base delay for exponential backoff in seconds
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    # Check if we should retry this exception
                    if not _should_retry_exception(e) or retries > max_retries:
                        if retries > max_retries:
                            logger.error("Failed after %s retries: %s", max_retries, e)
                        else:
                            logger.error("Non-retryable error: %s", e)
                        raise e

                    # Calculate delay with exponential backoff and jitter
                    max_delay = base_delay * (2 ** (retries - 1))
                    delay = random.uniform(max_delay * 0.5, max_delay)

                    logger.warning(
                        "Attempt %s failed with error: %s. Retrying in %.2f seconds...",
                        retries,
                        e,
                        delay,
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
