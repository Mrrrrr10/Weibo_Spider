# -*- coding: utf-8 -*-
import re
import scrapy
from urllib.parse import quote
from scrapy.http import Request, FormRequest
from ..items import WeibocnSleepItem


class WeiboSearchSpider(scrapy.Spider):
    name = 'weibo_sleep'
    allowed_domains = ['weibo.cn']
    search_url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword={keyword}&advancedfilter=1&sort=time'
    user_url = "https://weibo.cn/{uid}/info"

    key_word = ['晚安']
    max_page = 200

    def start_requests(self):
        for keyword in self.key_word:
            url = self.search_url.format(keyword=quote(keyword))
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
            flag = 1 if is_forward else 0  # 1:转发微博 0:原创微博
            if not flag:
                detail_url = weibo.xpath('.//a[contains(., "评论[")]//@href').extract_first()
            else:
                detail_url = weibo.xpath('.//a[contains(., "转发[")]//@href').extract_first()
            print(detail_url)
            source = weibo.xpath('.//span[@class="ct"]//a//text()').extract_first(default=None)
            yield Request(url=detail_url, callback=self.parse_detail, meta={'source': source, 'flag': flag})

    def parse_detail(self, response):
        url = response.url
        flag = response.meta.get('flag')
        if flag:
            id = re.search('repost\/(.*?)\?', response.url).group(1)
            is_pic = response.xpath('//div[@id="M_"]/div[3]')
            if is_pic:
                # 转发带图片
                content = is_pic.xpath('./text()').extract_first()
            else:
                # 转发不带图片
                content = response.xpath('//div[@id="M_"]/div[2]/text()').extract_first()
        else:
            id = re.search('comment\/(.*?)\?', response.url).group(1)
            content = ''.join(response.xpath('//div[@id="M_"]//span[@class="ctt"]//text()').extract())
        comment_count = response.xpath('//span[@class="pms"]//text()').re_first('评论\[(.*?)\]')
        forward_count = response.xpath('//a[contains(., "转发[")]//text()').re_first('转发\[(.*?)\]')
        like_count = response.xpath('//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]')
        created_at = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
        source = response.meta.get('source')
        filed_map = {
            'id': id, 'url': url, 'content': content,
            'comment_count': comment_count, 'forward_count': forward_count,
            'like_count': like_count, 'created_at': created_at, 'source': source

        }
        uid = response.xpath('//input[@name="srcuid"]/@value').extract_first()
        yield Request(url=self.user_url.format(uid=uid), callback=self.parse_user,
                      meta={'filed_map': filed_map, 'uid': uid})

    def parse_user(self, response):
        filed_map = response.meta.get('filed_map')
        weibo_item = WeibocnSleepItem()
        uid = response.meta.get('uid')
        user_url = response.url
        info = response.xpath('//body/div[7]/text()').extract()
        filed_map.update({
            'uid': uid, 'user_url': user_url, 'info': info
        })

        for filed, attr in filed_map.items():
            weibo_item[filed] = attr

        yield weibo_item
