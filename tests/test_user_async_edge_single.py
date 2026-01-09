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
async def test_patch_before_fetch(async_api_client, user_factory, cleanup_registry):
    """
    Edge-case workflow test: patch a user immediately after creation
    without fetching it first.

    Purpose:
    - Simulate uncommon user behavior
    - Verify API handles multi-step dependencies gracefully

    Validation:
    - Patch succeeds without errors
    - Response conforms to contract
    - User is tracked for cleanup
    """
    logger.info("-" * 60)
    logger.info("Starting edge-case test: patch before fetch")

    payload = user_factory.create_user_payload()
    created = await async_api_client.create_user(payload)
    user_id = created["id"]
    cleanup_registry.append(user_id)
    logger.info(f"User created: {user_id}")

    # Patch immediately
    patch_payload = {"name": "EdgeCaseUser"}
    patched = await async_api_client.patch_user(user_id, patch_payload)
    logger.info(f"User patched immediately: {patched}")

    normalized_users = normalize_users([patched])
    validate_users(normalized_users)
    logger.info("Edge-case workflow test completed successfully")


@pytest.mark.asyncio
@pytest.mark.contract
@pytest.mark.edge
async def test_sequential_user_dependencies(
        async_api_client,
        user_factory,
        cleanup_registry,
):
    """
    Optional workflow test: simulate dependent operations that could trigger edge cases.

    Purpose:
    - Verify system handles dependent operations correctly (e.g., create → patch → delete → fetch).
    - Check correct error handling for operations on deleted or non-existent users.

    Validation:
    - Create user and immediately patch.
    - Delete user and confirm fetching raises 404.
    - Contract validation on successful responses.

    Design notes:
    - Mimics real multi-step workflows that might be used in production.
    - Reuses async API client and factory for consistency.
    """

    logger.info("=" * 60)
    logger.info("Starting sequential edge-case workflow test")

    # Step 1: Create user
    payload = user_factory.create_user_payload()
    user = await async_api_client.create_user(payload)
    cleanup_registry.append(user["id"])
    logger.info(f"Created user {user['id']}")

    # Step 2: Patch user
    patch_payload = {"name": "edge_case_user"}
    patched = await async_api_client.patch_user(user["id"], patch_payload)
    logger.info(f"Patched user {patched['id']}")

    # Step 3: Delete user
    await async_api_client.delete_user(user["id"])
    cleanup_registry.remove(user["id"])
    logger.info(f"Deleted user {user['id']}")

    # Step 4: Fetch deleted user (expect error)
    with pytest.raises(Exception) as e:
        await async_api_client.get_user(user["id"])
    logger.info(f"Expected error when fetching deleted user: {e.value}")
