from mockapi_client.logger import get_logger
import requests
from time import sleep
from typing import Dict, List, Optional, Any
from requests.exceptions import HTTPError
from .decorators import retry_on_failure
from .config import BASE_URL, DEFAULT_TIMEOUT, TOKEN

logger = get_logger(__name__)


class UsersApiClient:
    """
       Users API client.

       Design contract:
       - 2xx  -> returns parsed JSON (or None if empty)
       - 404  -> returns None
       - 4xx  -> raises HTTPError
       - 5xx  -> raises HTTPError (retryable)
    """

    def __init__(
            self,
            base_url: str = BASE_URL,
            timeout: int = DEFAULT_TIMEOUT,
            session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            }
        )

    # -------------------------------------------------
    # Context manager support
    # -------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    # -------------------------------------------------
    # Core request handler
    # -------------------------------------------------

    def _request(
            self,
            method: str,
            endpoint: str = "",
            **kwargs
    ) -> Optional[Any]:
        url = f"{self.base_url}/{endpoint}".rstrip("/")
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)

        # # Handle specific MockAPI 500 behaviors
        # if response.status_code >= 500:
        #     raise HTTPError(f"Server Error: {response.status_code}", response=resp)

        # Explicit 404 contract
        if response.status_code == 404:
            return None

        # Raise for any other error (4xx / 5xx)
        try:
            response.raise_for_status()
        except HTTPError as exc:
            logger.error(
                "HTTP error",
                extra={
                    "method": method,
                    "url": url,
                    "status": response.status_code,
                    "body": response.text,
                },
            )
            raise exc

        # Successful response
        if not response.content:
            return None

        return response.json()

    # -------------------------------------------------
    # API methods
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Utility helpers (non-contractual)
    # -------------------------------------------------

    def get_user_status(self, user_id):
        url = f"{self.base_url}/{user_id}"
        response = self.session.get(url, timeout=self.timeout)
        return response.status_code

    def wait_until_deleted(self, user_id: str, retries: int = 5, delay: int = 1) -> bool:
        """
        Polls until the user is no longer found.
        Returns True if deletion is confirmed.
        """
        for attempt in range(1, retries + 1):
            status = self.get_user_status(user_id)
            if status == 404:
                return True

            logger.debug(
                f"Waiting for deletion of user {user_id} "
                f"(attempt {attempt}/{retries})"
            )
            sleep(delay)

        return False
