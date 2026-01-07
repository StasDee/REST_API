import logging
import colorlog
from time import sleep
from mockapi_client.client import UsersApiClient
from mockapi_client.factory import UserFactory

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(levelname)s] %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)
handler.setFormatter(formatter)

logger = colorlog.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
# Silence noisy library logs: utllib3 and requests
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


def user_scenario(
        api: UsersApiClient,
        factory: UserFactory,
        count: int = 5
):
    """
    Orchestrates the lifecycle for multiple users.
    """
    created_ids = []

    # 1. CREATE & VERIFY (GET)
    logger.info("-" * 50)
    logger.info(f"--- Step 1: Creating and verifying {count} users ---")
    for _ in range(count):
        logger.info("-" * 50)
        payload = factory.create_user_payload()
        logger.info(f"Generated payload for user: {payload}")

        # POST
        created = api.create_user(payload)
        user_id = created["id"]
        created_ids.append(user_id)
        logger.info(f"Created user: {payload['name']} (ID: {user_id})")

        # GET
        fetched = api.get_user(user_id)
        logger.info(f"Fetched user: {fetched}")
        assert fetched and fetched["name"] == payload["name"], f"Verification failed for {user_id}"
        logger.info(f"Creation - Fetching success")
    logger.info("-" * 50)
    logger.info("All users successfully created and verified.")
    logger.info("-" * 50)

    # 2. PATCH (Partial Update)
    if created_ids:
        target_id = created_ids[0]
        logger.info(f"--- Step 2: Patching user {target_id} ---")
        patch_data = {"name": "renamed_user"}
        patched = api.patch_user(target_id, patch_data)
        assert patched["name"] == "renamed_user", f"Rename user: {created_ids[0]} to renamed_user failed"
        logger.info(f"Patched user: {patched}")
        logger.info(f"User {target_id} successfully renamed to name: renamed_user")

    # 3. DELETE (Cleanup)
    logger.info("-" * 50)
    logger.info("--- Step 3: Deleting all users ---")
    for user_id in created_ids:
        logger.debug(f"Deleting user {user_id}...")
        api.delete_user(user_id)
        # Pause to help mockapi process the deletion
        sleep(0.5)

    # 4. FINAL VERIFICATION (Polling)
    logger.info("-" * 50)
    logger.info("--- Step 4: Final verification ---")
    # We use a loop here because MockAPI is eventually consistent
    for attempt in range(5):
        remaining = api.list_users()
        if not remaining:
            logger.info("Cleanup verified: No users remaining.")
            logger.info("-" * 50)
            return
        logger.warning(f"Cleanup check {attempt + 1}: {len(remaining)} users still exist. Retrying...")
        sleep(2)
    logger.info("-" * 50)
    raise RuntimeError("Cleanup failed: Users still present in the system.")


def main():
    factory = UserFactory()

    # We use the context manager (with) to ensure the session closes properly
    with UsersApiClient() as api:
        try:
            user_scenario(api, factory, count=5)  # Restored the '5' users logic
            logging.info("Task completed successfully!")
        except Exception as e:
            logging.error(f"Scenario failed: {e}")


if __name__ == "__main__":
    main()
