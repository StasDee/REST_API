from mockapi_client.logger import get_logger
import requests
from time import sleep
from typing import Dict, List, Optional, Any
from requests.exceptions import HTTPError
from .decorators import retry_on_failure
from .config import BASE_URL, DEFAULT_TIMEOUT, TOKEN

logger = get_logger(__name__)


class UsersApiClient:
    def __init__(
            self,
            base_url: str = BASE_URL,
            timeout: int = DEFAULT_TIMEOUT
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def _request(self, method: str, endpoint: str = "", **kwargs) -> Optional[Any]:
        url = f"{self.base_url}/{endpoint}".rstrip('/')
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)

        # Handle specific MockAPI 500 behaviors
        if resp.status_code >= 500:
            raise HTTPError(f"Server Error: {resp.status_code}", response=resp)

        if resp.status_code == 404:
            return None

        resp.raise_for_status()
        return resp.json() if resp.content else None

    @retry_on_failure()
    def create_user(self, user_data: Dict) -> Dict:
        return self._request("POST", json=user_data)

    @retry_on_failure()
    def get_user(self, user_id: str) -> Optional[Dict]:
        return self._request("GET", endpoint=user_id)

    @retry_on_failure()
    def patch_user(self, user_id: str, partial_data: Dict) -> Dict:
        return self._request("PATCH", endpoint=user_id, json=partial_data)

    @retry_on_failure()
    def delete_user(self, user_id: str) -> bool:
        self._request("DELETE", endpoint=user_id)
        return True

    @retry_on_failure()
    def list_users(self) -> List[Dict]:
        return self._request("GET") or []

    def get_user_status(self, user_id):
        url = f"{self.base_url}/{user_id}"
        resp = self.session.get(url)
        return resp.status_code

    def wait_until_deleted(self, user_id, retries=5, delay=1):
        """
        Polls the API until the user is no longer found.
        Returns True if deleted, False otherwise.
        """
        for i in range(retries):
            # Reuse your existing status check method
            if self.get_user_status(user_id) in [404, 500]:
                return True
            logger.debug(f"Waiting for deletion verification for {user_id}... attempt {i + 1}")
            sleep(delay)
        return False
