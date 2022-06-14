import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def get_logger(name: str) -> logging.Logger:
    """return the logger instance"""

    level = logging.DEBUG if eval(os.getenv('DEBUG', False)) else logging.INFO

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    timed_handler = TimedRotatingFileHandler(
        filename='image-compressor.log',
        when='W6',
        interval=1,
        backupCount=12,
        encoding='utf-8',
        delay=False,
    )

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s in %(pathname)s:%(lineno)d'
    )
    timed_handler.setFormatter(formatter)

    logger.addHandler(timed_handler)
    logger.setLevel(level)

    return logger
