import logging
from logging.handlers import RotatingFileHandler
import os

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# File handler for errors (and above) with rotation
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

error_file_handler = RotatingFileHandler(
    filename=os.path.join(log_directory, 'error.log'),
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=5
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(error_file_handler)

# Optionally, you can disable propagation to prevent double logging if this logger is a child of another logger
logger.propagate = False