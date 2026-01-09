import httpx
from .async_decorators import async_retry


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

    async def get_user(self, user_id: str) -> dict:
        resp = await self._client.get(f"{self.base_url}/{user_id}")
        resp.raise_for_status()
        return resp.json()
