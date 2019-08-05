# Weibo_Spider
**基于scrapy的微博爬虫**

## 说明：
上一个微博爬虫[WeiboList_Spider](https://github.com/Mrrrrr10/WeiboList_Spider)不需要登陆，但会导致用户的粉丝、评论数据不全，这次的微博爬虫数据可以说是很完整的，这次需要用到selenium进行登陆，总所周知，微博weibo.cn登陆，如果是异常号就需要四宫格验证码，解决方案为：[CrackWeiboSlide](https://github.com/Python3WebSpider/CrackWeiboSlide)，具体的思路是将所有验证模板保存下来，然后进行一一匹配，利用selenium进行四宫格滑动。
1. selenium登陆weibo.cn，保存cookie到redis，维护一个cookie池
2. cookie池随机选择一个cookie进行爬取指定用户的用户信息以及该用户发布的微博信息
3. 存储在mongodb，并且利用mongodb相关api在pipeline.py文件进行数据去重和增量更新
4. 对爬取的数据进行用户行为数据清洗、文本分析、情感分析、可视化操作
5. 这次我写了两个爬虫，一个是爬取有关于电影《无双》的微博，一个是持续抓取好多天关于微博用户睡觉时间的微博

## 用法：
```
scrapy crawl weibo
scrapy crawl weibo_sleep
```

## 数据分析、可视化：
1. 微博用户对于《无双》的情感分析

![Result1](https://github.com/Mrrrrr10/Weibo_Spider/blob/master/Data_Analysis/weibo/%E7%94%A8%E6%88%B7%E6%83%85%E6%84%9F%E5%88%86%E6%9E%90.png)

2. 微博含有“晚安”的微博用户年龄分布

![Result1](https://github.com/Mrrrrr10/Weibo_Spider/blob/master/Data_Analysis/weibo_sleep/age.png)

3. 性别

![Result1](https://github.com/Mrrrrr10/Weibo_Spider/blob/master/Data_Analysis/weibo_sleep/gender.png)

4. 用户地理位置

![Result1](https://github.com/Mrrrrr10/Weibo_Spider/blob/master/Data_Analysis/weibo_sleep/location.png)

5. 睡觉时间点

![Result1](https://github.com/Mrrrrr10/Weibo_Spider/blob/master/Data_Analysis/weibo_sleep/time.png)
