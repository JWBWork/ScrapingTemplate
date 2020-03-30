
from .scraping.proxies import update_proxies
from .scraping.scrapy.custom_scrapy_settings import custom_settings
from .config import config

# from .paths import project_path
from os import path
project_path = path.join(path.dirname(__file__), '..')

from .scraping.spiders import *
spiders= [
	TemplateSelSpider,
]
