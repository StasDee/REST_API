from mockapi_client.logger import get_logger
import pytest
from core.normalizers import normalize_users
from core.validators import validate_users, ValidationError

logger = get_logger(__name__)


def test_users_contract_workflow():
    """
    Integration test for the normalization and validation pipeline.

    Verifies that:
    1. Valid raw data is normalized and passes validation.
    2. Invalid/malformed data is handled gracefully and fails validation.
    """
    raw_users = [
        {"id": 1, "email": "Test@Email.com", "first_name": "John", "last_name": "Doe"},  # Valid (after normalization)
        {"id": 2, "email": "invalid_email.com"},  # Invalid email format
        {"id": None, "first_name": "Alice"},  # Invalid ID
        "not_a_dict",  # Invalid type
        {},  # Missing required fields
    ]

    # Step 1: Normalize raw data (converts IDs to strings, handles missing keys)
    normalized_users = normalize_users(raw_users)
    logger.debug(f"Normalized users: {normalized_users}")

    # Step 2: Test Positive Case
    # Expecting 'id': 1 to become 'id': '1' and 'email' to be lowercase
    valid_users = [u for u in normalized_users if u.get("id") == "1"]
    assert len(valid_users) == 1, "Should have exactly one valid user after normalization"

    logger.info("Running positive validation for user ID 1")
    validate_users(valid_users)

    # Step 3: Test Negative Cases
    # Every other user should trigger a ValidationError
    invalid_users = [u for u in normalized_users if u.get("id") != "1"]

    for user in invalid_users:
        logger.info(f"Checking expected failure for: {user}")
        with pytest.raises(ValidationError) as excinfo:
            validate_users([user])
        logger.debug(f"Caught expected error: {excinfo.value}")


@pytest.mark.parametrize("invalid_input", [
    [{"id": "2", "email": "no_at_sign.com"}],  # Bad format
    [{"id": "3", "email": ""}],  # Empty email
    [{"id": " ", "email": "test@test.com"}],  # Whitespace ID
    "not_a_list"  # Wrong root type
])
def test_validation_edge_cases(invalid_input):
    """Specific edge cases for the validator using parametrization."""
    with pytest.raises(ValidationError):
        validate_users(invalid_input)
