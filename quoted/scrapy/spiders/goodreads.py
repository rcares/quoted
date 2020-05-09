import scrapy
import random


class QuotesSpider(scrapy.Spider):
    name = 'goodreads'
    base_url = 'https://www.goodreads.com'
    page = random.randint(1, 100)

    start_urls = [
        base_url+'/quotes?page='+str(page),
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            tags = []
            for tag in quote.css('div.greyText > a'):
                tags.append(tag.xpath('text()').get())

            author = quote.css('span.authorOrTitle::text')
            text = quote.css('div.quoteText::text')
            url = quote.css('a.smallText::attr("href")')

            yield {
                'author': author.get().strip(', \n\r\t“”'),
                'text': text.get().strip(', \n\r\t“”'),
                'url': self.base_url+url.get().strip(),
                'tags': tags
            }
