import re
from typing import List, Dict
from core.normalizers import normalize_users  # reuse normalization

# EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_user_id(user: dict) -> None:
    user_id = user.get("id")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValidationError("User id must be a non-empty string")


def validate_user_email(user: dict) -> None:
    email = user.get("email")
    if not email or not isinstance(email, str):
        raise ValidationError("Email is missing or not a string")

    if not EMAIL_REGEX.match(email):
        raise ValidationError(f"Invalid email format: {email}")


def validate_user_name(user: dict) -> None:
    name = user.get("name")

    if name is None:
        return  # name is optional

    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Name must be a non-empty string if provided")


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


def validate_users(users: list[dict]) -> None:
    if not isinstance(users, list):
        raise ValidationError("Users payload must be a list")

    for user in users:
        if not isinstance(user, dict):
            raise ValidationError("Each user must be a dict")

        validate_user_id(user)
        validate_user_email(user)
        validate_user_name(user)
