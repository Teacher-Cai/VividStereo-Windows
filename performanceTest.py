import socket
import time
import numpy as np
from global_info import GlobalInfo
import json
from matplotlib import pyplot as plt
from synchronize import send_message_udp, udp_communication
import seaborn as sea

count_ave = []
upd_client = udp_communication()


def multi_loop_send_and_receive():
    """
    estimate absolute time gap between devices
    :return:
    """
    send_message_udp(json.dumps({'reason': 'tcp_sync'}), '192.168.0.103', upd_client)
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象
    # tcpClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    addr = ('192.168.0.103', 4000)

    tcpClient.connect(addr)  # 连接服务，指定主机和端口号
    res = []
    timediff = []
    data = 'return\r\n'.encode("utf-8")  # 报文数据，bytes类型

    for i in range(100):
        tcpClient.send(data)  # 发送数据给客户端据给服务端
        tsMillsStart = time.time() * 1000
        msg = tcpClient.recv(1024)  # 接收来自服务端的数据，小于1024字节
        tsMillsEnd = time.time() * 1000
        mess = msg.decode('utf-8')
        transferTime = tsMillsEnd - tsMillsStart
        estimateTimeDiff = tsMillsEnd - int(mess) - transferTime / 2
        print(mess, 'tsMillsdiff:', transferTime, estimateTimeDiff)
        res.append(transferTime)
        if transferTime < 3:
            timediff.append(estimateTimeDiff)

    timediff_ave = np.mean(timediff)
    print("通信时间", sum(res)/len(res), max(res), min(res), np.std(res))
    print("绝对时差", timediff_ave, np.std(timediff), len(timediff))
    print("="*50)
    # res.clear()
    # timediff.clear()
    # tcpClient.shutdown(socket.SHUT_RDWR)
    tcpClient.close()
    send_message_udp(json.dumps({'reason': 'tcp_sync_finished'}), '192.168.0.103', upd_client)


    count_ave.append(timediff_ave)
    # plt.hist(timediff, density=True)
    # sea.kdeplot(timediff)
    # plt.xlabel('Value')
    # plt.ylabel('Probability')
    # plt.title('Density plot')
    # plt.show()


if __name__ == "__main__":
    # udp broadcast test
    for i in range(20):
        print(str(i) + "--"* 20)
        multi_loop_send_and_receive()
        time.sleep(0.1)
    print("res:", np.mean(count_ave), np.std(count_ave), len(count_ave))
    print(count_ave)
    plt.hist(count_ave, density=True)
    sea.kdeplot(count_ave)
    plt.xlabel('Value')
    plt.ylabel('Probability')
    plt.title('Density plot')
    plt.show()