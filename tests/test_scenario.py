from core.normalizers import normalize_users
from core.validators import validate_users


def test_create_and_fetch_user_scenario(mockapi_client):
    """
    End-to-end user lifecycle scenario:

    1. Create user
    2. Fetch user
    3. Normalize response
    4. Validate contract
    """

    # Step 1: create user
    created_user = mockapi_client.create_user(
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "John.Doe@Example.com",
        }
    )

    assert created_user is not None
    assert "id" in created_user

    # Step 2: fetch user
    fetched_user = mockapi_client.get_user(created_user["id"])
    assert fetched_user is not None

    # Step 3: normalize
    normalized_users = normalize_users([fetched_user])

    # Step 4: validate
    validate_users(normalized_users)
