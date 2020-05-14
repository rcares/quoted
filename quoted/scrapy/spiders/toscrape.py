from . import QuotedSpider


class QuotesSpider(QuotedSpider):
    name = 'Quotes to Scrape'
    base_url = 'http://quotes.toscrape.com'
    start_urls = [
        '%s/tag/humor/' % base_url,
    ]

    def update_from_cache(self):
        pass

    def options_to_cache(self):
        return {}

    def options_from_cache(self, cache_config):
        pass

    def parse(self, response):
        for quote in response.css('div.quote'):
            tags = quote.css('meta.keywords').attrib['content'].split(',')
            yield {
                'author': quote.xpath('span/small/text()').get().strip(', \n\r\t“”'),
                'text': quote.css('span.text::text').get().strip(', \n\r\t“”'),
                'url': '%s%s' % (self.base_url, quote.css('span a::attr("href")').get()),
                'tags': tags
            }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
