import io
import json
import random
from scrapy.crawler import CrawlerProcess
# spiders
from quoted.scrapy.spiders import toscrape, brainyquote, goodreads

# Buffer
bytestream = io.BytesIO()


def get_spider():
    spiders = [
        toscrape.QuotesSpider,
        brainyquote.QuotesSpider,
        goodreads.QuotesSpider
    ]
    spider_selector = random.randint(1, len(spiders)-1)

    return spiders[spider_selector]


def do_crawl(spider):
    """
    Crawl web sites to get quotes using scrapy spiders.
    module: quoted.quoted.spiders
    """
    process = CrawlerProcess(settings={
        "LOG_ENABLED": False,
        "TELNETCONSOLE_ENABLED": False,
        "FEED_STORAGES": {
            'buffered': 'quoted.scrapy.extensions.storage.BufferedFeedStorage',
        },
        "FEED_STORAGE_BUFFERED": {
            "bytestream": {
                "module": "quoted.quoted",
                "buffer": "bytestream"
            },
        },
        "FEEDS": {
            "buffered:bytestream": {"format": "json"},
        },
    })

    process.crawl(spider)

    # the script will block here until the crawling is finished
    process.start()


def get_quote_from_json_stream(stream):
    stream_value = stream.getvalue()
    # print(stream_value)
    quotes = json.loads(stream_value)
    # print(quotes)
    quote_selector = random.randint(1, len(quotes)-1)

    return quotes[quote_selector]


def main():
    spider = get_spider()
    do_crawl(spider)

    try:
        quote = get_quote_from_json_stream(bytestream)

        print("\n“%s”" % quote["text"])
        print("―― %s\n" % quote["author"])
        print("tags: %s" % ', '.join(quote["tags"]))
        print("link: %s\n" % quote["url"])
        print("© %s\n" % spider.name)
        print("Powered by quoted")

    except json.JSONDecodeError:
        print("JSONDecodeError: Failed parsing json response!")
    except TypeError:
        print("TypeError: Failed parsing json response!")


if __name__ == "__main__":
    main()
