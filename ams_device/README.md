#  ams_device — 可穿戴设备边缘感知层

基于 **OpenHarmony IoT / HiSilicon WS63** 芯片的可穿戴设备固件，是「峰峦守护」的**边缘感知层**。负责采集血压、血氧等体征数据，通过**星闪（SLE, SparkLink Low Energy）** 近距通信实时推送给鸿蒙手机端，同时通过 **WiFi + MQTT** 上报云端。

---

##  芯片与构建

| 项目 | 说明 |
|------|------|
| MCU | HiSilicon WS63V100 |
| 操作系统 | OpenHarmony IoT (LiteOS-M) |
| 构建系统 | GN (BUILD.gn) + `hb build` |
| 星闪 SDK | `//device/soc/hisilicon/ws63v100/sdkv102/include/middleware/services/bts/sle` |

##  文件清单

| 文件 | 功能 |
|------|------|
| [blood_func.c/h](blood_func.c) | 血压 / 血氧传感器 UART 驱动 + SLE 收发桥接 |
| [iot_server.c](iot_server.c) |  **星闪 SLE SSAP 服务端**（UUID 服务 + Notify 推送） |
| [iot_server_ex.c/h](iot_server_ex.c) | SLE 服务端扩展（连接管理 / CCC 配置） |
| [mqtt_cmd.c](mqtt_cmd.c) | MQTT 云端上报指令、软重启、雷达传感器查询 |
| [wifi_func.c](wifi_func.c) | WiFi STA 模式连接 + 自动重连 + MQTT 启动/停止 |
| [ws2812_spi.c/h](ws2812_spi.c) | WS2812 RGB LED 驱动（SPI 协议，状态灯） |
| [iot_gpio_ex.h](iot_gpio_ex.h) | GPIO / SOS 按键 / 引脚扩展定义 |
| [BUILD.gn](BUILD.gn) | OpenHarmony GN 构建配置 |

##  星闪（SLE）通信设计

### SSAP 服务配置

```
服务 UUID (16-bit) : 0x2222
属性 UUID (16-bit) : 0x2323  ← 支持 Notify + Read + Write
基础 UUID (128-bit): 37BEA880-FC70-11EA-B720-000000000000
MTU 大小            : 200 Bytes
MCS 调制率          : MCS10（低时延模式）
设备 MAC            : 11:11:22:22:00:25
```

### 帧协议（设备 → 手机 Notify 上报）

设备向手机推送的数据帧：

| 方向 | 帧头 | 含义 | 数据 |
|------|------|------|------|
| 设备→手机 | `03` | 时钟同步 | 小时、分钟 |
| 设备→手机 | `04` | RGB 状态灯 | 亮度等级（00关 / 01低 / 02中 / 03高） |
| 设备→手机 | `01` | 睡眠数据 | -- |
| 设备→手机 | `01` | 心率数据 | -- |
| 设备→手机 | `01` | 呼吸数据 | -- |

### 帧协议（手机 → 设备 Write 指令）

手机端可通过 SSAP Write 控制设备：

```
04 01 00  → 关闭 LED
04 01 01  → LED 低亮
04 01 02  → LED 中亮
04 01 03  → LED 高亮
```

##  外设与引脚

| 外设 | 接口 | 引脚 | 说明 |
|------|------|------|------|
| 血压 / 血氧传感器 | UART0 | TX=15, RX=16 | 波特率 9600 |
| 雷达人体传感器 | UART3 | TX=8, RX=7 | 距离 / 存在检测 |
| SOS 按键 | GPIO | Pin 12 | 紧急呼叫触发 |
| WS2812 RGB | SPI0 | - | 10 颗 LED |
| WiFi | - | - | STA 模式 |
| 星闪 SLE | - | - | SSAP 服务端广播 |

##  WS2812 状态灯含义

| 颜色 | 状态 | 条件 |
|------|------|------|
| 🟢 绿色 | 正常 | 体征全部正常 + WiFi 已连接 |
| 🟡 黄色 | 警告 | 体征异常或 WiFi 断开 |
| 🔴 红色 | 危险 | 重度高反 / SOS 触发 |

##  编译与烧录

### 1. 环境准备

```bash
# 确保 OpenHarmony SDK 和 hb 构建工具已安装
# HiSilicon WS63 SDKv102 需放在标准路径下
```

### 2. 编译

```bash
hb build          # 默认编译本模块
```

### 3. 烧录固件

编译完成后，将产物通过 HiBurn 工具烧录到 WS63 开发板：

| 固件 | 用途 |
|------|------|
| `sle_server.fwpkg` | 可穿戴设备（本目录编译产物） |
| `sle_client.fwpkg` | 配套星闪客户端（手机侧） |

两个预编译固件已存放在 `../ams_device_bin/` 目录。

##  自定义配置

需修改的关键参数：

| 参数 | 位置 | 默认值 |
|------|------|--------|
| WiFi SSID | `wifi_func.c` → `CONFIG_WIFI_SSID` | `iot` |
| WiFi 密码 | `wifi_func.c` → `CONFIG_WIFI_PWD` | `12345678` |
| SLE MAC 地址 | `iot_server.c` → `g_mac` | `11:11:22:22:00:25` |
| MQTT Broker | `mqtt_cmd.c` 中 MQTT 配置 | 需根据实际服务器修改 |

##  启动流程

```
系统上电
    │
    ├── iot_server_init()         ← 初始化星闪 SLE 服务端并开始广播
    ├── wifi_init()               ← 连接 WiFi，成功后启动 MQTT
    ├── blood_func_init()         ← 启动 UART 采集线程
    └── 主循环
            │
            ├── 传感器数据采集 (UART)
            ├── WS2812 状态更新 (SPI)
            ├── SLE Notify 推送 → 鸿蒙手机
            ├── MQTT Publish → 云端
            └── SOS 按键检测 → 紧急呼叫
```

##  依赖库

| 依赖 | 来源 |
|------|------|
| CMSIS-OS2 | LiteOS-M 内核 |
| cJSON | OpenHarmony 开源组件 |
| lwIP | OpenHarmony 网络栈 |
| SLE SDK | WS63 SDKv102 内置 |
