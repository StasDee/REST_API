from typing import List, Dict, Optional


def normalize_user(raw_user: dict) -> dict:
    user_id = raw_user.get("id")
    email = raw_user.get("email")

    name = raw_user.get("name")
    if not name:
        first_name = raw_user.get("first_name")
        last_name = raw_user.get("last_name")

        if first_name and last_name:
            name = f"{first_name} {last_name}"
        else:
            name = first_name or last_name

    return {
        "id": str(user_id) if user_id is not None else None,
        "email": email.lower() if isinstance(email, str) else None,
        "name": name,
    }


from typing import List, Dict, Optional


def normalize_users(raw_users: list) -> list[dict]:
    if not isinstance(raw_users, list):
        return []

    return [
        normalize_user(user)
        for user in raw_users
        if isinstance(user, dict)
    ]
