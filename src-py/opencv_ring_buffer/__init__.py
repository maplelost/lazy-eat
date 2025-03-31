"""
Author:https://github.com/Calcifer97
Url:https://github.com/Calcifer97/OpencvRingBuffer/blob/master/OpencvRingBuffer.py
"""
import threading
import time


# 让opencv实时的从摄像头读取数据，不实时的原因是opencv自带缓冲区，
# 而且缓冲区的刷新时间是不可预知的，当算法运行跟不上摄像头的帧率时，
# opencv会返回旧的帧，导致不是实时，可以用这个类帮助解决问题。

# 适用于复杂耗时算法且性能低的平台，如在树莓派上进行图像识别相关工作
class OpencvRingBuffer:
    def __init__(self, cap, ring_size=5):
        self.items = [0 for i in range(ring_size)]
        self.ring_size = ring_size  # 环形缓冲大小
        self.pos = 0  # 当前最新数据的位置
        self.ready = 0  # 第一帧是否完成
        self.lock = threading.RLock()  # 锁
        self.cap = cap  # cv2.VideoCapture(0)对象
        self.thread = threading.Thread(target=self.run, daemon=True)  # 控制线程
        self.stopflag = 0  # 安全停止线程

    def startcap(self):  # 开启捕捉
        self.stopflag = 0
        self.thread.start()

    def stopcap(self):  # 停止捕捉
        self.stopflag = 1

    def run(self):  # 线程
        while (self.stopflag == 0):
            ret, img = self.cap.read()
            if (ret):
                self.push(img)
            else:
                print("请检查摄像头\n")
                time.sleep(0.5)

        # release
        self.cap.release()

    def push(self, img):
        self.lock.acquire()
        self.pos = self.pos + 1
        if (self.pos > self.ring_size - 1):  # 循环放置
            self.pos = 0
        self.items[self.pos] = img
        self.ready = 1
        self.lock.release()
        # print("push")

    def getnew(self):  # 返回格式和cap.read()一致
        ret = 1
        if (self.ready == 0):
            ret = 0
        self.lock.acquire()
        img = self.items[self.pos]
        self.lock.release()
        # print("get")
        return ret, img
