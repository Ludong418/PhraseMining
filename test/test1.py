import os, time
from collections import Counter

from multiprocessing import Process,Value,Lock, Pool

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

        return self.count


if __name__ == '__main__':
    start = time.time()
    string = [['引擎负责控制数据流在系统中所有组件中流动，并在相应动作发生时触发事件'] * 111100, ['初始的爬取URL和后续在页面中获取的待爬取的URL将放入调度器中'] * 111100,
              ['下载器负责获取页面数据并提供给引擎，而后提供给spider'] * 111100]
    ts = Test()
    result = []

    pool = Pool(processes=3)
    for i in string:
        a = pool.apply_async(ts.doubler, args=(i,))
        result.append(a)

    pool.close()
    pool.join()

    tmp = Counter()
    for i in result:
        tmp.update(i.get())
    print(tmp)
    print(time.time() - start)
