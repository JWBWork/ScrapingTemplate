from src.logging import logger
from scrapy.crawler import CrawlerProcess, CrawlerRunner
import datetime
import os
import pytz
# from memory_profiler import profile

from src import spiders, update_proxies, custom_settings, config


class Store:
	pass


# @profile
def main():
	'''
	Starts harvest script
	'''
	logger.info('launching main')
	# tz = pytz.timezone('America/Los_Angeles')
	tz = pytz.timezone('EST')
	start = datetime.datetime.now(tz=tz)

	if config['use_proxy']:
		update_proxies()

	# launching crawlers
	store = Store()
	process = CrawlerProcess(custom_settings)
	for spider in spiders:
		logger.info(f'starting {spider.name}')
		process.crawl(spider, store=store)
	process.start()
	process.join()

	end = datetime.datetime.now(tz=tz)
	logger.info(f"runtime: {end - start}")


if __name__ == '__main__':
	main()
