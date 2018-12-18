# -*- coding: utf-8 -*-

"""
@author: dong.lu

@contact: ludong@cetccity.com

@software: PyCharm

@file: train.py

@time: 2018/11/15 14:18

@desc: 训练模型参数

"""
import time

from sklearn.ensemble import RandomForestClassifier

from src.linefile import Fileiter, prec
from src.phrase import PhraseMine, QualityPhrase


def precess(text):
    return text.strip().split(' ')

corpus = Fileiter(r'..\data\分类数据_training.csv', precessfunc= prec, encode='utf8', end=5000)

pm = PhraseMine()
pm.statistics(corpus)
pm.pick_chars()
pm.pick_phrases()

pm.calculate_phrase()
pm.save_model('..\model')
b = time.time()


pm = PhraseMine.load_model(r'..\model\phrase_model_20181217180354.pkl')

train_phrase = []
data = Fileiter(r'..\data\sample.txt', start=0, precessfunc=precess, encode='utf8')
for i in data:
    train_phrase.append(i)

qp = QualityPhrase()
shuffle_x, shuffle_y = qp.obtain_train_phrase(train_phrase, pm.phrases_ls)

clf = RandomForestClassifier(max_depth=3, n_estimators=20,random_state=0)
clf.fit(shuffle_x, shuffle_y)

qp.model = clf

good_phrase, bad_phrase = qp.predict_prob(pm.phrases_ls.keys(), pm.phrases_ls)
print(good_phrase, bad_phrase)
