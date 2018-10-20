# -*- coding: utf-8 -*-

# Scrapy settings for Weibo_Spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html


BOT_NAME = 'Weibo_Spider'

SPIDER_MODULES = ['Weibo_Spider.spiders']
NEWSPIDER_MODULE = 'Weibo_Spider.spiders'

# 是否遵守机器人协议
ROBOTSTXT_OBEY = False  # # False:不会过滤任何页面


# 配置Scrapy执行的最大并发请求（默认值：16）
# CONCURRENT_REQUESTS = 32


# ------ 下载延迟设置 ------
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# ------ 是否启用cookie,默认为不启用 ------
# COOKIES_ENABLED = False


# ------ 禁用Telnet控制台（默认启用） ------
# TELNETCONSOLE_ENABLED = False


# ------ 可在特定的爬虫spider文件设置 ------
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'weibo.cn',
    'X-Requested-With': 'XMLHttpRequest',
}

# ---------- Middleware ----------
# 启用或者禁用 spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'Weibo_Spider.middlewares.ScrapyProjectSpiderMiddleware': 543,
# }

# 启用或者禁用 downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'Weibo_Spider.middlewares.WeiboSpiderDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,     # 禁用scrapy原有的User-Agent
    'Weibo_Spider.middlewares.RandomUserAgentMiddleware': 300,
    # 'Weibo_Spider.middlewares.RandomProxyMiddleware': 554,        # Proxy Pool
    'Weibo_Spider.middlewares.SeleniumCookieMiddleware': 556,
}

RANDOM_UA_TYPE = "random"                           # todo:既可以选择浏览器又可以随机切换
PROXY_POOL_URL = 'http://localhost:5555/random'     # Proxy Pool

# -------------------------------------------------
# 启用或者禁用扩展
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#    'scrapy.extensions.closespider.CloseSpider': 500
# }
# CLOSESPIDER_TIMEOUT = 84600   # 爬虫运行超过23.5小时，如果爬虫还没有结束，则自动关闭


# 配置pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'Weibo_Spider.pipelines.TimePipeline': 300,
    'Weibo_Spider.pipelines.WeiboPipeline': 301,
    'Weibo_Spider.pipelines.MongoPipeline': 302,

}

# MongoDB数据库配置
MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DBNAME = 'Weibo'

# Redis
REDIS_URL = "redis://root:@127.0.0.1:6379"
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379


# 时间处理
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
GMT_FORMAT = "%a %b %d %H:%M:%S +0800 %Y"


RETRY_HTTP_CODES = [401, 403, 407, 408, 414, 500, 502, 503, 504]

