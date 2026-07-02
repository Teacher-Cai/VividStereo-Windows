# VividStereo-Windows

![logo](image/vivid_stereo.png)

【自制 APP】多设备音乐同步播放软件，音乐爱好者不容错过的音乐播放器！ 🎵

> 在同一局域网下，让多台 Windows 设备以亚毫秒级精度同步播放同一首歌，打造沉浸式立体声环绕体验。

📺 视频介绍：[Bilibili](https://www.bilibili.com/video/BV1yoWNekEHN/) ｜ [YouTube](https://youtu.be/CTvh30tzPr0?si=-WsIIJp-1CjTZXOF)

---

## ✨ 功能特性

- 🎶 **本地音乐播放**：基于 `pygame.mixer` 实现，支持 `mp3 / wav / ogg` 格式。
- 📁 **文件夹加载**：一键选择本地音乐文件夹，自动扫描并加入播放列表。
- ▶️ **基础控制**：播放 / 暂停 / 继续、上一首 / 下一首、音量调节。
- 🪄 **自动连播**：当前歌曲结束后自动切换至下一首。
- 🖱️ **双击切歌**：双击列表中的任意歌曲立即播放。
- 🌐 **多设备同步播放**：同一局域网下，多台电脑协同播放同一首歌。
- ⏱️ **高精度时间同步**：基于 TCP 往返时延估算设备间绝对时差，自动补偿后让各设备"齐声"开唱。
- ⚙️ **本机播放延迟微调**：可手动设置本机播放时差（ms），用于声卡/缓冲等额外延迟补偿。
- 💾 **配置持久化**：自动保存上次打开的文件夹与播放时差，下次启动自动恢复。

---

## 🧠 多设备同步原理

整体流程（详见 `main.py` 中 `start_to_connet_surrounding_devices` 与 `synchronize.py`）：

1. **设备发现**：主设备通过 UDP 广播（`255.255.255.255:4002`）询问局域网内所有从设备。
2. **时差估算**：对每个从设备建立 TCP 连接（`4000` 端口），主从两端通过 100 次 `return\r\n` 请求-响应交换本机毫秒时间戳，用 `RTT/2` 补偿后取均值，得到两机的绝对时差。
3. **同步播放**：主设备在触发"播放/切歌"时，根据每个从设备的时差动态计算其播放时刻：
   ```
   pre_set_ts = now - device_delay + 1000ms + local_delay
   ```
   主设备自身则延时到该时间点（减去本机播放时差）再 `pygame.mixer.music.play()`，从设备在接收到 UDP 指令后同样在指定时间戳开始播放。
4. **暂停同步**：当 `timeMs = 0` 时，从设备执行 `pause()`。

> 网络抖动通过多次采样取均值过滤掉离群点（仅保留 RTT < 10ms 的样本）。

---

## 🛠️ 技术栈

- **Python 3**
- **GUI**：`tkinter`
- **音频**：`pygame`、`mutagen`
- **网络通信**：标准库 `socket`（UDP 广播 + TCP）
- **数据分析**：`numpy`（同步测试用 `performanceTest.py`）
- **可视化**（测试）：`matplotlib`、`seaborn`

---

## 📦 安装与运行

### 1. 克隆项目

```bash
git clone <your-repo-url> VividStereo-Windows
cd VividStereo-Windows
```

### 2. 安装依赖

```bash
pip install pygame mutagen numpy
# 可选：仅 performanceTest.py 使用
pip install matplotlib seaborn
```

> 提示：项目使用 `tkinter`，Windows 上的官方 Python 安装包已自带该模块。

### 3. 启动主程序

```bash
python main.py
```

### 4.（可选）运行同步精度测试

```bash
python performanceTest.py
```

该脚本会与指定 IP（默认 `192.168.0.103`）进行 20 轮时间同步测试，并绘制时差分布直方图。**使用前请将脚本中的目标 IP 改为实际的从设备 IP。**

---

## 🚀 使用说明

1. 启动后点击 **"选文件夹"** 选择存放音乐的目录。
2. 列表中会显示所有 `mp3 / wav / ogg` 文件，双击即可播放。
3. 拖动 **音量** 滑块可调节音量。
4. 若需要多设备同步：
   - 确保所有设备在同一局域网下，并能互相访问 `4000`（TCP）和 `4002`（UDP）端口。
   - 在 **主设备** 上点击 **"同步多播放设备"** 按钮：
     - 程序会自动扫描局域网内其他运行了 VividStereo 的设备。
     - 对每台设备估算绝对时差，并下发同步参数。
     - 同步状态显示为 **"已同步~"**。
   - 此后任意播放/切歌操作都会同步到所有设备。
5. **本设备运行时差(ms)**：根据本机声卡/系统延迟手动填写（毫秒），用于补偿启动播放时的额外耗时。
6. 关闭程序时会自动保存当前配置到 `VividStereo.config`，下次启动自动恢复。

---

## 📂 项目结构

```
VividStereo-Windows/
├── main.py              # GUI 主程序与播放控制逻辑
├── global_info.py       # 进程内共享状态（IP、时差、消息体等）
├── synchronize.py       # UDP/TCP 通信与设备间时间同步算法
├── utils.py             # 工具函数（高精度延时、配置读写、线程停止等）
├── performanceTest.py   # 时间同步精度测试脚本
├── image/               # 图标与封面
│   ├── vivid_stereo.ico
│   └── vivid_stereo.png
├── LICENSE
├── README.md
└── .gitignore
```

---

## ⚙️ 配置说明

程序在运行目录下生成 `VividStereo.config`（已被 `.gitignore` 忽略），结构示例：

```json
{
  "folder": "C:\\Users\\you\\Music\\favorite",
  "system_play_delay": 120
}
```

| 字段                 | 含义                                       |
| -------------------- | ------------------------------------------ |
| `folder`             | 上次选择的音乐文件夹路径                   |
| `system_play_delay`  | 本机播放延迟补偿值（毫秒），用于同步播放时 |

---

## 🌐 网络与端口

| 端口 | 协议 | 用途                                |
| ---- | ---- | ----------------------------------- |
| 4002 | UDP  | 局域网设备发现、播放控制消息广播    |
| 4000 | TCP  | 主从设备间时间戳同步（往返时延测量） |

> 首次使用多设备同步时，请关闭本机及路由器的防火墙，或在防火墙中放行上述端口。

---

## ❓ 常见问题

- **找不到其他设备？**
  确认所有设备在同一子网，Windows 防火墙放行 Python/本程序。
- **同步后仍有明显延迟？**
  调大主设备的 **"本设备运行时差(ms)"**，或检查路由器/交换机是否存在较大 QoS 抖动。
- **支持 macOS / Linux 吗？**
  本仓库标题为 `-Windows`，但核心同步逻辑与平台无关，理论上 `tkinter` + `pygame` 也能在其他平台运行，需要自行测试。

---

## 📜 License

本项目遵循仓库根目录中的 [LICENSE](LICENSE) 协议。
