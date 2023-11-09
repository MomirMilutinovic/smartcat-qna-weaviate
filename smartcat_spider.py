from pathlib import Path

import scrapy
import re
from bs4 import BeautifulSoup

class SmartcatSpider(scrapy.Spider):
    name = 'smartcat'
    start_urls = [
        'https://smartcat.io/',
        'https://smartcat.io/company/',
        'https://smartcat.io/industries/',
        'https://smartcat.io/case-studies/',
        'https://smartcat.io/jobs/',
        'https://smartcat.io/blog/',
        'https://smartcat.io/tech-blog/',
    ]

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html, 'lxml')
        self.remove_useless_elements(soup, response.url)
        text = soup.find('div', {'id': 'page'}).get_text()
        yield {
            'referer': str(response.request.headers.get('Referer', None)),
            'title': response.css('title::text').re('(.*) - SmartCat')[0],
            'text': text
        }
        
        for link in soup.find_all("a"):
            if link["href"].startswith('https://smartcat.io'):
                yield response.follow(link["href"], callback=self.parse)

    @staticmethod
    def remove_useless_elements(soup, url):
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
