import socket
import time
import numpy as np
from global_info import GlobalInfo
import json


# TCP连接
def receive_message():
    # 创建 socket
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # AF_INET IPv4；AF_INET6 IPv6；SOCK_STREAM 数据流，面向连接的(TCP)； SOCK_DGRAM 数据报，无连接的(UDP)

    # 配置ip和端口
    host = socket.gethostname()  # 本地计算机名
    ip = socket.gethostbyname(host)   # 获取本地IP
    port = 2022  # 设置可用端口

    # 绑定ip和端口
    tcp_server.bind((ip, port))    # bind函数绑定端口，有两个括号是因为参数传入的是元组，其中包含IP和端口号

    # 监听
    tcp_server.listen(2)   # 2(int)参数为backlog,代表同时最多接收n个客户端的连接申请

    #  accept函数等待连接，若连接成功返回conn和address， conn为新的套接字用于连接后的消息传输，address 连接上的客户端的地址
    conn, addr = tcp_server.accept()
    print(addr, "连接上了")

    # 单次接收处理
    data = conn.recv(1024)   # 接收数据，1024 -- bufsize参数为接收的最大数据量
    print(data.decode())  # 以字符串编码解析
    # decode函数 解码：将接收到的bytes类型二进制数据转换为str类型
    conn.send("ok".encode())  # 发送数据给客户端
    # encode函数 编码：将str类型转为bytes类型二进制数据去传输

    # 循环接收处理
    '''
    while True:
        data = conn.recv(1024)  
        if not data:
            print("消息已读完")
            break
        operation = data.decode() 
        print(operation)
        conn.send("ok".encode())
    
    '''
    tcp_server.close()  # 关闭套接字


def send_message(pre_set_ts, tcpClient):
    data = '{}\r\n'.format(pre_set_ts).encode("utf-8")  # 报文数据，bytes类型
    tcpClient.send(data)  # 发送数据给客户端据给服务端


def get_absolute_time_diff(tcpClient):
    timediff = []
    data = 'return\r\n'.encode("utf-8")  # 报文数据，bytes类型

    for i in range(100):
        tcpClient.send(data)  # 发送数据给客户端据给服务端
        tsMillsStart = time.time() * 1000
        msg = tcpClient.recv(1024)  # 接收来自服务端的数据，小于1024字节
        tsMillsEnd = time.time() * 1000
        mess = msg.decode('utf-8')
        if mess.endswith('\r\n'):
            mess = mess.replace('\r\n', '')
        transferTime = tsMillsEnd - tsMillsStart
        estimateTimeDiff = tsMillsEnd - int(mess) - transferTime / 2
        if transferTime < 10:
            timediff.append(estimateTimeDiff)
    absolute_time_diff = np.mean(timediff)
    print("绝对时差", absolute_time_diff, np.std(timediff), len(timediff))
    return absolute_time_diff


def multi_loop_send_and_receive():
    """
    estimate absolute time gap between devices
    :return:
    """
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象
    # tcpClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    addr = ('192.168.0.102', 4000)
    addr1 = ('192.168.0.107', 4000)
    tcpClient1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象

    tcpClient.connect(addr)  # 连接服务，指定主机和端口号
    tcpClient1.connect(addr1)
    res = []
    timediff = []
    data = 'return\r\n'.encode("utf-8")  # 报文数据，bytes类型

    for i in range(50):
        tcpClient.send(data)  # 发送数据给客户端据给服务端
        tsMillsStart = time.time() * 1000
        msg = tcpClient.recv(1024)  # 接收来自服务端的数据，小于1024字节
        tsMillsEnd = time.time() * 1000
        mess = msg.decode('utf-8')
        transferTime = tsMillsEnd - tsMillsStart
        estimateTimeDiff = tsMillsEnd - int(mess) - transferTime / 2
        print(mess, 'tsMillsdiff:', transferTime, estimateTimeDiff)
        res.append(transferTime)
        if transferTime < 10:
            timediff.append(estimateTimeDiff)

    print("通信时间", sum(res)/len(res), max(res), min(res), np.std(res))
    print("绝对时差", np.mean(timediff), np.std(timediff), len(timediff))
    print("="*50)
    res.clear()
    timediff.clear()
    for i in range(50):
        tcpClient1.send(data)  # 发送数据给客户端据给服务端
        tsMillsStart = time.time() * 1000
        msg = tcpClient1.recv(1024)  # 接收来自服务端的数据，小于1024字节
        tsMillsEnd = time.time() * 1000
        mess = msg.decode('utf-8')
        transferTime = tsMillsEnd - tsMillsStart
        estimateTimeDiff = tsMillsEnd - int(mess) - transferTime / 2
        print(mess, 'tsMillsdiff:', transferTime, estimateTimeDiff)
        res.append(transferTime)
        if transferTime < 10:
            timediff.append(estimateTimeDiff)

    print("通信时间", sum(res)/len(res), max(res), min(res), np.std(res))
    print("绝对时差", np.mean(timediff), np.std(timediff), len(timediff))


    # plt.hist(timediff, bins=30, density=True)
    # plt.xlabel('Value')
    # plt.ylabel('Probability')
    # plt.title('Density plot')
    # plt.show()

def udp_communication():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket.SOCK_DGRAM - udp
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(('', 4002))
    return udp_socket


def send_message_udp(pre_set_ts, target, upd_client):
    """

    :param pre_set_ts: json structure
    :param target: target ip
    :param upd_client: client instance
    :return:
    """
    data = pre_set_ts.encode("utf-8")  # 报文数据，bytes类型
    upd_client.sendto(data, (target, 4002))  # 发送数据给客户端据给服务端


def tcp_listener():
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(('', 4000))
    tcp_server_socket.listen(2)
    sender_client_socket, sender_aadr = tcp_server_socket.accept()
    print(sender_aadr)
    GlobalInfo.master_device = False
    while True:
        recv_data = sender_client_socket.recv(1024).decode('utf-8')
        if recv_data == 'return' or recv_data == 'return\r\n':
            sender_client_socket.send((str(int(time.time() * 1000)) + '\r\n').encode('utf-8'))


if __name__ == "__main__":
    # udp broadcast test
    udp_client = udp_communication()
    send_message_udp(json.dumps({'reason': 'get_ip_address', 'ip_address':"192.168.0.107"}), '255.255.255.255', udp_client)
