from pathlib import Path

import scrapy
import re
from bs4 import BeautifulSoup

class SmartcatSpider(scrapy.Spider):
    name = 'smartcat'
    start_urls = [
        'https://smartcat.io'
    ]

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html, 'lxml')

        for link in soup.find_all("a"):
            if link["href"].startswith('https://smartcat.io') and not 'blog' in link["href"] and link["href"] != response.url:
                yield response.follow(link["href"], callback=self.parse)

        self.remove_useless_elements(soup)
        text = soup.find('div', {'id': 'page'}).get_text()
        sections = [section.get_text() for section in soup.find_all('section')]
        yield {
            'url': response.url,
            'title': response.css('title::text').re('(.*) - SmartCat')[0],
            'text': text,
            'sections': sections
        }
        

    @staticmethod
    def remove_useless_elements(soup):
        if soup.header is not None:
            soup.header.decompose()
        if soup.footer is not None:
            soup.footer.decompose()
        if soup.aside is not None:
            soup.aside.decompose()
        for element in soup.find_all(class_=re.compile('.*gdpr.*')):
            element.decompose()
        for element in soup.find_all(class_='blog__related'):
            element.decompose()
