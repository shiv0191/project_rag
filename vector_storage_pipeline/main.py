import logging
import sys

from src.logger import setup_logger
from src.pipeline import StoragePipeline

logger = logging.getLogger(__name__)


def main() -> int:
    """
    Entry point for the Vector Storage Pipeline.
    """

    setup_logger()

    logger.info("=" * 80)
    logger.info("Vector Storage Pipeline Started")
    logger.info("=" * 80)

    try:

        pipeline = StoragePipeline()

        pipeline.run()

        logger.info("=" * 80)
        logger.info("Vector Storage Pipeline Finished Successfully")
        logger.info("=" * 80)

        return 0

    except KeyboardInterrupt:

        logger.warning(
            "Pipeline interrupted by user."
        )

        return 1

    except Exception:

        logger.exception(
            "Pipeline execution failed."
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())
