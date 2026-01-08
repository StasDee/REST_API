from mockapi_client.logger import get_logger
import pytest

logger = get_logger(__name__)


@pytest.mark.contract
@pytest.mark.parametrize("index", range(5))
def test_user_crud_lifecycle(
        api_client,
        user_factory,
        cleanup_registry,
        index
):
    """
    Verifies CRUD. Users are registered in cleanup_registry,
    will be deleted all at once at the end of the module.
    """
    logger.info("-" * 60)
    logger.info(f"--- User {index} ---")

    # Create payload
    payload = user_factory.create_user_payload()
    logger.info(f"Payload created: {payload}")

    # Create user
    created = api_client.create_user(payload)
    user_id = created["id"]
    logger.info(f"User: {user_id} created: {created}")

    # Register user ID in the cleanup registry
    cleanup_registry.append(user_id)

    logger.info(f"User: {user_id} registered for later cleanup.")

    # Verify user
    fetched = api_client.get_user(user_id)
    logger.info(f"User: {user_id} fetched: {fetched}")
    assert fetched["name"] == payload["name"]

    # Patch user
    patched = api_client.patch_user(user_id, {"name": f"renamed_{index}"})
    logger.info(f"User: {user_id} patched: {patched}")
    assert patched["name"] == f"renamed_{index}", (f"Expected name to be renamed_{index}"
                                                   f" but got {patched['name']}")
