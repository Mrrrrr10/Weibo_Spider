# -*- coding: utf-8 -*-

import re
import pymongo
import numpy as np
import matplotlib.pyplot as plt
from snownlp import SnowNLP
from pyecharts import Pie, Map
from collections import Counter
from Weibo_Spider.Weibo_Spider import settings

class Analysis(object):
    def __init__(self):
        client = pymongo.MongoClient(host=settings.MONGODB_HOST, port=settings.MONGODB_PORT)
        self.db = client[settings.MONGODB_DBNAME]
        self.collection = self.db.WeibocnSleepItem

    def takeFirst(self, elem):
        return elem[0]

    def start(self):
        # self.age()
        # self.sleep_time()
        # self.location()
        # self.gender()
        self.weibo()

    def age(self):
        """分析发布微博信息含有“晚安”的用户的年龄段，并且数据可视化"""
        # 由于部分用户生日是xx座，这样导致我们无法分析用户年龄，所以必须过滤掉，
        # 同时也过滤掉年龄造假、故意恶作剧的用户
        # 计算规则：年龄小于60且大于14周岁(14周岁微博官方规定最低年龄)
        cursor = self.collection.find({"birthday": {"$in": [re.compile("\d+")], "$ne": None}}, {"birthday": 1, "_id": 0})
        birthday = list(filter(lambda x: x.startswith('1') or x.startswith('2'), [birthday.get('birthday') for birthday in cursor]))
        age = [birth.split('-')[0] for birth in birthday if (2018 - int(birth.split('-')[0])) <= 60 and 2018 - int(birth.split('-')[0]) >= 14]

        filed, attr = [], []
        counter = Counter()
        for year in age:
            counter[year] += 1
        rank = counter.most_common()
        rank.sort(key=self.takeFirst)   # 对年份进行排序
        for k, v in rank:
            filed.append(k)
            attr.append(v)

        pie = Pie()
        pie.add("", filed, attr,  radius=[50, 75], label_text_color=None, is_label_show=True, legend_orient="vertical", legend_pos="left",)
        pie.render("age.html")

    def sleep_time(self):
        """分析发布微博信息含有“晚安”的用户的开始睡觉时间，并且数据可视化"""
        # 只分析21：00至次日06：00的用户
        sleep = ["21", "22", "23", "00", "01", "02", "03", "04", "05", "06"]
        cursor = self.collection.find({}, {"created_at": 1, "_id": 0})
        created_at = [created_at.get('created_at') for created_at in cursor]
        created_at = [sleep_time.split()[1].split(":")[0] for sleep_time in created_at if sleep_time.split()[1].split(":")[0] in sleep]

        filed, attr = [], []
        counter = Counter()
        for time in created_at:
            counter[time] += 1
        rank = counter.most_common()
        rank.sort(key=self.takeFirst)
        for k, v in rank:
            filed.append(k + "点")
            attr.append(v)

        pie = Pie()
        pie.add("", filed, attr, center=[50, 50], radius=[30, 75], rosetype="area", is_random=True, is_legend_show=False, is_label_show=True,)
        pie.render("sleep_time.html")

    def location(self):
        """分析发布微博信息含有“晚安”的用户的所在省级单位，并且数据可视化"""
        cursor = self.collection.find({}, {"location": 1, "" "_id": 0})
        # 去掉 地区="其他" 和 "None"
        location = [location.get('location') for location in cursor if location.get('location') != "其他" and location.get('location')]
        # 去掉 海外用户
        location = [loc for loc in location if "海外" not in loc]
        # 获取省、直辖市
        location = [loc.split()[0] for loc in location if " " in loc]

        filed, attr = [], []
        counter = Counter()
        for loc in location:
            counter[loc] += 1
        for k, v in counter.most_common():
            filed.append(k)
            attr.append(str(int(v)/10))

        map = Map("", width=1200, height=600)
        map.add("", filed, attr, maptype="china", is_visualmap=True, visual_text_color="#000", is_map_symbol_show=False, )

        map.render("location.html")

    def gender(self):
        """分析发布微博信息含有“晚安”的用户性别，并且数据可视化"""
        cursor = self.collection.find({}, {"gender": 1, "_id": 0})
        gender = [gender.get('gender') for gender in cursor if gender]

        filed, attr = [], []
        counter = Counter()
        for g in gender:
            counter[g] += 1
        for k, v in counter.most_common():
            filed.append(k)
            attr.append(v)

        pie = Pie()
        pie.add("", filed, attr, is_label_show=True, )
        pie.render("gender.html")

    def weibo(self):
        """分析发布微博信息含有“晚安”的微博进行情感分析"""
        cursor = self.collection.find({}, {"content": 1, "_id": 0})
        weibos = list(filter(None, [item.get('content') for item in cursor]))
        sentiments_list = [SnowNLP(weibo).sentiments for weibo in weibos]
        plt.hist(sentiments_list, bins=np.arange(0, 1, 0.02))
        plt.show()

if __name__ == '__main__':
    analysis = Analysis()
    analysis.start()







