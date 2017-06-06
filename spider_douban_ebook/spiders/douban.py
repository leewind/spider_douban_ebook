# -*- coding: utf-8 -*-
import time
import scrapy
import MySQLdb as mdb
from ..utils import SpiderDoubanUtil
from ..items import LSpiderBookInfo

class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["read.douban.com"]
    start_urls = ['http://read.douban.com/']

    domain = 'http://read.douban.com'
    client = None
    limit = 16
    count = 16

    def get_book_list_for_spider(self):
        cursor = self.client.cursor()
        query_sql = 'SELECT * FROM rough_book_brief_info WHERE spider_status=0 AND channel=%s LIMIT %s'
        cursor.execute(query_sql, [
            self.name,
            self.limit
        ])
        book_brief_list = cursor.fetchall()
        cursor.close()
        return book_brief_list

    def start_requests(self):
        config = SpiderDoubanUtil.get_config()
        self.client = mdb.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            passwd=config["passwd"],
            db='spider_rough_base',
            charset=config["charset"]
        )
        self.client.autocommit(True)

        book_brief_list = self.get_book_list_for_spider()
        for book_brief_info in book_brief_list:
            yield scrapy.Request(url=book_brief_info[3],
                                 callback=self.parse_detail,
                                 meta={'recommend': book_brief_info[4]})

    def parse_detail(self, response):
        now = int(time.time())

        item_id = SpiderDoubanUtil.get_item_id(response.url)
        custom_item_id = self.name + '_' + item_id

        author = ''
        author_arr = response.css('a.author-item::text').extract()
        for author_item in author_arr:
            author = author + ' ' + author_item

        title = response.css('h1.article-title::text').extract_first()

        price_str = response.css('span.prices-counts span.current-price-count::text').extract_first()
        price = SpiderDoubanUtil.process_price(price_str)

        if title is not None:
            # 组装book信息
            book_info = LSpiderBookInfo(
                title=title,
                custom_item_id=custom_item_id,
                channel=self.name,
                cover_image_url=response.css(
                    'article.app-article div.cover img::attr(src)').extract_first(),
                author=author,
                abstract=response.css('div.abstract-full div.info').extract_first(),
                detail_url=response.url,
                created_time=now,
                update_time=now,
                price=price,
                recommend=response.meta['recommend']
            )

            yield book_info

        self.count = self.count - 1
        if self.count == 0:
            self.count = self.limit
            print '请求最新的%d个参数' % (self.limit)
            book_brief_list = self.get_book_list_for_spider()
            for book_brief_info in book_brief_list:
                yield scrapy.Request(url=book_brief_info[3],
                                     callback=self.parse_detail,
                                     meta={'recommend': book_brief_info[4]})
