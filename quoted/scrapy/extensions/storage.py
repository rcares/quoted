import logging
import sys
from urllib.parse import urlparse
from zope.interface import implementer
from scrapy.extensions.feedexport import IFeedStorage


logger = logging.getLogger(__name__)


@implementer(IFeedStorage)
class BufferedFeedStorage:
    """
    Feeds are written to the buffer like `io.BytesIO` or `sys.stdout.buffer`
    identified by key on uri.
    - URI scheme: buffered
    - Example URI: buffered:bytestream
      Where bytestream is the buffered key, this need match with key on
      FEED_STORAGE_BUFFERED
    - Required external libraries: none

    The buffer options are configurated on FEED_STORAGE_BUFFERED var.
    Example:
    "FEED_STORAGE_BUFFERED": {
            "bytestream": {
                "module": "quoted.quoted",
                "buffer": "bytestream"
                },
        }

    - `bytestream` key need match with id of uri (buffered:key)
    - `module` is the python module where var is located
    - `buffer` is the name of var to use
    """

    def __init__(self, uri):
        self._buffer_id = urlparse(uri).path
        self._buffer = None
        self._module_name = None
        self._buffer_name = None

    def open(self, spider):
        settings = spider.crawler.settings['FEED_STORAGE_BUFFERED']

        if self._buffer_id not in settings:
            logger.error(
                "Buffer id %s not found in FEED_STORAGE_BUFFERED settings"
                %
                (self._buffer_id)
            )
            return self._buffer_id

        buffer_settings = settings[self._buffer_id]
        self._module_name = buffer_settings["module"]
        logger.debug("Module Name: %s" % (self._module_name))

        module_object = sys.modules[self._module_name]
        logger.debug("Module Object: %s" % (str(module_object)))

        self._buffer_name = buffer_settings["buffer"]
        logger.debug("Buffer Name: %s" % (self._buffer_name))

        self._buffer = getattr(module_object, self._buffer_name)
        logger.debug("Buffer Object: %s" % (str(self._buffer)))

        return self._buffer

    def store(self, file):
        module_object = sys.modules[self._module_name]
        # update object reference to file argument
        setattr(module_object, self._buffer_name, file)
