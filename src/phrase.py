# -*- coding: utf-8 -*-

"""
@author: dong.lu

@contact: ludong@cetccity.com

@software: PyCharm

@file: phrase.py

@time: 2018/11/15 14:18

@desc: 从大量语料中统计预选短语的
`
"""
import math
from collections import Counter

import numpy as np

from src.linefile import persistence


class PhraseMine(object):
    def __init__(self, alpha=0., unk_num=0, unk_idf=0, min_token=5, sample_list=True):
        self.sample_list = sample_list

        # char在全文的数量
        self.chars = Counter()
        # phrase在全文的数量
        self.phrases = Counter()
        # char的文档频数
        self.df = Counter()
        # 文档集的总数
        self.docs = 0

        self.min_token = min_token

        self.alpha = alpha
        self.unk_num = unk_num
        self.unk_idf = unk_idf
        self.pmi = {}
        self.plk = {}
        self.char_idf = {}
        self.phrase_idf = {}

        self.phrases_ls = {}

    def seg_sentence(self, sentence):
        self.chars.update(sentence)

        phrases = []

        for i, cw in enumerate(sentence):
            if i < len(sentence) and cw != '|':
                substring = sentence[i+1:]
                for j, sw in enumerate(substring, 1):
                    if sw != '|':
                        tmp = cw + substring[:j]
                        phrases.append(tmp)
                    else:
                        break

        self.phrases.update(phrases)

    def statistics(self, sentences):
        for sentence in sentences:
            self.df.update(set(sentence))
            self.docs += 1
            self.seg_sentence(sentence)

    def _get_token(self, chars_phrases, min_token=None, top=None):
        if not top:
            return dict(chars_phrases.most_common(top))
        elif min_token:
            return {
                word: num for word, num in chars_phrases.items() if num >= min_token
            }
        else:
            return {
                word: num for word, num in chars_phrases.items() if num >= self.min_token
            }

    def pick_chars(self, min_char=None, top=None):
        self.chars = self._get_token(self.chars, min_token=min_char, top=top)

    def pick_phrases(self, min_phrase=None, top=None):
        self.phrases = self._get_token(self.phrases, min_token=min_phrase, top=top)

    def _prob_u(self, phrase):
        accumulate = 0
        for char in phrase:
            accumulate += self.chars.get(char, self.unk_num)

        if len(phrase) > 1:
            return self.phrases[phrase] * 1. / accumulate
        else:
            return 1

    def _phrase_pmi_plk(self, phrase):
        prob_whole = self._prob_u(phrase)

        if len(phrase) > 2:
            min_mutual_info = float('inf')
            best_left = None
            best_right = None

            for i in range(len(phrase)):
                u_left = phrase[:i]
                u_right = phrase[i:]
                info = math.log(prob_whole * 1. / (self._prob_u(u_left) * self._prob_u(u_right)))

                if info < min_mutual_info:
                    min_mutual_info = info
                    best_left = u_left
                    best_right = u_right

        else:
            best_left = phrase[0]
            best_right = phrase[1]

        phrase_pmi = math.log(prob_whole * 1. / (self._prob_u(best_left) * self._prob_u(best_right)))
        phrase_plk = prob_whole * math.log(prob_whole * 1. / (self._prob_u(best_left) * self._prob_u(best_right)))

        if self.sample_list:
            self.phrases_ls[phrase] = [phrase_pmi]
            self.phrases_ls[phrase].append(phrase_plk)
        else:
            self.pmi[phrase] = phrase_pmi
            self.plk[phrase] = phrase_plk

    def calculate_char_idf(self):
        for char, count in self.df.items():
            self.char_idf[char] = math.log(self.docs + self.alpha) - math.log(count + self.alpha)
        # kv = list(zip(*self.df.items()))
        # key, value = kv[0], np.array(kv[1])
        # value = np.log((self.docs + self.alpha)) - np.log(value + self.alpha)
        # self.df = dict(zip(key, value))

    def average_phrase_idf(self, phrase):
        idf = 0
        for char in phrase:
            idf += self.char_idf.get(char, self.unk_idf)

        idf = idf * 1.0 / len(phrase)

        if self.sample_list:
            self.phrases_ls[phrase].append(idf)
        else:
            self.phrase_idf[phrase] = idf

    def calculate_phrase(self):
        self.calculate_char_idf()

        for phrase in self.phrases:
            self._phrase_pmi_plk(phrase)
            self.average_phrase_idf(phrase)

    def get_sample(self, phrase):
        if not self.sample_list:
            return [self.pmi[phrase], self.plk[phrase], self.phrase_idf[phrase]]
        else:
            return self.phrases_ls[phrase]

    def save_model(self, path):
        persistence(self, path, 'phrase_model', 'save')

    @classmethod
    def load_model(cls, path):
        return persistence(path, 'load')


class QualityPhrase(object):
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model:
            raise AttributeError('QualityPhrase object have not model!')

        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @classmethod
    def mapping_data(cls, phrases, phd):
        return list(map(lambda x: phd.get(x[0], [0] * 3), phrases))

    def obtain_train_phrase(self, train_phrases, phd):
        x = self.mapping_data(train_phrases, phd)
        y = list(map(lambda label: int(label[1]), train_phrases))
        shuffle = np.random.permutation(len(train_phrases))
        shuffle_x = np.array(x)[shuffle]
        shuffle_y = np.array(y)[shuffle]

        return shuffle_x, shuffle_y

    @classmethod
    def separate_data(cls, x, y, ratio=0):
        assert len(x) == len(y)

        if ratio:
            return x, y

        split_idx = int(len(x) * ratio)
        train_x, test_x = x[:split_idx], x[split_idx:]
        train_y, test_y = y[:split_idx], y[split_idx:]

        return train_x, test_x, train_y, test_y

    def predict_prob(self, test_phrases, phd):
        test_x = list(map(lambda x: phd[x], test_phrases))
        predict_data = self._model.predict_proba(test_x)

        good_phrase, bad_phrase = [], []

        for ind, phrase in enumerate(test_phrases):
            if predict_data[ind][1] >= 0.7:
                good_phrase.append(phrase)

            else:
                bad_phrase.append(phrase)

        return good_phrase, bad_phrase

    def save_model(self, path):
        persistence(self.model, path, 'classifier_model', 'save')

    @classmethod
    def load_model(cls, path):
        return persistence(path, 'load')
