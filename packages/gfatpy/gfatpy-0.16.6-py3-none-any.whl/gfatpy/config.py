import sys
from typing import Literal

from loguru import logger


def set_logger_level(
    level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
) -> None:
    logger.remove()
    logger.add(sys.stderr, level=level)
