from concurrent.futures import ThreadPoolExecutor, as_completed
from mockapi_client.logger import get_logger
import pytest

logger = get_logger(__name__)

@pytest.mark.contract
def test_concurrent_user_creation(api_client, user_factory, cleanup_registry):
    """
    Creates 10 users in parallel using threads.
    """
    logger.info("-" * 60)
    logger.info("Starting thread-based concurrent user creation test")

    def create_user_task(index):
        payload = user_factory.create_user_payload()
        logger.info(f"[Thread {index}] Payload: {payload}")
        created = api_client.create_user(payload)
        cleanup_registry.append(created["id"])
        return created

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_user_task, i) for i in range(10)]
        for future in as_completed(futures):
            user = future.result()
            logger.info(f"User created: {user}")
            results.append(user)

    logger.info(f"All users created: {results}")
    assert len(results) == 10
    assert all("id" in u for u in results)
