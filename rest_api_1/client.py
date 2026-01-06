import requests
from typing import Dict, List, Optional, Any
from requests.exceptions import HTTPError
from decorators import retry_on_failure
import config


class UsersApiClient:
    def __init__(
            self,
            base_url: str = config.BASE_URL,
            timeout: int = config.DEFAULT_TIMEOUT
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {config.TOKEN}",
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
