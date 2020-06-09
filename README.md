# ScrapingTemplate
I created this template for my freelance webscraping work.
It's just a scaffold that I found useful for most of any webscraping projects I take on with any complexity. 
This is build with scrapy to build crawlers which will automate navigation through the site, 
and is built to be used with the optional software of selenium.

Most of my webscraping jobs involve scraping data across many pages with the same structure.
I typically accomplish this in three steps:

1. *Find the route to the desired data.*
Ultimately what I want is to scrape data that's distributed across some subset of pages on a website.
In order to automate this crawling process I typically target one page where I can scrape a list of URLs to my target data.
Once I've found a way to scrape that list of URLs the crawler can automate navigation to my target data.

2. *Implement the scrape of the target data*
This simply consists of identifying the tags that will be used to target the desired data and applying them to automate
the data scrape.

3. *Clean and deliver*
This just consists of basic data cleaning before delivery, dropping any duplicates, ensuring data is formatted as requested, ect.

This scaffold is designed to work in this workflow. Scrapy is applied to build crawlers which target pages that will provide 
URLs to the desired data, and then automates the navigation to the desired data to be scraped. The template is also built 
so Selenium can be applied to scrape data as required as well.
