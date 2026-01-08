from typing import List, Dict
from core.normalizers import normalize_users  # reuse normalization


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_user_email(user: dict) -> None:
    """
    Validates that the user dictionary has a valid email.

    Rules:
    - 'email' field must exist and be a non-empty string
    - Must contain '@'
    """
    email = user.get("email")
    if not isinstance(email, str) or not email.strip():
        raise ValidationError(f"User {user.get('id')} has missing or empty email.")
    if "@" not in email:
        raise ValidationError(f"User {user.get('id')} has invalid email format: {email}")


def validate_users(users: List[Dict]) -> None:
    """
    Validate a list of user dictionaries.

    - Skips invalid items (non-dict)
    - Validates each user using existing rules
    - Raises ValidationError on first failure
    """

    normalized = normalize_users(users)

    for user in normalized:
        # Validate individual fields
        validate_user_email(user)
        # We can later add more validators, e.g., validate_user_name(user), validate_user_id(user)
