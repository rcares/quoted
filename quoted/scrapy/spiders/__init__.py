import scrapy
import logging
import json
import io
from time import time
from pathlib import Path


class QuotedSpider(scrapy.Spider):
    def _set_crawler(self, crawler):
        super()._set_crawler(crawler)

        cache = self.settings.get('HTTPCACHE_EXPIRATION_SECS')
        self.log('CACHE: %s' % cache, logging.DEBUG)

        quoted_cache_config_file = self.settings.get('QUOTED_CACHE_CONFIG_FILE')
        self.log('QUOTED_CACHE_CONFIG_FILE: %s' % quoted_cache_config_file)

        if cache != 0:
            cache_config = self.read_cache_config(quoted_cache_config_file) # noqa

            cache_expired = self.check_cache_expired(
                cache_config=cache_config,
                cache=cache
            )

            if cache_expired:
                self.write_cache_config(
                    quoted_cache_config_file,
                    time(),
                    self.options_to_cache()
                )
            else:
                self.options_from_cache(cache_config)

        self.update_from_cache()

    def update_from_cache(self):
        raise NotImplementedError

    def options_to_cache(self):
        raise NotImplementedError

    def options_from_cache(self, cache_config):
        raise NotImplementedError

    def check_cache_expired(self, cache_config, cache):
        return (cache_config is None) or (0 < cache < time() - cache_config['timestamp']) # noqa

    def read_cache_config(self, cache_settings_file):
        cache_settings_json = {}

        if Path(cache_settings_file).is_file():
            with open(cache_settings_file, 'r') as data_file:
                cache_settings_json = json.load(data_file)

            if self.name in cache_settings_json:
                return cache_settings_json[self.name]

        return None

    def write_cache_config(self, cache_settings_file, timestamp, options):
        cache_settings_json = {}
        if Path(cache_settings_file).is_file():
            with io.open(cache_settings_file, 'r+') as data_file:
                cache_settings_json = json.load(data_file)

        cache_settings_json[self.name] = {
            'timestamp': timestamp,
            'options': options
        }

        # Write JSON file
        with io.open(cache_settings_file, 'w+', encoding='utf8') as outfile:
            str_ = json.dumps(
                cache_settings_json,
                indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False
            )
            outfile.write(str(str_))
