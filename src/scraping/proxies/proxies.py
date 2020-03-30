"""
module containing methods pertaining to harvesting, storing, and retrieving proxies
"""
from lxml.html import fromstring
import requests
from itertools import cycle
import traceback
from os import path
from pprint import pprint
from loguru import logger
from src.config import config


proxy_path = path.join(path.dirname(__file__), config['proxy_path'].split('/')[-1])


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
	# todo: harvest these proxies when the site is back up
	url = 'https://www.proxy-list.download/HTTP'
	response = requests.get(url)
	pprint(response.__dict__)


def update_proxies(merge=False):
	"""
	takes functions retrieving proxies from different sites and merges results into single set, then writes to file
	:param merge: Boolean , if true will not overwrite previously harvested proxies
	"""
	new_proxies = set()
	proxy_sources = (
		harvest_us_proxy,
		harvest_proxyscrape_api
	)
	logger.info('requesting proxies...')
	for func in proxy_sources:
		new_proxies = new_proxies.union(func())

	if merge:
		logger.info('loading previous proxies')
		current_proxies = get_proxies()
		new_proxies = set(new_proxies).union(set(current_proxies))

	logger.info('writing proxies to file')
	with open(proxy_path, 'wb') as p_file:
		new_line = b'\n'
		for proxy in new_proxies:
			p_file.write(proxy + new_line)


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
	# harvest_proxy_list()
