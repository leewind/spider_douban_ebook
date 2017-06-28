# -*- coding: utf-8 -*-
import time
from urlparse import urlparse
import scrapy
import MySQLdb as mdb
from ..utils import SpiderDoubanUtil
from ..items import LSpiderTopicInfo, LSpiderBookInfo


class DoubanBannerSpider(scrapy.Spider):
    name = "douban_banner"
    allowed_domains = ["read.douban.com"]
    start_urls = ['https://read.douban.com/ebooks']

    channel = "douban"
    domain = 'https://read.douban.com'
    client = None

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

        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def get_banner_object(self, banners, now, banner_list):
        if banner_list is not None:
            for banner in banner_list:

                url = banner.css('a::attr(href)').extract_first()

                if 'topic' in url:
                    topic = LSpiderTopicInfo(
                        topic_type="image_for_books_aggregation",
                        name=banner.css('img::attr(alt)').extract_first(),
                        content=None,
                        published_time=now,
                        cover_image=banner.css(
                            'img::attr(src)').extract_first(),
                        detail_url=url,
                        channel=self.channel,
                        books=[]
                    )
                    banners.append(topic)
                elif 'ebook' in url:
                    item_id = SpiderDoubanUtil.get_item_id(url)
                    custom_item_id = self.name + '_' + item_id
                    topic = LSpiderTopicInfo(
                        topic_type="image_for_single_book",
                        name=banner.css('img::attr(alt)').extract_first(),
                        content=None,
                        published_time=now,
                        cover_image=banner.css(
                            'img::attr(src)').extract_first(),
                        detail_url=url,
                        channel=self.channel,
                        books=[custom_item_id]
                    )
                    banners.append(topic)

    def parse(self, response):
        now = int(time.time())
        banners = []

        major_banners = response.css('ul.slide-list li.slide-item')
        self.get_banner_object(banners, now, major_banners)

        for banner_info in banners:
            cursor = self.client.cursor()
            sql = 'SELECT count(*) FROM rough_topic_info WHERE detail_url="%s"' % (
                banner_info.get('detail_url'))
            cursor.execute(sql)
            item = cursor.fetchone()
            cursor.close()

            if item[0] == 0:
                if banner_info['topic_type'] == 'image_for_books_aggregation':
                    yield scrapy.Request(url=banner_info.get('detail_url'),
                                         callback=self.parse_list,
                                         meta={"banner": banner_info})
                elif banner_info['topic_type'] == 'image_for_single_book':
                    yield banner_info
                    yield scrapy.Request(url=banner_info.get('detail_url'),
                                         callback=self.parse_detail,
                                         meta={'recommend': None})

    def parse_list(self, response):
        banner_info = response.meta['banner']
        items = response.css('ul.summary-list li.item')
        for item in items:
            url = item.css(
                'div.border-wrap div.cover a::attr(href)').extract_first()
            recommend = item.css(
                'div.border-wrap div.info div.rec-intro::text').extract_first()
            item_id = SpiderDoubanUtil.get_item_id(url)
            banner_info['books'].append(self.channel + '_' + item_id)

            print self.domain + url
            yield scrapy.Request(url=self.domain + url,
                                 callback=self.parse_detail,
                                 meta={'recommend': recommend})

        next_page = response.css(
            'div.pagination ul li.next a::attr(href)').extract_first()
        if next_page is not None:
            ourl = urlparse(response.url)

            url = self.domain + next_page
            if next_page[0] == '?':
                url = self.domain + ourl.path + next_page

            print url
            yield scrapy.Request(url=url,
                                 callback=self.parse_list,
                                 meta={"banner": banner_info})
        else:
            yield banner_info

    def parse_detail(self, response):
        now = int(time.time())

        item_id = SpiderDoubanUtil.get_item_id(response.url)
        custom_item_id = self.name + '_' + item_id

        author = ''
        author_arr = response.css('a.author-item::text').extract()
        for author_item in author_arr:
            author = author + ' ' + author_item

        title = response.css('h1.article-title::text').extract_first()

        price_str = response.css(
            'span.prices-counts span.current-price-count::text').extract_first()
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
                abstract=response.css(
                    'div.abstract-full div.info').extract_first(),
                detail_url=response.url,
                created_time=now,
                update_time=now,
                price=price,
                recommend=response.meta['recommend']
            )

            yield book_info
