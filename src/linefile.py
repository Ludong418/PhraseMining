#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: dong.lu

@contact: ludong@cetccity.com

@software: PyCharm

@file: linefile.py

@time: 2018/08/16 10:30

@desc: 读取文件数据的迭代器，Fileiter类支持 .txt .csv，Xliter类支持 excel文件

"""
import re
import os
import time
import codecs
import itertools
import pickle

import xlrd

pattern = re.compile('[。.，,？：、；（）“”\-()《》【】"]')


def precesspass(sentence):
    """
    对单条文本不进行处理
    :param sentence: 输入文本，str
    :return: 输入文本,str
    """
    return sentence


def prec(sentence):
    """
    处理单条文本数据，处理内容由自己自定义
    :param sentence: 输入的单条文本，str
    :return: 处理后的文本
    """
    sentence = sentence.strip('\n\r').split(',')[1]
    return pattern.sub('|', sentence)


class FiletypeException(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
        print(self.msg)


class Fileiter(object):
    """
    类Fileiter是一个读取csv，txt的迭代器，可以自动识别文件后缀，读取过程中可以设置处理函数进行文件内容处理

    :arg
    filename 文件地址
    precessfunc 处理函数，为None时，调用prec()函数，表示不处理数据；也可以传入prec()函数进行自定义处理。
    start 读取开始下标为多少的数据
    end 读取结束小标为多少的数据
    encode 按什么方式编码
    errors 是否忽略错误，可选 ignore
    """
    def __init__(self, filename, precessfunc=None, start=None, end=None, encode=None, errors=None):
        self.filename = filename
        self.precessfunc = precesspass
        if precessfunc:
            self.precessfunc = precessfunc
        self.start = start
        self.end = end
        self.encode = encode
        self.errors = errors

    def __len__(self):
        return sum(1 for _ in self)

    def __iter__(self):
        _, ext = os.path.splitext(self.filename)
        if ext in ['.txt', '.csv', '.dat']:
            self.file = codecs.open(self.filename, 'r', encoding=self.encode, errors=self.errors)
            for line in itertools.islice(self.file, self.start, self.end):
                yield self.precessfunc(line)
        else:
            raise FiletypeException("File type is error,it must be '.csv' or '.txt'!")


class Xliter(object):
    """
    类Xliter是一个读取Excel文件的迭代器，方法和Fileiter相同

    :arg
    workname Excel文件地址
    sheets sheet的名称
    precessfunc 方法和Fileiter相同
    start 方法和Fileiter相同
    end 方法和Fileiter相同
    isall 是否读取全部的数据，若为True，star和end失效
    """
    def __init__(self, workname, sheets, precessfunc=None, start=0, end=1, isall=True):
        self.workname = workname
        self.sheets = sheets
        self.precessfunc = precesspass
        if precessfunc:
            self.precessfunc = precessfunc
        self.start = start
        self.end = end
        self.isall = isall

    def __iter__(self):
        _, ext = os.path.splitext(self.workname)
        if ext in ['.xls', '.xlsx']:
            data = xlrd.open_workbook(self.workname)
            for sheet in self.sheets:
                table = data.sheet_by_name(sheet)
                if self.isall:
                    self.end = table.nrows
                for row in range(self.start, self.end):
                    yield self.precessfunc(table.row_values(row))
        else:
            raise FiletypeException("File type is error,it must be '.xls' or '.xlsx'!")


def persistence(*args):
    """
    持久化对象或加载对象
    :param args: 持久化参数顺序(对象, 存储文件夹, 文件名标识,'save')
                 加载参数顺序(文件路径, 'load')
    :return:
    """
    if args[1] == 'load':
        f = open(args[0], 'rb')
        obj = pickle.load(f)
        return obj

    elif args[3] == 'save':
        path = args[1] + '\\' + args[2] + r'_{}.pkl'.format(
            time.strftime("%Y%m%d%H%M%S",
                          time.localtime()))
        f = open(path, 'wb')
        pickle.dump(args[0], f)
