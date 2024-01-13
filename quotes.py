# quotes_scraper/spiders/quotes.py
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = ['http://quotes.toscrape.com/js/']

    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)

        # Extract quote, author, and tags using Selenium
        for quote in self.driver.find_elements("css selector", 'div.quote'):
            yield {
                'quote': quote.find_element("css selector", 'span.text').text,
                'author': quote.find_element("css selector", 'small').text,
                'tags': [tag.text for tag in quote.find_elements("css selector", 'div.tags a.tag')],
            }

        # Handle pagination
        try:
            next_button = self.driver.find_element("css selector", 'li.next a')
            next_button.click()
            yield scrapy.Request(self.driver.current_url, callback=self.parse)
        except NoSuchElementException:
            self.log("No 'Next' button found. Exiting.")

    def closed(self, reason):
        self.driver.quit()
