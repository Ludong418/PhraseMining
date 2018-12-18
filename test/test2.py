import os, time
from collections import Counter

from multiprocessing import Process,Value,Lock, Pool
from multiprocessing.managers import BaseManager


from jieba import lcut


class Test(object):
    def __init__(self):
        self.count = Counter()

    def doubler(self, string):
        """
        A doubling function that can be used by a process
        """
        for i in string:
            ls = lcut(i)
            self.count.update(ls)

    def a(self):
        return self.count

class MyManager(BaseManager):
    pass

def Manager2():
    m=MyManager()
    m.start()
    return m

MyManager.register('Test',Test)

def func1(ts,lock, i):
    with lock:
        ts.doubler(i)

if __name__ == '__main__':
    start = time.time()
    string = [['引擎负责控制数据流在系统中所有组件中流动，并在相应动作发生时触发事件'] * 111100, ['初始的爬取URL和后续在页面中获取的待爬取的URL将放入调度器中'] * 111100, ['下载器负责获取页面数据并提供给引擎，而后提供给spider'] * 111100]
    manager = Manager2()
    ts = manager.Test()

    lock = Lock()

    proces = [Process(target=func1, args=(ts, lock, i, )) for i in string]
    for p in proces:
        p.start()
    for p in proces:
        p.join()

    print(ts.a())

    # ts = Test()
    # for s in string:
    #     ts.doubler(s)
    #
    # print(ts.a())
    print(time.time() - start)

