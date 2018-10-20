# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# ---------- Item_WeiboSleepItem ----------
class WeibocnSleepItem(scrapy.Item):
    id = scrapy.Field()
    uid = scrapy.Field()
    url = scrapy.Field()
    user_url = scrapy.Field()
    content = scrapy.Field()
    comment_count = scrapy.Field()
    forward_count = scrapy.Field()
    like_count = scrapy.Field()
    created_at = scrapy.Field()
    user = scrapy.Field()
    source = scrapy.Field()
    info = scrapy.Field()
    gender = scrapy.Field()
    birthday = scrapy.Field()
    location = scrapy.Field()
    brief = scrapy.Field()
    verify = scrapy.Field()
    favor = scrapy.Field()
    crawled_at = scrapy.Field()


# ---------- Item_WeibocnItem ----------
class WeibocnItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    comment_count = scrapy.Field()
    forward_count = scrapy.Field()
    like_count = scrapy.Field()
    created_at = scrapy.Field()
    user = scrapy.Field()
    source = scrapy.Field()
    crawled_at = scrapy.Field()
