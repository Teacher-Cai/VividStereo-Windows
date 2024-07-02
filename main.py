import json
import os
import socket
import threading
import time
import tkinter as tk
import tkinter.filedialog

import mutagen.mp3
import pygame
import concurrent.futures

from synchronize import send_message_udp, get_absolute_time_diff, udp_communication, tcp_listener
from utils import load_config, write_config, delayMsecond, get_local_ip
from global_info import GlobalInfo

# 建立一个GUI
root = tk.Tk()
root.title("VividStereo")
width = 500
height = 320
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = "%dx%d+%d+%d" % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(False, False)

# 一些全局变量
music_dir = []  # 音乐文件路径
music_name = []  # 音乐文件名称
num = 0  # 当前所播放的音乐序号
SONG_END_EVENT = pygame.USEREVENT + 1
END_OF_SONG_FLAG = True

device_tcp = []
device_absolute_time_diff = []
device_ip = []  # '192.168.0.108', '192.168.0.100'
device_time_diff_list = []
update_config = {}
upd_client = udp_communication()


def assessPlayingDelay(start_ts):
    for i in range(20):
        time.sleep(0.2)
        cur_ts = time.time()
        cur_music = pygame.mixer.music.get_pos()
        print(cur_ts - start_ts, cur_music, int((cur_ts - start_ts)*1000) - cur_music)


# 选择播放音乐所在文件夹
def buttonAddClick():
    # global限定全局变量
    global music_dir
    global music_name
    global num
    global END_OF_SONG_FLAG
    num = 0
    if pygame.mixer.get_init():
        END_OF_SONG_FLAG = False
        pygame.mixer.music.stop()
    # 选择一个文件夹并其返回路径
    folder = tkinter.filedialog.askdirectory()
    if not folder:
        return
    music_name.clear()
    music_dir.clear()
    # 读取文件夹里的音乐文件
    for each in os.listdir(folder):
        if each.endswith((".mp3", ".wav", ".ogg")):
            music_name.append(each)
            music_dir.append(folder + "\\" + each)
    if not music_dir:
        return
    # 将文件名列出到GUI上
    update_config['folder'] = folder
    var.set(music_name)

    buttonPlay["state"] = "normal"
    start_stop.set("播放")
    END_OF_SONG_FLAG = True


def play(pre_set_time_sec):
    """
    播放音乐函数
    :param pre_set_time_sec: preset music play time, second
    :return:
    """
    global num
    global END_OF_SONG_FLAG
    next_music = music_dir[num]
    mp3 = mutagen.mp3.MP3(next_music)
    END_OF_SONG_FLAG = False
    pygame.mixer.quit()
    pygame.mixer.init(mp3.info.sample_rate)
    # print(next_music, pygame.mixer.get_init())
    pygame.mixer.music.load(next_music)

    pygame.mixer.music.play()
    # pygame.mixer.music.pause()
    pygame.mixer.music.set_volume(0.0)

    if pre_set_time_sec > 0:
        remain_time_sec = pre_set_time_sec - time.time()
        delayMsecond(int(remain_time_sec * 1000))

    # pygame.mixer.music.unpause()
    # pygame.mixer.music.play()
    pygame.mixer.music.set_pos(0)
    pygame.mixer.music.set_volume(1.0)

    musicName.set("正在播放:" + music_name[num])
    start_stop.set("暂停")
    END_OF_SONG_FLAG = True


# 播放暂停切换button
def buttonPlayClick():
    # buttonNext["state"] = "normal"
    # buttonPrev['state'] = 'normal'
    if start_stop.get() == "播放":
        ts_sec = time.time()
        tsMills = int(ts_sec * 1000)
        if sync_state.get() == "已同步~":
            for idx, i in enumerate(device_ip):
                pre_set_ts = tsMills - GlobalInfo.ip_with_absolute_time_diff.get(i, 0) + 1000 + GlobalInfo.ip_with_absolute_time_diff.get(GlobalInfo.local_ip, 0)
                next_music = music_name[num]

                GlobalInfo.udp_message.clear()
                GlobalInfo.udp_message['reason'] = 'music_play'
                GlobalInfo.udp_message.update({'music_name': next_music, 'timeMs': pre_set_ts})

                t1 = threading.Thread(target=send_message_udp, args=(json.dumps(GlobalInfo.udp_message), i, upd_client,))
                t1.daemon = True
                t1.start()

        self_set_time = ts_sec + 1 - int(device_running_time_diff_value.get()) / 1000
        play(self_set_time)

    elif start_stop.get() == "暂停":
        pygame.mixer.music.pause()
        for idx, i in enumerate(device_ip):
            pre_set_ts = 0
            next_music = music_name[num]

            GlobalInfo.udp_message.clear()
            GlobalInfo.udp_message['reason'] = 'music_play'
            GlobalInfo.udp_message.update({'music_name': next_music, 'timeMs': pre_set_ts})

            t1 = threading.Thread(target=send_message_udp, args=(json.dumps(GlobalInfo.udp_message), i, upd_client,))
            t1.daemon = True
            t1.start()

        start_stop.set("继续")
    elif start_stop.get() == "继续":
        pygame.mixer.music.unpause()
        start_stop.set("暂停")


# 回到上一首
def buttonPrevClick():
    global num
    if num == 0:
        num = len(music_dir) - 1
    else:
        num -= 1

    ts_sec = time.time()
    tsMills = int(ts_sec * 1000)
    if sync_state.get() == "已同步~":

        for idx, i in enumerate(device_ip):
            pre_set_ts = tsMills - GlobalInfo.ip_with_absolute_time_diff.get(i, 0) + 1000 +GlobalInfo.ip_with_absolute_time_diff.get(GlobalInfo.local_ip, 0)
            next_music = music_name[num]

            GlobalInfo.udp_message.clear()
            GlobalInfo.udp_message['reason'] = 'music_play'
            GlobalInfo.udp_message.update({'music_name': next_music, 'timeMs': pre_set_ts})

            t1 = threading.Thread(target=send_message_udp, args=(json.dumps(GlobalInfo.udp_message), i, upd_client,))
            t1.daemon = True
            t1.start()

        self_set_time = ts_sec + 1 - int(device_running_time_diff_value.get()) / 1000
        play(self_set_time)

    else:
        play(0)


def buttonNextClick():
    """
    切换下一首，
    :return:
    """
    global num
    if num == len(music_dir) - 1:
        num = 0
    else:
        num += 1

    ts_sec = time.time()
    tsMills = int(ts_sec * 1000)
    if sync_state.get() == "已同步~":

        for idx, i in enumerate(device_ip):
            pre_set_ts = tsMills - GlobalInfo.ip_with_absolute_time_diff.get(i, 0) + 1000 + GlobalInfo.ip_with_absolute_time_diff.get(GlobalInfo.local_ip, 0)
            next_music = music_name[num]

            GlobalInfo.udp_message.clear()
            GlobalInfo.udp_message['reason'] = 'music_play'
            GlobalInfo.udp_message.update({'music_name': next_music, 'timeMs': pre_set_ts})

            t1 = threading.Thread(target=send_message_udp, args=(json.dumps(GlobalInfo.udp_message), i, upd_client,))
            t1.daemon = True
            t1.start()

        self_set_time = ts_sec + 1 - int(device_running_time_diff_value.get()) / 1000
        play(self_set_time)

    else:
        play(0)


# 调整音量
def controlVoice(value):
    pygame.mixer.music.set_volume(float(value))


def auto_play_next_song():
    while True:
        e = pygame.event.wait()
        if e.type == SONG_END_EVENT and END_OF_SONG_FLAG and GlobalInfo.master_device:
            buttonNextClick()


def udp_read(udp_socket):
    global num
    while True:
        recv_data = udp_socket.recvfrom(1024)
        recv_message = recv_data[0].decode('utf-8')
        recv_address = recv_data[1]  # ('192.168.0.107', 4002)

        # process logic
        upd_message = json.loads(recv_message)
        if upd_message['reason'] == 'music_play':
            preSetTs = int(upd_message['timeMs'])
            a_music_name = upd_message['music_name']

            music_idx = -1
            if a_music_name in music_name:
                music_idx = music_name.index(a_music_name)

            print("udp:", recv_message, music_idx)

            if music_idx > -1 and preSetTs > 0:
                self_set_time = preSetTs - int(device_running_time_diff_value.get())  # ms
                num = music_idx
                play(self_set_time/1000)

            elif preSetTs == 0:
                pygame.mixer.music.pause()

        elif upd_message['reason'] == 'all_device_delay':
            GlobalInfo.ip_with_absolute_time_diff = dict(upd_message['ip_with_delay'])
            print('ip delay', GlobalInfo.ip_with_absolute_time_diff)
            global device_ip

            device_ip = list(GlobalInfo.ip_with_absolute_time_diff.keys())
            device_ip.remove(GlobalInfo.local_ip)
            print("device_ip", device_ip)
            sync_state.set('已同步~')

        elif upd_message['reason'] == 'get_ip_address':
            GlobalInfo.udp_message.clear()
            GlobalInfo.udp_message['reason'] = 'return_ip_address'
            GlobalInfo.udp_message.update({'ip_address': GlobalInfo.local_ip})
            print("return_ip_address", recv_address)
            send_message_udp(json.dumps(GlobalInfo.udp_message), recv_address[0], upd_client)

        elif upd_message['reason'] == 'return_ip_address':
            GlobalInfo.all_device_ip.append(upd_message['ip_address'])
            print(upd_message['ip_address'])

# init
pygame.init()
pygame.mixer.quit()
pygame.mixer.music.set_endevent(SONG_END_EVENT)
GlobalInfo.local_ip = get_local_ip()

# autoplay next song
t = threading.Thread(target=auto_play_next_song)
t.daemon = True
t.start()

# listen info
t1 = threading.Thread(target=udp_read, args=(upd_client,))
t1.daemon = True
t1.start()

t2 = threading.Thread(target=tcp_listener, args=())
t2.daemon = True
t2.start()

# 添加音乐按钮
buttonAdd = tk.Button(root, text="选文件夹", command=buttonAddClick)
buttonAdd.place(x=30, y=10, width=60, height=30)

# 播放/暂停按钮
start_stop = tk.StringVar(root, value="播放")
buttonPlay = tk.Button(root, textvariable=start_stop, command=buttonPlayClick)
buttonPlay.place(x=100, y=10, width=60, height=30)
buttonPlay["state"] = "disabled"

# 下一首按钮
buttonNext = tk.Button(root, text="下一首", command=buttonNextClick)
buttonNext.place(x=100, y=50, width=60, height=30)
# buttonNext["state"] = "disabled"

# 上一首按钮
buttonPrev = tk.Button(root, text="上一首", command=buttonPrevClick)
buttonPrev.place(x=30, y=50, width=60, height=30)
# buttonPrev["state"] = "disabled"

# 当前播放音乐
musicName = tk.StringVar(root, value="暂时没有播放音乐")
labelName = tk.Label(root, textvariable=musicName, justify=tk.LEFT, fg="green")
labelName.place(x=200, y=10, width=260, height=20)

# 调节音量
labelvoice = tk.Label(root, text="音量", justify=tk.LEFT)
labelvoice.place(x=20, y=150, width=30, height=20)
s = tkinter.Scale(root, from_=0, to=1, orient=tkinter.HORIZONTAL, length=200, resolution=0.1, command=controlVoice)
s.set(1)
s.place(x=55, y=130, width=100)


def start_to_connet_surrounding_devices():
    """
    use tcp protocol get relative ms diff
    :return:
    """
    global device_tcp
    global device_absolute_time_diff
    global device_ip

    # get all device ip in local network
    GlobalInfo.udp_message.clear()
    GlobalInfo.udp_message['reason'] = 'get_ip_address'
    GlobalInfo.udp_message.update({'ip_address': GlobalInfo.local_ip})

    send_message_udp(json.dumps(GlobalInfo.udp_message), "255.255.255.255", upd_client)

    time.sleep(1)

    GlobalInfo.all_device_ip.remove(GlobalInfo.local_ip)
    device_ip = GlobalInfo.all_device_ip
    print("device_ip:", device_ip)

    for i in device_ip:
        try:
            tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象
            tcpClient.settimeout(3)
            addr = (i, 4000)
            tcpClient.connect(addr)  # 连接服务，指定主机和端口号
        except OSError:
            print(i, "can't connect, skipped!")
            continue
        device_tcp.append(tcpClient)

    # get different dive absolute time diff
    executor = concurrent.futures.ThreadPoolExecutor(5)

    for i in device_tcp:
        device_time_diff_list.append(executor.submit(get_absolute_time_diff, i))

    device_absolute_time_diff += [int(i.result()) for i in device_time_diff_list]
    print(device_absolute_time_diff)
    sync_state.set("已同步~")
    GlobalInfo.ip_with_absolute_time_diff.update(dict(zip(device_ip, device_absolute_time_diff)))
    GlobalInfo.ip_with_absolute_time_diff[GlobalInfo.local_ip] = 0

    GlobalInfo.udp_message['reason'] = 'all_device_delay'
    GlobalInfo.udp_message['ip_with_delay'] = GlobalInfo.ip_with_absolute_time_diff
    # send message to all machine
    for idx, i in enumerate(device_ip):
        t2 = threading.Thread(target=send_message_udp, args=(json.dumps(GlobalInfo.udp_message), i, upd_client))
        t2.daemon = True
        t2.start()


# synchronize play music
sync_play_button = tk.Button(root, text='同步多播放设备', command=start_to_connet_surrounding_devices)
sync_play_button.place(x=30, y=190)

# synchronize info
sync_info_label = tk.Label(root, text="同步状态:", justify=tk.LEFT)
sync_info_label.place(x=30, y=230)

sync_state = tk.StringVar(root, value="单机模式(未同步)")
sync_state_name = tk.Label(root, textvariable=sync_state, justify=tk.LEFT, fg="pink")
sync_state_name.place(x=90, y=230)

# synchronize password
# sync_password = tk.Label(root, text="同步密钥:", justify=tk.LEFT)
# sync_password.place(x=30, y=260)
#
# sync_password_input_value = tk.StringVar(root, value="1234")
# sync_password_input = tk.Entry(root, textvariable=sync_password_input_value, width=10)
# sync_password_input.place(x=90, y=260)

# adjust device running time diff
device_running_time_diff_label = tk.Label(root, text="本设备运行时差(ms):", justify=tk.LEFT)
device_running_time_diff_label.place(x=30, y=290)

device_running_time_diff_value = tk.StringVar(root)
device_running_time_diff_input = tk.Entry(root, textvariable=device_running_time_diff_value, width=5)
device_running_time_diff_input.place(x=150, y=290)

# initialize music list
var = tk.StringVar()
music_list = tk.Listbox(root, listvariable=var)
music_list.place(x=200, y=40, width=260, height=240)
config = load_config()
update_config = config

if config and config.get('folder'):
    folder = config.get('folder')
    for each in os.listdir(folder):
        if each.endswith((".mp3", ".wav", ".ogg")):
            music_name.append(each)
            music_dir.append(folder + "\\" + each)
    buttonPlay["state"] = "normal"
    start_stop.set("播放")
    var.set(music_name)

    device_running_time_diff_value.set(config.get('system_play_delay', 10))


def when_close():
    update_config['system_play_delay'] = device_running_time_diff_value.get()
    write_config(update_config)
    root.destroy()


root.protocol('WM_DELETE_WINDOW', when_close)
root.mainloop()
