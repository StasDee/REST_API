# mockapi_client/async_decorators.py
import asyncio
import functools


def async_retry(attempts=3, delay=0.5):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    if attempt == attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))

        return wrapper

    return decorator
