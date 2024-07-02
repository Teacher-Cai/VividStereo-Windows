import json
import threading
import os

import playsound
import time
import numpy as np
import socket


class Job(threading.Thread):

    def __init__(self, job):
        super().__init__()
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.run_program = job

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            self.run_program()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

    def giveMeProgram(self, program):
        self.run_program = program


def load_config():
    if os.path.exists('VividStereo.config'):
        with open('VividStereo.config', 'r') as f:
            config = f.read()
        if config:
            return json.loads(config)
        else:
            return {}
    else:
        return {}


def write_config(json_file):
    with open('VividStereo.config', 'w') as f:
        f.write(json.dumps(json_file))


def use_playsound_play_music(file_path):
    playsound.playsound(file_path)


def delayMsecond(t):
    """
    high precision delay function
    :param t: delay millisecond
    :return:
    """
    if t <= 0:
        return
    start, end = 0, 0
    start = time.time_ns()  # 精确至ns级别
    while end - start < t * 1000000:
        end = time.time_ns()


def get_local_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip


if __name__ == '__main__':
    res = []
    for _ in range(10):
        ts1 = time.time()
        delayMsecond(1000)
        tmp = time.time() - ts1
        print(tmp)
        res.append(tmp)

    print(np.mean(res), np.std(res))
