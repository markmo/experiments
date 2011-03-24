# Scrapy settings for market_rent project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'market_rent'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['market_rent.spiders']
NEWSPIDER_MODULE = 'market_rent.spiders'
DEFAULT_ITEM_CLASS = 'market_rent.items.MarketRentItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

