import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'BrainyQuote'
    base_url = 'https://www.brainyquote.com'
    start_urls = [
        base_url+'/quote_of_the_day',
    ]

    def parse(self, response):
        for quote in response.css('div.qll-bg'):
            tags = []
            for tag in quote.css('a.qkw-btn'):
                tags.append(tag.xpath('text()').get())
            yield {
                'author': quote.xpath('div/div/div/a/text()').get(),
                'text': quote.xpath('div/div/a/text()').get(),
                'url': self.base_url+quote.xpath('div/div/a/@href').get(),
                'tags': tags
            }
