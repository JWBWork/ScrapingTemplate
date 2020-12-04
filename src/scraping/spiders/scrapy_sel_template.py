import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
		self.config = kwargs['config']
		self.file_path = kwargs.get(
			'file_path',
			path.join(project_path, f"results/{self.__class__.__name__}-{datetime.now().strftime('%y-%m-%d-%H-%M')}")
		)
		if kwargs.get('use_selenium'):
			self.driver = get_driver()
		logger.info(
			f'{TemplateSelSpider.name} init, store: {type(self.store)}, file_path: {self.file_path}'
		)
		super().__init__()

	def start_requests(self):
		# TODO: change for multiple start urls?
		# for url in TemplateSelSpider.start_urls:
		step_0 = self.config.sets[0]
		callback = getattr(self, step_0['type'])
		for url in step_0.url:
			request = scrapy.Request(
				url,
				# callback=self.parse,
				callback=callback,
				meta={'step_n': 0}
			)
			request.meta['max_proxies_to_try'] = 150
			yield request

	def parse(self, response):
		logger.info(f'parsed url {response.url}')
		# SELENIUM DRIVER
		# self.driver.get(response.url)
		# self.driver.implicitly_wait(3)
		# Append data
		self.store = self.store.append({'c': 0, 'd': 2}, ignore_index=True)

	def selenium_scrape(self, response):
		step = self.config['steps'][response.meta['step_n']]
		self.driver.get(step['url'])
		self.driver.implicitly_wait(2)
		instructions = step['selenium']
		repeat = instructions.get('repeat')
		follow_urls = []

		def follow_check(scrape, url):
			if scrape['follow_urls']:
				follow_urls.append(url)

		# actual scraping happens in while loop
		while True:
			for action_n, action in enumerate(instructions.actions):
				action_type = action['action']
				if action_type == 'click':
					button = self.driver.find_element_by_xpath(action['path'])
					button.click()
					self.driver.implicitly_wait(2)
				elif action_type == 'scrape':
					targets = self.driver.find_elements_by_xpath(action['path'])
					for attribute, name in action['scrape']['content'].items():
						if attribute == 'href':
							for target in targets:
								href_url = target.get_attribute('href')
								follow_check(instructions['scrape'], href_url)

			if not instructions.get('repeat'):
				break
			elif repeat.condition == "Not present":
				# TODO: other break conditions? Not clickable? ect?
				try:
					if repeat['type'] == 'xpath':
						self.driver.find_elements_by_xpath(repeat['xpath'])
				except NoSuchElementException:
					break

		for url in follow_urls:
			request =

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
		'use_selenium': False,
		'config': config
	}
	process.crawl(TemplateSelSpider, **kwargs)
	process.start()


if __name__ == '__main__':
	start_scrape()
