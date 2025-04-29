import scrapy

class GameItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    genres = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
