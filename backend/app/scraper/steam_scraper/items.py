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
    developers = scrapy.Field()
    publishers = scrapy.Field()  # Add this field to fix the KeyError
