
import jieba
import pymongo
import numpy as np
from snownlp import SnowNLP
from collections import Counter
import jieba.posseg as posseg
import jieba.analyse as analyse
import matplotlib.pyplot as plt
from pyecharts import WordCloud
from Weibo_Spider.Weibo_Spider import settings

class Analysis(object):
    def __init__(self):
        client = pymongo.MongoClient(host=settings.MONGODB_HOST, port=settings.MONGODB_PORT)
        self.db = client[settings.MONGODB_DBNAME]
        self.collection = self.db.WeibocnItem

    def start(self):
        self.analysis_weibo()
        self.analysis_tf()
        self.extract_keyword()

    def analysis_weibo(self):
        """对电影《无双》进行用户的情感分析"""
        print("开始分析：%s" % self.__class__.analysis_weibo.__name__)
        count = self.collection.find().count()
        print("数据基数：%s" % count)
        cursor = self.collection.find({}, {"content": 1, "_id": 0})
        content = [item.get('content') for item in cursor]
        weibos = list(filter(lambda x: len(x) != 0, content))
        sentiments_list = [SnowNLP(weibo).sentiments for weibo in weibos]
        plt.hist(sentiments_list, bins=np.arange(0, 1, 0.02))
        plt.show()
        print("分析结束：%s" % self.__class__.analysis_weibo.__name__)

    def analysis_tf(self):
        """对电影《无双》微博进行词频分析，去停词，并且数据可视化"""
        print("开始分析：%s" % self.__class__.analysis_tf.__name__)
        count = self.collection.find().count()
        print("数据基数：%s" % count)
        cursor = self.collection.find({}, {"content": 1, "_id": 0})
        content = [item.get('content') for item in cursor]

        filed, attr, keywords = eval("[]," * 3)
        weibos = list(filter(lambda x: len(x) != 0, content))
        stop = [line.strip() for line in open('stop_words.txt', 'r', encoding='utf-8').readlines()]     # 加载停用词表
        jieba.load_userdict("userdict.txt")     # 导入自定义词典
        for weibo in weibos:
            segs = posseg.cut(weibo)
            for seg, flag in segs:
                if seg not in stop:
                    if flag != 'm' and flag != 'x':     # 去数词和去字符串
                        keywords.append(seg)            # 输出分词

        counter = Counter()
        for keyword in keywords:
            counter[keyword] += 1

        for word, rate in counter.most_common(50):
            filed.append(word)
            attr.append(rate)

        """制作词云图"""
        wordcloud = WordCloud(width=1300, height=620)
        wordcloud.add("电影《无双》词频统计", filed, attr, word_size_range=[30, 100], shape='diamond')
        wordcloud.render("Word_Frequency_Count.html")
        print("分析结束：%s" % self.__class__.analysis_tf.__name__)

    def extract_keyword(self):
        """对电影《无双》微博进行关键词提取，并且数据可视化"""
        print("开始分析：%s" % self.__class__.extract_keyword.__name__)
        count = self.collection.find().count()
        print("数据基数：%s" % count)
        cursor = self.collection.find({}, {"content": 1, "_id": 0})
        content = [item.get('content') for item in cursor]
        weibos = list(filter(lambda x: len(x) != 0, content))
        jieba.load_userdict("userdict.txt")  # 导入自定义词典

        filed, attr, keywords = eval("[]," * 3)
        for weibo in weibos:
            for x in jieba.analyse.extract_tags(weibo, withWeight=False, topK=3):
                keywords.append(x)

        counter = Counter()
        for keyword in keywords:
            counter[keyword] += 1

        for word, count in counter.most_common(50):
            filed.append(word)
            attr.append(count)

        """制作词云图"""
        wordcloud = WordCloud(width=1300, height=620)
        wordcloud.add("电影《无双》关键词统计", filed, attr, word_size_range=[30, 100], shape='diamond')
        wordcloud.render("Word_Keyword_Count.html")
        print("分析结束：%s" % self.__class__.extract_keyword.__name__)

if __name__ == '__main__':
    analysis = Analysis()
    analysis.start()
















