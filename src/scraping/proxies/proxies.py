"""
module containing methods pertaining to harvesting, storing, and retrieving proxies
"""
from lxml.html import fromstring
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from itertools import cycle
import traceback
from os import path
from pprint import pprint
import re
import pickle
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import \
	NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
from os import path, name as os_name
from time import sleep
from src.config import config
from datetime import datetime, timedelta


proxy_path = path.join(path.dirname(__file__), config['proxy_path'].split('/')[-1])
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = True
chrome_options.add_argument("--log-level=2")
chrome_options.add_argument("--–disable-notifications")
chrome_options.add_argument("--disable-dev-shm-usage")
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"
chrome_options.add_argument(f'--user-agent={user_agent}')
chrome_options.add_argument("test-type")

executable_path = path.join(
	path.dirname(__file__), f"../selenium/chromedriver.exe"
) if os_name == 'nt' else "/usr/bin/chromedriver"
driver = webdriver.Chrome(
	executable_path=executable_path,
	options=chrome_options
)


def spys():
	driver.get('http://spys.one/free-proxy-list/US/')
	driver.implicitly_wait(2)
	for _ in range(3):
		display_500_option = driver.find_element_by_xpath(
			'/html/body/table[2]/tbody/tr[5]/td/table/tbody/tr[1]/td[2]/font[2]/select[1]/option[6]'
		)
		display_500_option.click()
		sleep(1)
	for _ in range(3):
		driver.implicitly_wait(2)
		port_http_option = driver.find_element_by_xpath(
			'/html/body/table[2]/tbody/tr[5]/td/table/tbody/tr[1]/td[2]/font[2]/select[5]/option[2]'
		)
		port_http_option.click()
		sleep(2)
	driver.implicitly_wait(3)
	page_source = driver.page_source
	soup = BeautifulSoup(page_source, features="lxml")
	potential_proxies = soup.find_all('font', {'class': 'spy14'})
	python_re_pattern = r"(\d+\.\d+\.\d+\.\d+)<script[\s\w=\"/>\.\(<>:\\+^\)]+</font>(\d+)"
	proxy_re = lambda html: f'{re.search(python_re_pattern, str(html)).group(1)}:' \
	                        f'{re.search(python_re_pattern, str(html)).group(2)}' if \
		re.search(python_re_pattern, str(html)) and \
		re.search(python_re_pattern, str(html)) \
		else None
	proxies = set([proxy_re(pp).encode('utf-8') for pp in potential_proxies
	               if proxy_re(pp) is not None])
	driver.close()
	driver.quit()
	return proxies


def harvest_proxyscrape_api():
	"""
	calls proxyscrape.com url which returns a list of proxies, returns set of proxies.
	:return: set
	"""
	url = 'https://api.proxyscrape.com/' \
	      '?request=getproxies&' \
	      'proxytype=http&' \
	      'timeout=10000&' \
	      'country=US&' \
	      'ssl=all&' \
	      'anonymity=all'
	response = requests.get(url)
	proxies = response.content.split(b'\r\n')
	try:
		proxies.remove(b'')
	except ValueError as e:
		print('proxies.remove(b'') ValueError - continuing')
	return set(proxies)


def harvest_us_proxy():
	"""
	scrapes free-proxy-list.net for list of proxies, returns set of proxies
	:return:
	"""
	logger.info('harvest_us_proxy - requesting https://free-proxy-list.net/')
	url = 'https://www.us-proxy.org/'
	response = requests.get(url)

	logger.info('parsing response for proxies')
	parser = fromstring(response.text)
	proxies = set()
	for i in parser.xpath('//tbody/tr'):
		try:
			ip = i.xpath('.//td[1]/text()')
			port = i.xpath('.//td[2]/text()')
			if ip and port:
				proxy = ":".join([
					ip[0], port[0]
				])
				# proxy = f'http://{proxy}'
				proxies.add(proxy.replace('\n', '').encode())
		except Exception as e:
			logger.warning(f'Exception parsing proxy!: {e}, {ip}:{port}')
	if len(proxies) == 0:
		logger.warning('harvest_us_proxy returning empty set list!')
	return set(proxies)


def harvest_proxy_list():
	# url = 'https://www.proxy-list.download/HTTP'
	url = 'https://www.proxy-list.download/api/v1/get?type=https&&country=US'
	response = requests.get(url)
	https = response.content.split(b'\r\n')
	url = 'https://www.proxy-list.download/api/v1/get?type=http&&country=US'
	response = requests.get(url)
	http = response.content.split(b'\r\n')
	proxies = set(http + https)
	return proxies


def proxy_nova():
	#todo: finish?
	url = 'https://www.proxynova.com/proxy-server-list/country-us/'
	response = requests.get(url)
	# print(response.text)
	parser = fromstring(response.text)
	ips = parser.xpath('/html/body/div[3]/div[2]/table/tbody[1]/tr/td/abbr/@title')
	print(ips)


def update_proxies(merge=False):
	"""
	takes functions retrieving proxies from different sites and merges results into single set, then writes to file
	:param merge: Boolean , if true will not overwrite previously harvested proxies
	"""
	pickle_path = path.join(path.dirname(__file__), 'prev_harvest_dt.pkl')
	try:
		with open(pickle_path, 'rb') as pickle_file:
			prev_harvest_dt = pickle.load(pickle_file)
	except Exception as e:
		logger.warning(f'update_proxies no pickl found at {pickle_path}: {e}')
		prev_harvest_dt = datetime.now() - timedelta(minutes=16)
	now = datetime.now()
	if now - prev_harvest_dt > timedelta(minutes=15):
		logger.info(f'Updating proxies! '
		            f'(No time record: {not prev_harvest_dt} or '
		            f'now-pdt>15m: {now - prev_harvest_dt > timedelta(minutes=15)})')
		all_proxies = set()
		proxy_sources = (
			harvest_us_proxy,
			harvest_proxyscrape_api,
			harvest_proxy_list,
			spys
		)
		logger.info('requesting proxies...')
		for func in proxy_sources:
			logger.info(f'harvesting proxies from {func.__name__}')
			try:
				new_proxies = func()
				all_proxies = all_proxies.union(new_proxies)
				logger.info(f'{func.__name__} returned {len(new_proxies)} '
				            f'proxies, {len(all_proxies)} total')
			except (ConnectTimeout, ConnectionError) as e:
				logger.error(f'{e} for {func.__name__}')

		if merge:
			logger.info('loading previous proxies')
			current_proxies = get_proxies()
			all_proxies = set(all_proxies).union(set(current_proxies))

		logger.info('writing proxies to file')
		with open(proxy_path, 'wb') as p_file:
			new_line = b'\n'
			for proxy in all_proxies:
				p_file.write(proxy + new_line)
		with open(pickle_path, 'wb') as pickle_file:
			logger.info(f'logging current proxy harvest time: {now} to {pickle_path}')
			pickle.dump(now, pickle_file)
	else:
		pass
		# logger.info(f'Not updating proxies. '
		#             f'(No time record: {not prev_harvest_dt} or '
		#             f'now-pdt>15m: {now - prev_harvest_dt > timedelta(minutes=15)}')


def get_proxies():
	"""
	returns harvested proxies as a list
	:return: list
	"""
	if path.isfile(proxy_path):
		with open(proxy_path, 'rb') as p_file:
			return list(proxy for proxy in p_file)
	else:
		logger.warning(f'no proxy file found! creating {config["proxy_file"]}')
		with open(proxy_path, 'wb') as p_file:
			p_file.close()
			return []


if __name__ == '__main__':
	update_proxies()
	# proxy_nova()
	# spys()
	pass
