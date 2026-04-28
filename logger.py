import logging
import os
from logging.handlers import TimedRotatingFileHandler

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("quantsense")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = TimedRotatingFileHandler(
        filename="logs/quantsense.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Silence noisy libraries
logging.getLogger("yfinance").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)