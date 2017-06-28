# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LSpiderBookInfo(scrapy.Item):
    title = scrapy.Field()
    custom_item_id = scrapy.Field()
    channel = scrapy.Field()
    cover_image_url = scrapy.Field()
    author = scrapy.Field()
    abstract = scrapy.Field()
    detail_url = scrapy.Field()
    created_time = scrapy.Field()
    update_time = scrapy.Field()
    price = scrapy.Field()
    recommend = scrapy.Field()

class LSpiderBookBriefInfo(scrapy.Item):
    custom_item_id = scrapy.Field()
    channel = scrapy.Field()
    detail_url = scrapy.Field()
    created_time = scrapy.Field()
    update_time = scrapy.Field()
    recommend = scrapy.Field()
    spider_status = scrapy.Field()

class LSpiderTopicInfo(scrapy.Item):
    topic_type = scrapy.Field()
    name = scrapy.Field()
    content = scrapy.Field()
    published_time = scrapy.Field()
    cover_image = scrapy.Field()
    detail_url = scrapy.Field()
    books = scrapy.Field()
    channel = scrapy.Field()
