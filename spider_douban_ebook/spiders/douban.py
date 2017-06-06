# -*- coding: utf-8 -*-
import scrapy


class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["read.douban.com"]
    start_urls = ['http://read.douban.com/']

    def parse(self, response):
        pass
