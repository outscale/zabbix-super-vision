import logging

# Logger Configuration
stdio_handler = logging.StreamHandler()
stdio_handler.setLevel(logging.INFO)
logger = logging.getLogger("aiohttp.access")
logger.addHandler(stdio_handler)
logger.setLevel(logging.INFO)
