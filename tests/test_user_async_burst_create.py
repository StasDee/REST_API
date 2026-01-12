import pytest
import asyncio
import random
import string
from mockapi_client.logger import get_logger
import uuid

logger = get_logger(__name__)

pytestmark = pytest.mark.asyncio


def random_string(length: int = 6) -> str:
    """Generate a random string for unique emails and names."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_user_payload() -> dict:
    uid = str(uuid.uuid4())
    return {
        "id": uid,  # optional if server auto-generates
        "name": f"User_{uid[:6]}",
        "email": f"user_{uid[:6]}@example.com",
    }


@pytest.mark.contract
@pytest.mark.asyncio
async def test_user_burst_unique_ids(async_api_client, register_async_user):
    """
    Burst test: create 20 random users concurrently and register them locally.

    Steps:
    1. Generate 20 random user payloads with unique emails.
    2. Send all creation requests concurrently.
    3. Register each successfully created user with `register_async_user`.
    4. Print all successfully created users and failures.
    5. Fail the test if no users were created.
    6. Check that all returned IDs are unique (no duplicates).
    """
    num_users = 20
    payloads = [generate_user_payload() for _ in range(num_users)]

    async def create_and_register_user(payload):
        try:
            user = await async_api_client.create_user(payload)
            # Register the created user in test context
            await register_async_user(user["id"])
            return user
        except Exception as e:
            return e

    # Fire all requests concurrently
    results = await asyncio.gather(*(create_and_register_user(p) for p in payloads))

    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    logger.info(f"\nCreated users ({len(successes)}):")
    for u in successes:
        logger.info(u)

    logger.warning(f"\nFailures ({len(failures)}):")
    for f in failures:
        logger.warning(f)

    # Fail if nothing was created
    assert successes, "All user creation requests failed!"

    # Basic field checks
    for user in successes:
        assert "id" in user
        assert "name" in user
        assert "email" in user

    # Check all users have unique IDs
    ids = [u["id"] for u in results]
    duplicates = set([id for id in ids if ids.count(id) > 1])
    if duplicates:
        logger.error(f"Duplicate user IDs detected: {duplicates}")
        pytest.fail(f"Duplicate user IDs detected: {duplicates}")
    else:
        logger.info("✓ All user IDs are unique")

    # Sanity check that all have 'id' key
    assert all("id" in u for u in results)
