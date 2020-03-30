from .scraping.spiders import *
spiders= [
	TemplateSelSpider,
]

from .scraping.proxies import update_proxies
from .scraping.scrapy.custom_scrapy_settings import custom_settings
from .config import config