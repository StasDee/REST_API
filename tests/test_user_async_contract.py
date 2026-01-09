import pytest

from mockapi_client.logger import get_logger

from mockapi_client.async_client import AsyncUsersApiClient
from core.normalizers import normalize_users
from core.validators import validate_users

logger = get_logger(__name__)


@pytest.mark.asyncio
@pytest.mark.contract
async def test_async_user_create_and_validate(config):
    """
    Async contract test:
    1. Create user asynchronously
    2. Normalize API response
    3. Validate contract rules

    Purpose:
    - Ensure async client works with the existing contract validation
    - Demonstrate async CRUD pattern
    """
    logger.info("Creating async user for contract test")
    async with AsyncUsersApiClient(
            base_url=config.base_url,
            headers=config.headers
    ) as api:
        created_user = await api.create_user(
            {
                "first_name": "Async",
                "last_name": "User",
                "email": "async.user@test.com",
            }
        )

        assert created_user is not None
        assert "id" in created_user

        normalized = normalize_users([created_user])
        validate_users(normalized)
