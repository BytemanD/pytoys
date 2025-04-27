import sys
from loguru import logger

def setup_logger(level="INFO", file=None):
    """Setup logging configuration."""
    logger.remove()
    logger.add(
        file if file else sys.stdout,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} "
               "<level>{level: <7}</level> "
               "<level>{message}</level>",
    )
