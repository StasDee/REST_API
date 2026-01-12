from mockapi_client.logger import get_logger
import pytest
from requests.exceptions import HTTPError

logger = get_logger(__name__)


# -------------------------
# Negative / Edge - Case
# Tests
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
def test_user_creation_negative(api_client, payload, register_sync_user):
    """
    Expectation: API should fail with 4xx for invalid payloads.
    Reality: Log the actual response if API does not behave as expected.
    """
    logger.info("-" * 60)
    logger.info(f"Testing negative user creation with payload: {payload}")

    try:
        user = api_client.create_user(payload)

        # Register for cleanup
        user_id = user["id"]
        register_sync_user(user_id)
        logger.info(f"User {user_id} registered for later cleanup.")
    except HTTPError as exc:
        # ✅ API returned expected failure
        response = exc.response
        logger.info(
            f"Expected failure caught: status={response.status_code}, body={response.text}"
        )
        assert response.status_code in (400, 422)
    else:
        # API unexpectedly succeeded — log and fail
        logger.error(
            f"Expected HTTPError, but API returned successfully! "
            f"Returned object: {user}"
        )
        pytest.fail(
            f"Expected HTTPError for payload {payload}, "
            f"but API returned: {user}"
        )


logger = get_logger(__name__)


@pytest.mark.contract
def test_fetch_nonexistent_user(api_client):
    """
    Fetching a non-existent user:
    - Expectation: 404 Not Found
    - Reality: API may sometimes return 500 Internal Server Error
    - Logs expected vs actual outcome.
    """
    non_existent_id = "999999"
    logger.info("-" * 60)
    logger.info(f"Testing fetch of non-existent user ID: {non_existent_id}")

    try:
        api_client.get_user(non_existent_id)
        # If we reach here, no exception was raised - that's also wrong
        logger.error("CONTRACT VIOLATION: No error raised for non-existent user")
        pytest.fail(
            f"Expected HTTPError (404) for non-existent user {non_existent_id}, "
            f"but request succeeded without error"
        )
    except HTTPError as exc:
        # Extract status and body
        if hasattr(exc, "response") and exc.response is not None:
            status = exc.response.status_code
            body = exc.response.text
        else:
            status = "no response"
            body = str(exc)
            import re
            m = re.search(r"(\d{3}) .*? for url", body)
            if m:
                status = int(m.group(1))

        # Senior-level logging: document the contract
        logger.info("=" * 60)
        logger.info("API CONTRACT CHECK: Non-existent User")
        logger.info("=" * 60)
        logger.info(f"Expected Status Code: 404 (Not Found)")
        logger.info(f"Actual Status Code:   {status}")
        logger.info(f"Response Body:        {body}")
        logger.info("=" * 60)

        # Evaluate contract compliance
        if status == 404:
            logger.info("✓ CONTRACT COMPLIANT: API correctly returned 404")
        else:
            logger.error("✗ CONTRACT VIOLATION: API returned wrong status code")
            logger.error(f"  Expected: 404 Not Found")
            logger.error(f"  Received: {status}")
            logger.error(f"  Details:  {body}")
            pytest.fail(
                f"API Contract Violation: Expected 404 for non-existent user {non_existent_id}, "
                f"but received {status}. Response: {body}"
            )


@pytest.mark.contract
def test_patch_user_invalid_data(api_client, user_factory, register_sync_user):
    """
    Attempt to patch an existing user with invalid data (e.g., invalid email) to test server validation.
    Expected: server rejects invalid data with 4xx (400/422). Logs expected vs actual results.
    """
    logger.info("-" * 60)
    logger.info("Creating valid user to test invalid patch")

    # Step 1: create a valid user
    payload = user_factory.create_user_payload()
    created = api_client.create_user(payload)
    user_id = created["id"]
    register_sync_user(user_id)
    logger.info(f"User created for patch test: {created}")

    # Step 2: attempt invalid patch
    invalid_patch = {"email": "invalid_email"}
    logger.info(f"Attempting invalid patch: {invalid_patch} on user {user_id}")

    try:
        response = api_client.patch_user(user_id, invalid_patch)
    except HTTPError as exc:
        # Catch server-side errors (5xx)
        status = getattr(exc.response, "status_code", "no response")
        body = getattr(exc.response, "text", str(exc))
        logger.error(
            f"HTTP error caught during invalid patch: expected 4xx, got {status}. Response body: {body}"
        )
        pytest.fail(f"Server error during patch for user {user_id}: {status}. Body: {body}")

    # Step 3: inspect server response
    patched_email = response.get("email")
    if patched_email == invalid_patch["email"]:
        # Server accepted invalid email — fail test, log info
        logger.error(
            f"Server accepted invalid data! Expected rejection, but email was set to: {patched_email}"
        )
        pytest.fail(
            f"Invalid patch accepted by server for user {user_id}. "
            f"Sent: {invalid_patch}, Got: {patched_email}"
        )
    else:
        # Server rejected or sanitized invalid data
        logger.info(f"Server correctly handled invalid patch: {response}")
