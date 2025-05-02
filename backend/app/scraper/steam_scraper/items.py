import scrapy

class GameItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    genres = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
    app_id = scrapy.Field()
    description = scrapy.Field()
    rating_text = scrapy.Field()
    is_indie = scrapy.Field()
    source = scrapy.Field()
