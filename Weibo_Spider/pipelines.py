# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import time
import pymongo
from .items import *
from .settings import DATETIME_FORMAT, DATE_FORMAT

class WeiboSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

# ---------- MongoDB_Pipeline ----------
class MongoPipeline(object):
    def __init__(self, mongo_host, mongo_port, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGODB_HOST'),
            mongo_port=crawler.settings.get('MONGODB_PORT'),
            mongo_db=crawler.settings.get('MONGODB_DBNAME')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, WeibocnSleepItem) or isinstance(item, WeibocnItem):
            self.db[item.__class__.__name__].create_index([('id', pymongo.ASCENDING)])
            self.db[item.__class__.__name__].update({'id': item.get('id')}, {'$set': item}, True)

        return item

# ---------- Time_Pipeline ----------
class TimePipeline():
    def process_item(self, item, spider):
        now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        item['crawled_at'] = now
        return item

# ---------- Weibo_Pipeline ----------
class WeiboPipeline():

    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime(DATETIME_FORMAT, time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime(DATETIME_FORMAT, time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime(DATETIME_FORMAT, time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime(DATE_FORMAT, time.localtime(time.time() - float(24) * 60 * 60)) + ' ' + date
        if re.match('今天.*', date):
            date = re.match('今天(.*)', date).group(1).strip()
            date = time.strftime(DATE_FORMAT, time.localtime()) + ' ' + date
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00'
        if re.match('\d+月\d+日', date):
            date = date.replace('月', '-').replace('日', '')
            date = time.strftime("%Y-", time.localtime()) + date
        return date

    def process_item(self, item, spider):
        if isinstance(item, WeibocnItem) or isinstance(item, WeibocnSleepItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))

            if item.get('pictures'):
                item['pictures'] = [pic.get('url') for pic in item.get('pictures')]

            if item.get('text'):
                item['text'] = re.sub('<span.*?>|</span>|<img.*?>|<br />|<a.*?>|</a>', '', item.get('text')).strip()
            if item.get('raw_text'):
                item['raw_text'] = re.sub('<span.*?>|</span>|<img.*?>|<br />|<a.*?>|</a>', '', item.get('raw_text')).strip()

            if item.get('content'):
                item['content'] = item['content'].lstrip(':').strip()

            if item.get('info'):
                for info in item.get('info'):
                    if re.match('昵称:', info):
                        item['user'] = re.search('昵称:(.*)', info).group(1)
                    if re.match('性别:', info):
                        item['gender'] = re.search('性别:(.*)', info).group(1)
                    if re.match('生日:', info):
                        item['birthday'] = re.search('生日:(.*)', info).group(1)
                    if re.match('地区:', info):
                        item['location'] = re.search('地区:(.*)', info).group(1)
                    if re.match('简介:', info):
                        item['brief'] = re.search('简介:(.*)', info).group(1)
                    if re.match('感情状况:', info):
                        item['location'] = re.search('感情状况:(.*)', info).group(1)
                    if re.match('认证:', info):
                        item['verify'] = re.search('认证:(.*)', info).group(1)
                    if re.match('达人:', info):
                        item['favor'] = re.search('达人:(.*)', info).group(1)

        return item










