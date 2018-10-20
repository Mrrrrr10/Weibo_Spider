# -*- coding: utf-8 -*-
import re
import time
import scrapy
from urllib.parse import quote
from ..items import WeibocnItem
from scrapy.http import Request, FormRequest


class WeiboCnSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword={keyword}&advancedfilter=1&starttime=20180930&endtime={endtime}&sort=time'
    key_word = ['《无双》']
    max_page = 200

    def start_requests(self):
        endtime = time.strftime("%Y%m%d", time.localtime(time.time()))
        for keyword in self.key_word:
            url = self.search_url.format(keyword=quote(keyword), endtime=endtime)
            for page in range(self.max_page + 1):
                data = {
                    "mp": str(self.max_page),
                    "page": str(page)
                }
                yield FormRequest(url=url, formdata=data, callback=self.parse_index)

    def parse_index(self, response):
        """解析索引页"""
        weibos = response.xpath('//div[@class="c" and contains(@id, "M_")]')
        for weibo in weibos:
            is_forward = bool(weibo.xpath('.//span[@class="cmt"]').extract_first())
            if is_forward:
                # 转发微博
                detail_url = weibo.xpath('.//a[contains(., "原文评论[")]//@href').extract_first()  # . -> <a>
            else:
                # 原创微博
                detail_url = weibo.xpath('.//a[contains(., "评论[")]//@href').extract_first()
            print(detail_url)
            source = weibo.xpath('.//span[@class="ct"]//a//text()').extract_first(default=None)
            yield Request(url=detail_url, callback=self.parse_detail, meta={'source': source})

    def parse_detail(self, response):
        weibo_item = WeibocnItem()
        id = re.search('comment\/(.*?)\?', response.url).group(1)
        url = response.url
        content = ''.join(response.xpath('//div[@id="M_"]//span[@class="ctt"]//text()').extract())
        comment_count = response.xpath('//span[@class="pms"]//text()').re_first('评论\[(.*?)\]')
        forward_count = response.xpath('//a[contains(., "转发[")]//text()').re_first('转发\[(.*?)\]')
        like_count = response.xpath('//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]')
        created_at = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
        user = response.xpath('//div[@id="M_"]/div[1]/a[1]/text()').extract_first(default=None)
        source = response.meta.get('source')
        print(id, url, content, comment_count, forward_count, like_count, created_at, user, source)
        for filed in weibo_item.fields:
            try:
                weibo_item[filed] = eval(filed)  # 动态赋值,但是如果filed未定义,会抛出异常
            except NameError:
                self.logger.debug("filed is not defined：" + filed)
        yield weibo_item
