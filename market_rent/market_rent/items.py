# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class MarketRentItem(Item):
    date_type = Field()
    start_date = Field()
    end_date = Field()
    region = Field()
    district = Field()
    area = Field()
    bedrooms = Field()
    dwelling = Field()
    bonds_received = Field()
    average_rent = Field()
    std = Field()
    lower_quartile = Field()
    median_rent = Field()
    upper_quartile = Field()
