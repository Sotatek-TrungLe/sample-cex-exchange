import logging
import sys

# Configure the logger
logger = logging.getLogger("balance_service")
logger.setLevel(logging.DEBUG)

# Stream handler to output logs to stdout (for Docker logs)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# Log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(stream_handler)
