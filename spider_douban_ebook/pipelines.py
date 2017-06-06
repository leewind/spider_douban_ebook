# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb as mdb
from items import LSpiderBookBriefInfo, LSpiderBookInfo
from utils import SpiderDoubanUtil

class SpiderDoubanEbookPipeline(object):
    """数据爬取完成之后对数据进行处理
    meijutt站点数据爬取之后存储mysql数据库

    Attributes:
        client (:obj): 数据库操作游标
    """
    client = None

    def open_spider(self, spider):
        """爬虫开启之后的回调
        爬虫开启之后，连接上数据库

        Args:
            spider (scrapy.Spider) 爬虫对象
        """
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

    def process_book_brief(self, item, cursor):
        book_brief_info = [
            item.get('custom_item_id'),
            item.get('channel'),
            item.get('detail_url'),
            item.get('created_time'),
            item.get('update_time'),
            item.get('recommend'),
            item.get('spider_status')
        ]
        book_brief_info_insert_sql = 'INSERT IGNORE INTO rough_book_brief_info (custom_item_id, channel, detail_url, created_time, update_time, recommend, spider_status) values(%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(book_brief_info_insert_sql, book_brief_info)

    def process_book(self, item, cursor):
        book_info = [
            item.get('title'),
            item.get('custom_item_id'),
            item.get('channel'),
            item.get('cover_image_url'),
            item.get('author'),
            item.get('abstract'),
            item.get('detail_url'),
            item.get('created_time'),
            item.get('update_time'),
            item.get('price'),
            item.get('recommend'),
        ]
        book_info_insert_sql = 'INSERT IGNORE INTO rough_book_info (title, custom_item_id, channel, cover_image_url, author, abstract, detail_url, created_time, update_time, price, recommend) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(book_info_insert_sql, book_info)

        update_book_spider_status_sql = 'UPDATE rough_book_brief_info SET spider_status=1 WHERE custom_item_id=%s'
        cursor.execute(update_book_spider_status_sql, [
            item.get('custom_item_id')
        ])

        # tag_list = item.get('tags')
        # for tag in tag_list:
        #     tag_info = [
        #         tag.get('name'),
        #         item.get('custom_item_id')
        #     ]
        #     print "name: %s, id: %s" % (tag.get('name'), item.get('custom_item_id'))
        #     book_tag_reflection_sql = 'INSERT IGNORE INTO book_tag_reflection (tag_name, book_custom_item_id) values (%s, %s)'
        #     cursor.execute(book_tag_reflection_sql, tag_info)

    def process_item(self, item, spider):
        """处理item数据

        Args:
            item (scrapy.Item): scrapy.Item数据对象
            spider (scrapy.Spider): scrapy.Spider爬虫对象

        Returns:
            item (scrapy.Item): scrapy.Item数据对象
        """

        cursor = self.client.cursor()

        if type(item) is LSpiderBookInfo:
            self.process_book(item, cursor)
        elif type(item) is LSpiderBookBriefInfo:
            self.process_book_brief(item, cursor)

        # 每次完成之后都需要关闭游标
        cursor.close()
        return item

    def close_spider(self, spider):
        """关闭spider
        每次关闭spider时候关闭数据库连接
        """

        if self.client is not None:
            self.client.close()
