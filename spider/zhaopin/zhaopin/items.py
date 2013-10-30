# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ZhaopinItem(Item):
    position = Field()
    company = Field()
    time = Field()
    position_desc = Field()
    url = Field()
    company_desc = Field()
    company_address = Field()
