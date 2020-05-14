import random
from . import QuotedSpider


class QuotesSpider(QuotedSpider):
    name = 'goodreads'
    base_url = 'https://www.goodreads.com'
    page = random.randint(1, 100)

    def update_from_cache(self):
        self.start_urls = [
            self.base_url+'/quotes?page='+str(self.page),
        ]

    def options_to_cache(self):
        return {'page': self.page}

    def options_from_cache(self, cache_config):
        self.page = cache_config['options']['page']

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
