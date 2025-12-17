import os

import structlog
import yoyo

from app.config import settings


def apply_db_migrations(mode: str = "apply"):
    logger = structlog.get_logger()
    logger.info(f"Running Yoyo Migrations: {mode.upper()}")

    # Connect to the database and find migration files
    backend = yoyo.get_backend(
        f"postgresql://{settings.app_db_user}:{settings.app_db_password}@{settings.app_db_host}:{settings.app_db_port}/{settings.app_db_database}"
    )
    migrations = yoyo.read_migrations(
        os.path.join(os.path.dirname(__file__), "scripts")
    )

    # Select the action based on the mode
    if mode == "apply":
        # Apply all outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))
        logger.info("Migrations applied successfully.")
    elif mode == "rollback":
        # Roll back the last applied migration
        backend.rollback_migrations(backend.to_rollback(migrations))
        logger.info("Last migration rolled back.")
    else:
        logger.error("Invalid mode. Use 'apply' or 'rollback'.")
