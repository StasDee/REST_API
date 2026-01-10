import pytest
from mockapi_client.client import UsersApiClient
from mockapi_client.async_client import AsyncUsersApiClient
from mockapi_client.factory import UserFactory
from mockapi_client.logger import get_logger

logger = get_logger(__name__)


# -----------------------------
# Synchronous API client fixture
# -----------------------------
@pytest.fixture(scope="module")
def api_client():
    with UsersApiClient() as client:
        yield client


# -----------------------------
# Asynchronous API client fixture
# -----------------------------
@pytest.fixture(scope="module")
async def async_api_client():
    async with AsyncUsersApiClient() as client:
        yield client


# -----------------------------
# UserFactory fixture
# -----------------------------
@pytest.fixture
def user_factory():
    factory = UserFactory()
    yield factory
    # After the test finishes, clear the used names set
    factory.reset()
    logger.debug("UserFactory memory cleared")


# -----------------------------
# Cleanup registry fixture
# -----------------------------
@pytest.fixture(scope="module")
async def cleanup_registry():
    """
    Store users created during tests for teardown.
    Each item is a tuple: (client, user_id, is_async)
    """
    registry = []
    yield registry

    if not registry:
        return

    print("\n")
    logger.info("-" * 60)
    logger.info(f"Final Teardown: Deleting {len(registry)} users")

    failed_deletions = []

    for client, user_id, is_async in registry:
        try:
            logger.debug(f"Deleting user {user_id} (async={is_async})...")

            if is_async:
                # Async deletion
                await client.delete_user(user_id)
                if hasattr(client, "wait_until_deleted"):
                    if not await client.wait_until_deleted(user_id):
                        logger.error(f"Timeout verifying deletion for user: {user_id}")
                        failed_deletions.append(user_id)
            else:
                # Sync deletion
                client.delete_user(user_id)
                if hasattr(client, "wait_until_deleted"):
                    if not client.wait_until_deleted(user_id):
                        logger.error(f"Timeout verifying deletion for user: {user_id}")
                        failed_deletions.append(user_id)

            logger.debug(f"Successfully deleted user {user_id}")

        except Exception as e:
            logger.exception(f"Error deleting user {user_id}: {e}")
            failed_deletions.append(user_id)

    assert not failed_deletions, f"Teardown failed for users: {failed_deletions}"
    logger.info("Cleanup completed successfully.")
    logger.info("-" * 60)


# -----------------------------
# Separator for readability
# -----------------------------
@pytest.fixture(autouse=True)
def separator():
    print("\n")
    yield
