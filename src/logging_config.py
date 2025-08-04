import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    """Configure the logging system."""
    logger = logging.getLogger('NFCApp')
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # File handler with rotation (1MB per file, max 3 backups)
    file_handler = RotatingFileHandler(
        'logs/nfc_app.log',
        maxBytes=1_000_000,  # 1MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Add handler to logger (avoid duplicate handlers)
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger