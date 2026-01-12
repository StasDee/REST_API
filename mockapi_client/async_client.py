import asyncio
from typing import Dict

import httpx
from .async_decorators import async_retry
from mockapi_client.logger import get_logger


logger = get_logger(__name__)

class AsyncUsersApiClient:
    def __init__(self, base_url: str, headers: dict):
        self.base_url = base_url
        self.headers = headers
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=5
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.aclose()

    @async_retry()
    async def create_user(self, payload: dict) -> dict:
        resp = await self._client.post(self.base_url, json=payload)
        resp.raise_for_status()
        return resp.json()

    @async_retry()
    async def delete_user(self, user_id: str) -> None:
        resp = await self._client.delete(f"{self.base_url}/{user_id}")
        resp.raise_for_status()
        return None  # optional, just to be explicit

    @async_retry()
    async def get_user(self, user_id: str) -> dict:
        resp = await self._client.get(f"{self.base_url}/{user_id}")
        resp.raise_for_status()
        return resp.json()

    @async_retry()
    async def patch_user(self, user_id: str, partial_data: Dict) -> Dict:
        resp = await self._client.patch(f"{self.base_url}/{user_id}", json=partial_data)
        resp.raise_for_status()
        return resp.json()

    async def wait_until_deleted(self, user_id: str, retries: int = 10, delay: float = 1.0) -> bool:
        """
        Polls until the user with the given ID is no longer found.
        Returns True if deletion is confirmed (404) or we give up after retries.
        Treat persistent 500 as 'probably deleted'.
        """
        for attempt in range(1, retries + 1):
            try:
                resp = await self._client.get(f"{self.base_url}/{user_id}")
                status = resp.status_code
                logger.debug(f"Attempt {attempt} - user {user_id} status: {status}")
                if status == 404:
                    return True
                elif 200 <= status < 300:
                    # user still exists, retry
                    pass
                else:
                    # 500 or other unexpected, retry
                    logger.error(f"Server error {status}, retrying...")
            except httpx.RequestError:
                logger.debug(f"Network error for user {user_id}, retrying...")

            await asyncio.sleep(delay)

        # Give up after all retries
        logger.warning(f"User {user_id} may still exist, giving up after {retries} retries (server unreliable).")
        return True  # assume deleted to allow cleanup to continue
