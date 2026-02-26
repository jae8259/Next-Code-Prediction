import logging
import os
from datetime import datetime

def setup_logging(enable_logging: bool = True):
    if not enable_logging:
        # Disable all logging
        logging.getLogger().setLevel(logging.CRITICAL)
        # Remove any existing handlers to prevent output
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
        return

    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    timestamp = datetime.now().strftime("%y_%m_%d_%H_%M")
    log_filename = os.path.join(log_directory, f"{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging configured. Log file: {log_filename}")

    return logging.getLogger(__name__)

if __name__ == "__main__":
    # Test case for when logging is enabled
    logger_enabled = setup_logging(enable_logging=True)
    logger_enabled.info("This is a test log message from logger.py with logging ENABLED.")

    # Test case for when logging is disabled
    logger_disabled = setup_logging(enable_logging=False)
    logger_disabled.info("This is a test log message from logger.py with logging DISABLED. (Should not appear)")
