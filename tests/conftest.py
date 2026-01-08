import pytest
from mockapi_client.client import UsersApiClient
from mockapi_client.factory import UserFactory
from mockapi_client.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture(scope="module")
def api_client():
    with UsersApiClient() as client:
        yield client


@pytest.fixture
def user_factory():
    factory = UserFactory()
    yield factory
    # After the test finishes, clear the used names set
    factory.reset()
    logger.debug("UserFactory memory cleared")


@pytest.fixture(scope="module")
def cleanup_registry(api_client):
    user_ids = []
    yield user_ids

    print("\n")
    logger.info("-" * 60)
    logger.info(f"Final Teardown: Deleting {len(user_ids)} users")

    failed_deletions = []

    for user_id in user_ids:
        logger.debug(f"Deleting user {user_id}...")
        api_client.delete_user(user_id)

        if api_client.wait_until_deleted(user_id):
            logger.debug(f"Successfully verified deletion of user {user_id}")
        else:
            logger.error(f"Timeout verifying deletion for user: {user_id}")
            failed_deletions.append(user_id)

    assert not failed_deletions, f"Teardown failed for users: {failed_deletions}"

    logger.info("Cleanup completed successfully.")
    logger.info("-" * 60)


@pytest.fixture(autouse=True)
def separator():
    # This runs before every test function in the project
    print("\n")
    yield
