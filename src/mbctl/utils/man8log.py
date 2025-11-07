import logging

# Configure basic formatting for the root handlers but do not force the root level here.
logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s")

# Module logger used across the project. Default to INFO so messages appear by default.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
