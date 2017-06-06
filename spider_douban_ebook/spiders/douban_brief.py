# -*- coding: utf-8 -*-
import time
import urllib
import scrapy
from urlparse import urlparse
from ..utils import SpiderDoubanUtil
from ..items import LSpiderBookBriefInfo


class DoubanBriefSpider(scrapy.Spider):
    name = "douban_brief"
    allowed_domains = ["read.douban.com"]
    start_urls = ['https://read.douban.com/ebooks/']

    domain = "https://read.douban.com"
    channel = "douban"

    def parse(self, response):
        catalogs = response.css(
            'section.kinds ul.kinds-list li a::attr(href)').extract()

        for catalog in catalogs:
            url = self.domain + catalog

            yield scrapy.Request(url=url,
                                 callback=self.parse_list)

    def parse_list(self, response):
        now = int(time.time())
        book_list = response.css('ul.ebook-list li.store-item')

        for book in book_list:

            detail_url = book.css(
                'div.info div.title a::attr(href)').extract_first()
            item_id = SpiderDoubanUtil.get_item_id(detail_url)
            if item_id is not None:
                custom_item_id = self.channel + '_' + item_id
                url = self.domain + detail_url

                yield LSpiderBookBriefInfo(
                    custom_item_id=custom_item_id,
                    channel=self.channel,
                    created_time=now,
                    update_time=now,
                    recommend=book.css(
                        'div.info div.article-desc-brief::text').extract_first(),
                    detail_url=url,
                    spider_status=0
                )

        next_page = response.css(
            'div.pagination li.next a::attr(href)').extract_first()
        if next_page is not None:
            ourl = urlparse(response.url)

            print '\n------------------------'
            print ourl.path
            print ourl.path + next_page
            print '------------------------\n'

            if next_page[0] == '?':
                yield scrapy.Request(url=self.domain + ourl.path + next_page,
                                     callback=self.parse_list)
            else:
                yield scrapy.Request(url=self.domain + next_page,
                                     callback=self.parse_list)
