# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import json
import redis
import base64
import random
import hashlib
import logging
import requests
import pymongo
from scrapy import signals
from scrapy.conf import settings
from urllib.parse import urlparse
from scrapy.http import HtmlResponse  # HtmlResponse就会让下载器不再去请求,直接把请求结果发往spider
from fake_useragent import UserAgent
# from .cookie import init_cookie
from twisted.internet import defer
from scrapy.exceptions import IgnoreRequest
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, ConnectionLost, TCPTimedOutError


class WeiboSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeiboSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# ------------- 动态设置ip代理的Middleware -------------
class RandomProxyMiddleware(object):
    def __init__(self, proxy_pool_url, http_proxy):
        self.proxy_pool_url = proxy_pool_url
        self.http_proxy = http_proxy
        self.logger = logging.getLogger(__name__)
        self.cnt = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('PROXY_POOL_URL'), crawler.settings.get('HTTP_PROXY'))

    def process_request(self, request, spider):
        def get_proxy():
            try:
                response = requests.get(self.proxy_pool_url)
                if response.status_code == 200:
                    return response.text
            except ConnectionError:
                return None

        request.meta['proxy'] = "http://{0}".format(get_proxy())
        self.logger.debug('Using Proxy')


# ------------- SeleniumCookieMiddleware -------------
class SeleniumCookieMiddleware(object):
    def __init__(self, host, port):
        self.logger = logging.getLogger(__name__)
        self.cookie_db = redis.Redis(host, port, db=4, decode_responses=True)
        self.keys = self.cookie_db.keys()  # list

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler.settings.get('REDIS_HOST'), crawler.settings.get('REDIS_PORT'))
        return s

    def process_request(self, request, spider):
        keys = list(filter(lambda x: 'cookie:weibo' in x, self.keys))
        key = random.choice(keys)

        cookie = json.loads(self.cookie_db.get(key))
        request.cookies = cookie
        self.logger.debug('Using Cookies' + json.dumps(cookie))

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 320, 303]:
            try:
                redirect_url = response.headers['location']
                if 'passport' in redirect_url:
                    self.logger.warning("Need Login, Updating Cookie")
                elif 'weibo.cn/security' in redirect_url:
                    self.logger.warning("Account is Locked!")
                keys = list(filter(lambda x: 'cookie:weibo' in x, self.keys))
                key = random.choice(keys)
                cookie = json.loads(self.cookie_db.get(key))
                request.cookies = cookie
                return request

            except:
                raise IgnoreRequest

        elif response.status in [414]:
            return request
        else:
            return response


# ------------- 随机更换UserAgent的Middleware -------------
class RandomUserAgentMiddleware(object):

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent(verify_ssl=False)
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault("User-Agent", get_ua())


