from functools import wraps
from requests.exceptions import HTTPError, Timeout, ConnectionError
import time
from .logger import get_logger

logger = get_logger(__name__)


def retry_on_failure(num_retries=3, wait_seconds=2):
    """
    Decorator to retry a function call on network errors or 5xx HTTP errors.
    Exponential backoff is applied between retries.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait = wait_seconds
            # +1 because we want to include the initial attempt
            for attempt in range(num_retries + 1):
                try:
                    res = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"Recovered on attempt {attempt + 1}")
                    return res
                except (Timeout, ConnectionError, HTTPError) as e:
                    # Only retry on server errors (5xx); propagate 4xx immediately
                    if isinstance(e, HTTPError) and e.response is not None:
                        if e.response.status_code < 500:
                            raise

                    if attempt == num_retries:
                        logger.error(f"All {num_retries + 1} attempts failed. Last error: {e}")
                        raise

                    logger.warning(
                        f"[Attempt {attempt + 1}/{num_retries + 1}] "
                        f"Caught {type(e).__name__}: {e}. Retrying in {wait}s..."
                    )
                    time.sleep(wait)
                    # exponential backoff capped at 10s
                    wait = min(wait * 2, 10)

        return wrapper

    return decorator
