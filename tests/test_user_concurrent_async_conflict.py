import asyncio
import pytest

from mockapi_client.logger import get_logger

logger = get_logger(__name__)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.contract,
    pytest.mark.edge,
]


@pytest.mark.asyncio
@pytest.mark.contract
@pytest.mark.edge
@pytest.mark.parametrize("concurrent_attempts", [5, 10])
async def test_parallel_user_creation_conflict(
        async_api_client,
        user_factory,
        cleanup_registry,
        concurrent_attempts,
):
    """
    Edge-case concurrency test: attempt to create multiple users with the same email simultaneously.

    Purpose:
    - Verify backend correctly handles race conditions for unique constraints.
    - Ensure only one user is created, others fail gracefully.

    Validation:
    - Only one user with the duplicate email exists.
    - All exceptions are caught and logged.
    - Cleanup registry only includes successfully created users.

    Design notes:
    - Uses asyncio.gather to execute concurrent create requests.
    - Reuses existing factory, logging, and cleanup mechanisms.
    """

    logger.info("-" * 60)
    logger.info(f"Testing {concurrent_attempts} parallel creation attempts with the same email")

    # Shared payload with the same email
    payload = user_factory.create_user_payload()
    payloads = [{**payload} for _ in range(concurrent_attempts)]

    # Launch all creates concurrently
    tasks = [async_api_client.create_user(p) for p in payloads]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    created_users = []
    for result in results:
        if isinstance(result, Exception):
            logger.info(f"Expected failure caught: {result}")
        else:
            created_users.append(result)
            cleanup_registry.append(result["id"])
            logger.info(f"User created: {result['id']}")

    # Only one user should be successfully created
    assert len(created_users) == 1, "Multiple users created with duplicate email"
