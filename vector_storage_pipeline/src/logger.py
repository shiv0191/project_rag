import logging
from pathlib import Path

from src.config import settings


def setup_logger() -> None:
    """
    Configure application logging.

    Logs are written to both:

    - Console
    - Log file

    This function should be called once during
    application startup.
    """

    log_directory = settings.LOG_DIR

    log_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    log_file = settings.LOG_FILE

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    #
    # Prevent duplicate handlers
    #

    if root_logger.handlers:
        root_logger.handlers.clear()

    #
    # File Handler
    #

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)

    file_handler.setFormatter(formatter)

    #
    # Console Handler
    #

    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)

    console_handler.setFormatter(formatter)

    #
    # Register handlers
    #

    root_logger.addHandler(file_handler)

    root_logger.addHandler(console_handler)

    logging.info(
        "Logger initialized successfully."
    )