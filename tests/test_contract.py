import pytest
from core.normalizers import normalize_users
from core.validators import validate_users, ValidationError


def test_users_contract():
    raw_users = [
        {"id": 1, "email": "Test@Email.com", "first_name": "John", "last_name": "Doe"},
        {"id": 2, "email": "invalid_email.com"},
        {"id": None, "first_name": "Alice"},
        "not_a_dict",
        {},
    ]

    normalized_users = normalize_users(raw_users)

    valid = [u for u in normalized_users if u["id"] == "1"]
    invalid = [u for u in normalized_users if u["id"] != "1"]

    # Valid users pass
    validate_users(valid)

    # Invalid users fail
    for user in invalid:
        with pytest.raises(ValidationError):
            validate_users([user])
