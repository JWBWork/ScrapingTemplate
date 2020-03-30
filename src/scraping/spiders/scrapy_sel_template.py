import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from os import path, name as os_name
import json
from time import sleep
import re
from pprint import pformat
from src.logging import logger
import pandas as pd
from src.config import config
from datetime import datetime
from src.scraping.scrapy.custom_scrapy_settings import custom_settings
from src.scraping import proxies
from src import config, project_path

# mode = config['mode']
executable_path = path.join(path.dirname(__file__), f"../selenium/chromedriver.exe") if os_name == 'nt' \
	else "/usr/bin/chromedriver"


def get_driver():
	chrome_options = webdriver.ChromeOptions()
	chrome_options.headless = True
	chrome_options.add_argument("--log-level=2")
	chrome_options.add_argument("--–disable-notifications")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument(f'--user-agent={TemplateSelSpider.user_agent}')
	chrome_options.add_argument("test-type")
	driver = webdriver.Chrome(
		executable_path=executable_path,
		options=chrome_options
	)
	return driver


class TemplateSelSpider(scrapy.Spider):
	custom_settings = custom_settings
	name = "TemplateSelSpider"
	start_urls = [
		'https://www.google.com',
	]
	# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"

	def __init__(self, **kwargs):
		# instantiating chrome selenium driver, start urls feature an 'infinite scroll'
		# behavior that needs to be triggered to view all listed shoes
		self.store = kwargs.get('store', pd.DataFrame())
		self.file_path = kwargs.get(
			'file_path',
			path.join(project_path, f"results/{self.__class__.__name__}-{datetime.now().strftime('%y-%m-%d-%H-%M')}")
		)
		if kwargs.get('use_selenium'):
			self.driver = get_driver()
		logger.info(
			f'{TemplateSelSpider.name} init, store: {self.store}, file_path: {self.file_path}'
		)
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
		# SELENIUM DRIVER
		# self.driver.get(response.url)
		# self.driver.implicitly_wait(3)
		#Append data
		self.store = self.store.append({'c': 0, 'd': 2}, ignore_index=True)

	def __del__(self):
		self.store.to_csv(self.file_path, index=False)
		if hasattr(self, 'driver'):
			self.driver.close()

	@staticmethod
	def closed(reason):
		logger.warning(f'{TemplateSelSpider.name} spider closed:{reason}')


def start_scrape():
	if config['use_proxy']:
		proxies.update_proxies()

	file_name = 'Template.csv'
	file_path = path.join(path.dirname(__file__), f'{project_path}/results/{file_name}')

	try:
		store = pd.read_csv(file_path)
	except Exception as e:
		logger.warning(f'Could not load store, {e}')
		store = pd.DataFrame()
	process = CrawlerProcess(custom_settings)
	kwargs = {
		'file_name': 'template.csv',
		'file_path': file_path,
		'store': store,
		'use_selenium': False
	}
	process.crawl(TemplateSelSpider, **kwargs)
	process.start()


if __name__ == '__main__':
	start_scrape()
