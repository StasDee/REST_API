import asyncio
import time
import pytest

from mockapi_client.logger import get_logger
from core.normalizers import normalize_users
from core.validators import validate_users

logger = get_logger(__name__)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.contract,
    pytest.mark.concurrency,
]


@pytest.mark.asyncio
@pytest.mark.contract
@pytest.mark.parametrize("burst_size", [20, 30, 50])
async def test_concurrent_user_burst_create(
        async_api_client,
        user_factory,
        cleanup_registry,
        burst_size,
):
    """
    Burst test: create a larger number of users concurrently to simulate traffic spikes
    and validate backend stability.

    Purpose:
    - Verify API handles bursts of 20–50 concurrent CREATE requests.
    - Ensure no partial failures, corrupted responses, or duplicate IDs.
    - All created users satisfy contract validation.

    Notes:
    - Measures rough total duration (informational only).
    - Uses existing async infrastructure, factory, logging, and cleanup.
    - Keeps validation lightweight to reduce flakiness.
    """

    logger.info("-" * 60)
    logger.info(f"Starting burst user creation test with {burst_size} users")

    payloads = [user_factory.create_user_payload() for _ in range(burst_size)]
    logger.info(f"Prepared {burst_size} user payloads")

    start_time = time.time()

    # Create users concurrently
    tasks = [async_api_client.create_user(payload) for payload in payloads]
    results = await asyncio.gather(*tasks)

    duration = time.time() - start_time
    logger.info(f"Burst creation completed in {duration:.2f} seconds")

    # Normalize and validate responses
    normalized_users = normalize_users(results)
    validate_users(normalized_users)
    logger.info("All burst users passed contract validation")

    # Basic checks and cleanup
    assert len(results) == burst_size

    user_ids = set()
    for user in results:
        assert user is not None
        assert "id" in user
        user_ids.add(user["id"])
        cleanup_registry.append(user["id"])
        logger.info(f"User created in burst: {user['id']}")

    # Ensure all IDs are unique
    assert len(user_ids) == burst_size, "Duplicate user IDs detected during burst creation"

    logger.info(f"Burst user creation test with {burst_size} users completed successfully")
