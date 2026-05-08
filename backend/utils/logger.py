import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Ensure a logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Default log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger with the specified name.
    Logs to both console and a rotating file.
    """
    logger = logging.getLogger(name)
    
    # Only configure if no handlers exist to avoid duplicate logs in case of multiple imports
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (Rotating: max 5MB per file, keep 3 backups)
        file_path = os.path.join(LOG_DIR, "app.log")
        file_handler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
