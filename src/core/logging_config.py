import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    """Configure the logging system."""
    logger = logging.getLogger('NFCApp')
    logger.setLevel(logging.INFO)

    # Use user's AppData folder for logs
    appdata_dir = os.path.join(os.environ.get("APPDATA", os.getcwd()), "ElixionNiviu", "logs")
    os.makedirs(appdata_dir, exist_ok=True)

    log_path = os.path.join(appdata_dir, "nfc_app.log")

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,  # 1MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
