import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from os import path, name as os_name
import json
from time import sleep
import re
from pprint import pformat
from src.logging import logger
from src.config import config
from src.scraping.scrapy.custom_scrapy_settings import custom_settings


# mode = config['mode']
executable_path = path.join(path.dirname(__file__), f"../selenium/chromedriver.exe") if os_name == 'nt' \
	else "/usr/bin/chromedriver"


class TemplateSelSpider(scrapy.Spider):
	custom_settings = custom_settings
	name = "TemplateSelSpider"
	start_urls = [
		'https://www.google.com',
	]
	user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"

	def __init__(self, **kwargs):
		# instantiating chrome selenium driver, start urls feature an 'infinite scroll'
		# behavior that needs to be triggered to view all listed shoes
		self.store = kwargs.get('store', {})
		chrome_options = webdriver.ChromeOptions()
		chrome_options.headless = True
		chrome_options.add_argument("--log-level=2")
		chrome_options.add_argument("--–disable-notifications")
		chrome_options.add_argument("--disable-dev-shm-usage")
		chrome_options.add_argument(f'--user-agent={TemplateSelSpider.user_agent}')
		chrome_options.add_argument("test-type")
		self.driver = webdriver.Chrome(
			executable_path=executable_path,
			options=chrome_options
		)
		logger.info(f'{TemplateSelSpider.name} init ...')
		super().__init__()

	def start_requests(self):
		for url in TemplateSelSpider.start_urls:
			request = scrapy.Request(
				url,
				callback=self.parse,
			)
			request.meta['max_proxies_to_try'] = 150
			yield request

	def parse(self, response):
		logger.info(f'parsed url {response.url}')
		self.driver.get(response.url)
		self.driver.implicitly_wait(3)

	def __del__(self):
		self.driver.close()

	@staticmethod
	def closed(reason):
		logger.warning(f'{TemplateSelSpider.name} spider closed:{reason}')


def test_scrape():
	"""
	launches stadiumgoods spider on its own for testing
	"""
	process = CrawlerProcess(custom_settings)
	kwargs = {}
	process.crawl(TemplateSelSpider, kwargs=kwargs)
	process.start()


if __name__ == '__main__':
	test_scrape()
