import asyncio
import pytest_asyncio
import pytest
from mockapi_client.client import UsersApiClient
from mockapi_client.async_client import AsyncUsersApiClient
from mockapi_client.factory import UserFactory
from mockapi_client.logger import get_logger
from ResilientAPI.mockapi_client.config import BASE_URL

logger = get_logger(__name__)


# =========================================================
# Clients
# =========================================================

@pytest.fixture(scope="session")
def api_client():
    with UsersApiClient() as client:
        yield client


@pytest_asyncio.fixture  # (scope="session")
async def async_api_client():
    async with AsyncUsersApiClient(base_url=BASE_URL, headers={}) as client:
        yield client


# =========================================================
# Factory
# =========================================================

@pytest.fixture
def user_factory():
    factory = UserFactory()
    yield factory
    factory.reset()
    logger.debug("UserFactory memory cleared")


# =========================================================
# Cleanup Registry (safe for sync + async)
# =========================================================

@pytest.fixture(scope="session")
def cleanup_registry():
    """
    Separate registries prevent cross-execution bugs.
    """
    return {
        "sync": set(),
        "async": set(),
    }


# =========================================================
# Registry helpers (used by tests)
# =========================================================

@pytest.fixture
def register_sync_user(cleanup_registry):
    def _register(user_id: str):
        cleanup_registry["sync"].add(user_id)

    return _register


@pytest_asyncio.fixture
async def register_async_user(cleanup_registry):
    async def _register(user_id: str):
        cleanup_registry["async"].add(user_id)

    return _register


# =========================================================
# The One True Janitor™
# =========================================================

@pytest.fixture(scope="session", autouse=True)
def final_cleanup(cleanup_registry):
    """
    Runs exactly once.
    Safe.
    Deterministic.
    """
    yield

    # -------------------
    # Sync cleanup
    # -------------------

    if cleanup_registry["sync"]:
        logger.info(
            f"--- Sync Cleanup: {len(cleanup_registry['sync'])} users ---"
        )
        with UsersApiClient() as client:
            for user_id in cleanup_registry["sync"]:
                try:
                    client.delete_user(user_id)
                    logger.debug(f"Successfully deleted user with id: {user_id}")
                except Exception as e:
                    logger.error(f"Failed to delete {user_id}: {e}")

    # -------------------
    # Async cleanup
    # -------------------

    if cleanup_registry["async"]:
        logger.info(
            f"--- Async Cleanup: {len(cleanup_registry['async'])} users ---"
        )

        async def _async_cleanup():
            async with AsyncUsersApiClient(base_url=BASE_URL, headers={}) as client:
                for user_id in cleanup_registry["async"]:
                    logger.debug(f"Deleting async user: {user_id}")
                    try:
                        await client.delete_user(user_id)
                        # Wait until deletion is confirmed
                        success = await client.wait_until_deleted(user_id)
                        logger.debug(f"Deletion confirmed: {success}")
                        if success:
                            logger.debug(f"Deleted async user {user_id}")
                        else:
                            logger.error(f"User {user_id} still exists after deletion")
                    except Exception as e:
                        logger.error(f"Failed to delete async user {user_id}: {e}")

        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(_async_cleanup())
        except RuntimeError:
            asyncio.run(_async_cleanup())


@pytest.fixture(autouse=True)
def separator():
    print("\n")
    yield
