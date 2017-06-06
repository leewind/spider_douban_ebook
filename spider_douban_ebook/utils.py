# -*- coding: utf-8 -*-
import re
import json

class SpiderDoubanUtil(object):

    @staticmethod
    def get_config():
        file_reader = open("config.json", "r")
        config_info = file_reader.read()
        config = json.loads(config_info)
        file_reader.close()
        return config

    @staticmethod
    def get_item_id(url):
        """从URL中获取item_id
        Args:
            url (string): url链接

        Returns:
            item_id (string): item_id
        """
        # item_id从url中获取
        item_id_pattern = re.compile(r'\/ebook\/(.+)')
        found = item_id_pattern.findall(url)
        item_id = None
        if found:
            item_id = found[0]

        if item_id is not None:
            item_id_clean_pattern = re.compile(r'\w+')
            clean = item_id_clean_pattern.findall(item_id)
            length = len(clean)
            if length == 0:
                return item_id
            else:
                item_id = clean[0]

        return item_id

    @staticmethod
    def process_price(price_str):
        """将price从string变成int
        Args:
            url (string): url链接

        Returns:
            price (int): 商品价格
        """

        price = 0
        if price_str is not None:
            # if u'免费' in price_str:
                # price = 0
            # else:

            price_str = price_str.replace(u'¥', '')
            price_str = price_str.replace(u'￥', '')
            price = int(float(price_str) * 100)
        else:
            price = 0

        return price
