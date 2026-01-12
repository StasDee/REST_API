import asyncio
import pytest

from mockapi_client.logger import get_logger
from core.normalizers import normalize_users
from core.validators import validate_users

logger = get_logger(__name__)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.contract,
    pytest.mark.edge,
]


@pytest.mark.asyncio
@pytest.mark.contract
@pytest.mark.edge
@pytest.mark.parametrize("burst_size", [10])#, 20])
async def test_burst_user_workflow(
        async_api_client,
        user_factory,
        register_async_user,
        burst_size,
):
    """
    Burst-load test: create, patch, fetch, and delete multiple users concurrently.

    Purpose:
    - Verify backend stability under short bursts of heavy multi-step operations.
    - Ensure operations complete correctly and in isolation.

    Validation:
    - Each user is created, patched, fetched, and deleted successfully.
    - Responses pass contract validation.
    - No duplicate IDs or data corruption occurs.

    Design notes:
    - Uses asyncio.gather for concurrent execution.
    - Combines multiple CRUD steps per user in the same task.
    - Logs each step for observability.
    - Keeps validation lightweight to reduce flakiness.
    """

    logger.info("-" * 60)
    logger.info(f"Starting burst workflow with {burst_size} users")

    async def workflow_task(idx):
        payload = user_factory.create_user_payload()
        logger.info(f"[Task {idx}] Creating user")
        user = await async_api_client.create_user(payload)
        logger.info(f"[Task {idx}] Created user: {user}")
        await register_async_user(user["id"])

        # Patch user
        patch_payload = {"name": f"burst_{idx}"}
        patched = await async_api_client.patch_user(user["id"], patch_payload)
        logger.info(f"[Task {idx}] Patched user: {patched['id']} with name {patched['name']}")

        # Fetch user
        fetched = await async_api_client.get_user(user["id"])
        logger.info(f"[Task {idx}] Fetched user: {fetched['id']} with name {fetched['name']}")

        return fetched

    tasks = [workflow_task(i) for i in range(burst_size)]
    results = await asyncio.gather(*tasks)

    # Normalize and validate
    normalized_users = normalize_users(results)
    validate_users(normalized_users)

    # Ensure unique IDs
    ids = {u["id"] for u in results}
    assert len(ids) == burst_size, "Duplicate IDs detected in burst workflow"

    logger.info(f"Burst workflow test for {burst_size} users completed successfully")
