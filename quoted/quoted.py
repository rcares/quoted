import io
import json
import random
import logging
import shutil
from pathlib import Path
from importlib_metadata import version, PackageNotFoundError
import click
from scrapy.crawler import CrawlerProcess
from rich.console import Console
from rich.logging import RichHandler
# spiders
from quoted.scrapy.spiders import toscrape, brainyquote, goodreads

# Logging
logger = logging.getLogger(__name__)

# Paths
QUOTED_DIR = str(Path.home().joinpath('.quoted'))
QUOTED_CACHE_DIR = str(Path(QUOTED_DIR).joinpath('cache'))

# Buffer
bytestream = io.BytesIO()


def init_logging(log_level=logging.CRITICAL):
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=log_level,
        format=FORMAT, datefmt="[%X] ",
        handlers=[RichHandler(level=log_level)]
    )

    return logging.getLogger(__name__)


def get_spider():
    spiders = [
        toscrape.QuotesSpider,
        brainyquote.QuotesSpider,
        goodreads.QuotesSpider
    ]
    spider_selector = random.randint(1, len(spiders)-1)

    return spiders[spider_selector]


def do_crawl(spider, cache=0, cache_dir='httpcache'):
    """
    Crawl web sites to get quotes using scrapy spiders.
    module: quoted.quoted.spiders
    """
    if Path(cache_dir).is_absolute():
        """
        If cache_dir is relative scrapy create a .scrapy/<cache_dir>
        directory relative to project dir.
        https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-dir
        """
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

    process = CrawlerProcess(settings={
        "LOG_ENABLED": False,
        "TELNETCONSOLE_ENABLED": False,
        "HTTPCACHE_ENABLED": False if cache == 0 else True,
        "HTTPCACHE_STORAGE": 'scrapy.extensions.httpcache.FilesystemCacheStorage',
        "HTTPCACHE_POLICY": 'scrapy.extensions.httpcache.DummyPolicy',
        "HTTPCACHE_EXPIRATION_SECS": cache,
        "HTTPCACHE_DIR": cache_dir,
        "HTTPCACHE_GZIP": True,
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
    logger.debug(stream_value)
    quotes = json.loads(stream_value)
    logger.debug(quotes)
    quote_selector = random.randint(1, len(quotes)-1)

    return quotes[quote_selector]


def do_show_version(console, logger):
    quoted_version = 'master'
    try:
        quoted_version = version('quoted')
    except PackageNotFoundError:
        logger.debug("PackageNotFoundError: quoted version not found")
    console.print('Quoted version %s' % quoted_version)
    exit()


def do_cache_clear(console, logger):
    try:
        if Path(QUOTED_CACHE_DIR).is_dir():
            shutil.rmtree(Path(QUOTED_CACHE_DIR))
    except Exception:
        logger.critical(
            'Exception: An error ocurred when try delete %s directory'
            %
            QUOTED_CACHE_DIR
        )
        exit()
    console.print(':wastebasket: Cache cleared')
    exit()


def do_print_quote(quote, spider, show_tags, show_link, console, print_styles):
    console.print("")
    console.print(
        "“%s”" % quote["text"],
        style=print_styles["text"],
        highlight=False
    )
    console.print("―― %s" % quote["author"], style=print_styles["author"])
    console.print("")
    if show_tags:
        console.print("tags: %s" % ', '.join(quote["tags"]))
    if show_link:
        console.print("link: %s" % quote["url"])
    if show_tags or show_link:
        console.print("")
    console.print("© %s" % spider.name)
    console.print("")
    console.print("Powered by quoted")


@click.command()
@click.option(
    '--rich-text/--no-rich-text',
    ' /-R',
    help='Rich Text support',
    default=True,
    show_default=True
)
@click.option(
    '--show-tags/--no-show-tags',
    ' /-T',
    help='Show or Hide quote tags',
    default=True,
    show_default=True
)
@click.option(
    '--show-link/--no-show-link',
    ' /-L',
    help='Show or Hide quote link',
    default=True,
    show_default=True
)
@click.option(
    '--log-level',
    '-l',
    help='Set log level',
    type=click.Choice(
        [
            'CRITICAL',
            'ERROR',
            'WARNING',
            'INFO',
            'DEBUG',
            'NOTSET'
        ],
        case_sensitive=False
    ),
    default='CRITICAL',
    show_default=True
)
@click.option(
    '--version',
    '-v',
    'show_version',
    help='Print version information and quit',
    is_flag=True
)
@click.option(
    '--cache',
    help='Cache expiration in seconds (0 means disabled)',
    type=int,
    default=86400,  # one day
    show_default=True
)
@click.option(
    '--cache-clear',
    help='Clear data from cache directory (%s)' % QUOTED_CACHE_DIR,
    is_flag=True
)
def main(
    rich_text=True,
    show_tags=True,
    show_link=True,
    log_level="CRITICAL",
    show_version=False,
    cache=86400,
    cache_clear=False
):
    """Feed your brain with the best random quotes from multiple web portals"""
    print_styles = {
        "text": "italic",
        "author": "bold"
    }

    if not rich_text:
        print_styles = {
            "text": "",
            "author": ""
        }

    logger = init_logging(log_level)
    console = Console()

    if show_version:
        do_show_version(console=console, logger=logger)

    if cache_clear:
        do_cache_clear(console, logger)

    spider = get_spider()
    do_crawl(spider, cache, QUOTED_CACHE_DIR)

    try:
        quote = get_quote_from_json_stream(bytestream)

        do_print_quote(
            quote,
            spider,
            show_tags,
            show_link,
            console,
            print_styles
        )

    except json.JSONDecodeError:
        logger.error("JSONDecodeError: Failed parsing json response!")
    except TypeError:
        logger.error("TypeError: Failed parsing json response!")


if __name__ == "__main__":
    main()
