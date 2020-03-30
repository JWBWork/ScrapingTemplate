"""
Module to define logging behavior with preferred logging library
"""
from loguru import logger
import logging
from scrapy.utils.log import configure_logging


class InterceptHandler(logging.Handler):
	def emit(self, record):
		# Get corresponding Loguru level if it exists
		try:
			level = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		# Find caller from where originated the logged message
		frame, depth = logging.currentframe(), 2
		while frame.f_code.co_filename == logging.__file__:
			frame = frame.f_back
			depth += 1

		logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

configure_logging(install_root_handler=False)
logging.basicConfig(handlers=[InterceptHandler()], level=0)
logger.add('logs/log.txt', rotation='5 MB')