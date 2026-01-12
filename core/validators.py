from mockapi_client.logger import get_logger
from typing import List, Dict

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_user_id(user: dict) -> None:
    """
    Validates that the user dictionary contains a valid unique identifier.

    Raises:
        ValidationError: If 'id' is missing, not a string, or contains only whitespace.
    """
    user_id = user.get("id")
    logger.debug(f"Validating user_id: {user_id}")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValidationError("User id must be a non-empty string")


def validate_user_name(user: dict) -> None:
    """
    Validates the 'name' field of a user dictionary.

    The name is considered an optional field, but if present, it must
    adhere to string format rules.

    Raises:
        ValidationError: If 'name' is provided but is not a non-empty string.
    """
    name = user.get("name")
    logger.debug(f"Validating user_name: {name}")

    if name is None:
        return  # name is optional

    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Name must be a non-empty string if provided")


def validate_user_email(user: dict) -> None:
    """
    Performs integrity and format checks on the user's email address.

    Validation logic:
    1. Ensures the 'email' key exists and is a non-empty string.
    2. Performs a pragmatic format check (presence of '@' and a domain dot).

    Raises:
        ValidationError: If the email is missing, malformed, or the wrong type.
    """
    user_id = user.get("id", "Unknown ID")
    email = user.get("email")
    logger.debug(f"Validating user_email: {email}")

    # 1. Type and Empty Check
    if not isinstance(email, str) or not email.strip():
        raise ValidationError(f"User [{user_id}]: Email is missing or not a string.")

    # 2. Basic Format Check (Pragmatic approach)
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValidationError(f"User [{user_id}]: Invalid email format '{email}'.")


def validate_users(users: list[dict]) -> None:
    """
    Iterates through a list of user dictionaries and triggers individual
    field validations for each.

    This acts as the primary entry point for batch validation before
    processing API data.

    Raises:
        ValidationError: If the payload is not a list, if any item is not
                         a dictionary, or if any specific user field fails validation.
    """
    if not isinstance(users, list):
        raise ValidationError("Users payload must be a list")

    for user in users:
        if not isinstance(user, dict):
            raise ValidationError("Each user must be a dict")

        logger.debug(f"Validating user: {user}")
        validate_user_id(user)
        validate_user_email(user)
        validate_user_name(user)