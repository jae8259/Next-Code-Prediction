import logging
import os
from datetime import datetime

def setup_logging():
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
    logger = setup_logging()
    logger.info("This is a test log message from logger.py")
