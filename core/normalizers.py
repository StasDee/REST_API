from typing import List, Dict, Optional


def normalize_user(raw_user: dict) -> dict:
    """
    Normalize raw API user data into a stable internal representation.

    Rules:
    - Missing optional fields → None
    - Extra fields → ignored
    - 'id' always str
    - 'email' lowercase
    - 'name' constructed from first_name + last_name if missing
    """
    user_id = raw_user.get("id")
    email = raw_user.get("email")
    name = raw_user.get("name")

    first_name = raw_user.get("first_name")
    last_name = raw_user.get("last_name")

    if name is None:
        if first_name and last_name:
            name = f"{first_name} {last_name}"
        elif first_name:
            name = first_name
        elif last_name:
            name = last_name
        else:
            name = None

    return {
        "id": str(user_id) if user_id is not None else None,
        "email": email.lower() if isinstance(email, str) else None,
        "name": name
    }


from typing import List, Dict, Optional


def normalize_users(raw_users: List[Dict]) -> List[Dict]:
    """
    Normalize a list of raw API users.

    - Ignores items that are not dictionaries
    - Skips entries where all fields are missing
    - Preserves original order
    """
    normalized_list = []

    for raw_user in raw_users:
        # Skip non-dict entries
        if not isinstance(raw_user, dict):
            continue

        # Normalize individual user
        user = normalize_user(raw_user)

        # Skip completely empty users (all fields None)
        if all(value is None for value in user.values()):
            continue

        normalized_list.append(user)

    return normalized_list
