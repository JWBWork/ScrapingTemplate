"""
module defines dictionary containing settings applied by scrapy
"""
from os import path
from src.config import config

custom_settings = {
	'USER_AGENT_LIST': path.join(path.dirname(__file__), 'userAgents.txt'),
	'CONCURRENT_REQUESTS': 15,
	'DOWNLOAD_DELAY': 5,
	'ROBOTSTXT_OBEY': False,
	'DOWNLOAD_TIMEOUT': 100,
	'LOG_ENABLED': False
}

if config['use_proxy']:
	custom_settings['DOWNLOADER_MIDDLEWARES'] = {
		'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
		'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
	}
	custom_settings['ROTATING_PROXY_LIST_PATH'] = \
		path.join(path.dirname(__file__), '../../..', config['proxy_path'])
	custom_settings['ROTATING_PROXY_PAGE_RETRY_TIMES'] = 30
