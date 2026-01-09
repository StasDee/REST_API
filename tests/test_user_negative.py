from mockapi_client.logger import get_logger
import pytest

logger = get_logger(__name__)


# -------------------------
# Negative / Edge-Case Tests
# -------------------------

@pytest.mark.contract
@pytest.mark.parametrize(
    "payload",
    [
        {"email": "invalid_email"},  # Invalid email format
        {"first_name": "Alice"},  # Missing email
        {},  # All required fields missing
    ],
)
def test_user_creation_negative(api_client, payload):
    """
    Verify that creating users with invalid payloads fails as expected.
    """
    logger.info("-" * 60)
    logger.info(f"Testing negative user creation with payload: {payload}")

    with pytest.raises(ValueError) as e:
        api_client.create_user(payload)

    logger.info(f"Expected validation error caught: {e.value}")


@pytest.mark.contract
def test_fetch_nonexistent_user(api_client):
    """
    Fetching a user ID that doesn't exist should raise a 404 error.
    """
    non_existent_id = "999999"
    logger.info("-" * 60)
    logger.info(f"Testing fetch of non-existent user ID: {non_existent_id}")

    with pytest.raises(Exception) as e:
        api_client.get_user(non_existent_id)

    logger.info(f"Expected 404 error received: {e.value}")
    assert "404" in str(e.value)


@pytest.mark.contract
def test_patch_user_invalid_data(api_client, user_factory, cleanup_registry):
    """
    Attempt to patch an existing user with invalid data.
    """
    logger.info("-" * 60)
    logger.info("Creating valid user to test invalid patch")

    # Create a valid user first
    payload = user_factory.create_user_payload()
    created = api_client.create_user(payload)
    user_id = created["id"]
    cleanup_registry.append(user_id)

    logger.info(f"User created for patch test: {created}")

    # Attempt invalid patch
    invalid_patch = {"email": "invalid_email"}
    logger.info(f"Attempting invalid patch: {invalid_patch} on user {user_id}")

    with pytest.raises(ValueError) as e:
        api_client.patch_user(user_id, invalid_patch)

    logger.info(f"Expected validation error caught: {e.value}")
