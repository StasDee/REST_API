import time
import logging
from functools import wraps
from requests.exceptions import HTTPError, Timeout, ConnectionError

logger = logging.getLogger(__name__)

def retry_on_failure(num_retries=3, wait_seconds=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait = wait_seconds
            for attempt in range(num_retries + 1):
                try:
                    res = func(*args, **kwargs)
                    # If attempt > 0, it means at least one failure happened before this success
                    if attempt > 0:
                        logger.info(f"Successfully recovered on attempt {attempt + 1}")
                    return res
                except (Timeout, ConnectionError, HTTPError) as e:
                    # Logic for filtering retries (5xx only)
                    if isinstance(e, HTTPError) and e.response is not None:
                        if e.response.status_code < 500:
                            raise

                    if attempt == num_retries:
                        logger.error(f"All {num_retries + 1} attempts failed. Last error: {e}")
                        raise

                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                    wait = min(wait * 2, 10)
        return wrapper
    return decorator