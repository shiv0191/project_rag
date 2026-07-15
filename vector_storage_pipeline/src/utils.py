import hashlib
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate the SHA-256 checksum of a file.

    Args:
        file_path:
            Path to the file.

    Returns:
        Hexadecimal SHA-256 hash.

    Raises:
        FileNotFoundError:
            If the file does not exist.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    logger.info(
        "Calculating SHA-256 for %s",
        file_path
    )

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(8192)

            if not chunk:
                break

            sha256.update(chunk)

    checksum = sha256.hexdigest()

    logger.info(
        "SHA-256 calculated successfully."
    )

    return checksum


def ensure_directory(directory: Path) -> None:
    """
    Create a directory if it does not already exist.

    Args:
        directory:
            Directory path.
    """

    directory.mkdir(
        parents=True,
        exist_ok=True
    )


def file_size(file_path: Path) -> int:
    """
    Return file size in bytes.

    Args:
        file_path:
            Path to the file.

    Returns:
        File size in bytes.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return file_path.stat().st_size


def file_exists(file_path: Path) -> bool:
    """
    Check whether a file exists.

    Args:
        file_path:
            Path to the file.

    Returns:
        True if file exists.
    """

    return file_path.exists()