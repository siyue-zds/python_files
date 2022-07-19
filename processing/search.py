import threading

from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path


class FileSearchThread(QThread):
    sinOut = pyqtSignal(str)

    # 自定义信号，执行run()函数时，从相关线程发射此信号
    def __init__(self, path: str, file_name: str, thread_sum: int = 4, style: bool = True):
        """
        :param path: 目录路径
        :param file_name: 搜索文件关键字
        :param thread_sum: 线程数量
        :param style: 搜索模式：True:按文件名查找、False:文件内容查找
        """

        super(FileSearchThread, self).__init__()
        self.path = Path(path)
        self.key_word = file_name
        self.thread_sum = thread_sum
        self.style = style

    def run(self):

        # 线程列表
        threads = []
        # 目录下文件数量
        files = [file for file in self.path.iterdir()]
        count = len(files)
        # 每个线程遍历的文件
        num = int(count / 4) + 1
        # 通过多线程对文件的遍历查找
        for i in range(0, count, num):
            t = threading.Thread(target=self.search,
                                 args=(self.style, self.key_word, files[i:(i + num if i + num < count else count)]))
            threads.append(t)
            t.start()
        for i in range(len(threads)):  # 将主线程阻塞
            threads[i].join()

    def search(self, style: bool, key_word: str, files: list):
        if style:
            # 按文件名查找
            for file in files:
                if file.is_file():
                    # 文件
                    if file.name.__contains__(key_word):
                        self.sinOut.emit(str(file))
                elif file.is_dir():
                    # 文件夹
                    if file.name.__contains__(key_word):
                        self.sinOut.emit(str(file))
                    # 文件夹
                    for path in file.glob(f'**/*{key_word}*'):
                        self.sinOut.emit(str(path))
        else:
            # 文件内容查找
            folders = []
            for file in files:
                if file.is_file() and file.suffix == '.txt':
                    # 搜索txt文件
                    import re  # 引用re模块
                    file_txt = open(str(file), "r")
                    # re.findall()返回的是一个列表
                    content = file_txt.read()
                    file_txt.close()
                    if not len(re.findall(key_word, content)) == 0:
                        self.sinOut.emit(str(file))
                elif file.is_dir():
                    # 文件夹，递归遍历
                    # folders.append(file)
                    self.search(style, key_word, [file for file in file.iterdir()])
