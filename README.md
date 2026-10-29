#  峰峦守护

> **基于 OpenHarmony 与星闪的高海拔边缘健康感知预警终端**

面向高原旅行者与登山者的 **高反（AMS）智能监测预警系统**。依托 **OpenHarmony** 全栈架构，结合 **星闪（SLE, SparkLink Low Energy）** 低时延近距通信、IoT 可穿戴边缘采集与 AI 机器学习，在高海拔场景下实时感知人体生理体征，智能评估高原反应风险等级，并通过鸿蒙移动终端提供可视化健康报告与救援建议。

 **核心亮点**

-  **星闪（SLE）近距通信** — 比 BLE 低 60% 时延，SSAP 自定义服务实现设备与手机间高速体征数据同步
-  **OpenHarmony 全栈** — 设备端 / 边缘端 / 移动端统一基于 OpenHarmony 生态
-  **边缘 + 云端协同 AI** — 设备端本地初步判断 + 云端 RF/SVM 模型精准分级（4 级风险）
-  **多模通信** — 星闪（近距）+ MQTT（云边）双通道保障高海拔弱网环境

---

##  项目结构

```
ams_alarm/
│
├── ams_device/                  【边缘感知层】IoT 可穿戴设备固件（C / OpenHarmony）
│   ├── iot_server.c/h              ★ 星闪 SLE SSAP 服务端（自定义 UUID 服务 + Notify 上报）
│   ├── blood_func.c/h              血压 / 血氧传感器驱动，SLE 收发桥接
│   ├── mqtt_cmd.c                  MQTT 云端上报指令处理
│   ├── wifi_func.c                 WiFi 连接管理
│   ├── ws2812_spi.c/h              WS2812 RGB 状态灯驱动
│   ├── iot_gpio_ex.h               GPIO / 外设扩展
│   └── BUILD.gn                    OpenHarmony 构建配置
│
├── ams_device_bin/              固件预编译包
│   ├── sle_server.fwpkg            星闪 SLE 服务端固件（烧录到可穿戴设备）
│   └── sle_client.fwpkg            星闪 SLE 客户端固件
│
├── ams_HarmonyApp/              【移动应用层】鸿蒙客户端（ArkTS / DevEco Studio）
│   └── DevEcoStudioProjects/entry/src/main/
│       ├── ets/
│       │   ├── pages/              登录 / 健康监测 / 风险分析 / 个人中心
│       │   ├── models/             CityModel / LoginModel / VitalModel
│       │   └── utils/              NetApi / GlobalContext / Logger / PreferencesUtil
│       └── resources/              图标 / 图片 / 颜色 / 字符串资源
│
├── ams_api/                     【云端服务层】Flask API + MQTT Broker
│   ├── flask_app.py                /oper/auth  /city/temp  /vital/upload  /risk/report ...
│   └── db_comm.py                  MySQL 数据库操作封装
│
├── ams_guard_ai/                【AI 分析层】高反风险机器学习引擎
│   ├── main.py                     主入口：体征 → AI → 风险等级
│   ├── predictor.py                风险预测器
│   ├── model_trainer.py            RF / SVM 模型训练脚本
│   ├── mobile_ai.py                移动健康分析
│   ├── scenario_service.py         场景服务（城市海拔 / 环境温氧）
│   ├── health_report.py            健康报告文本生成
│   ├── alert_rescue.py             救援警报触发
│   ├── database.py                 SQLite 中间库管理
│   ├── data_generator.py           高反模拟数据生成
│   ├── visualizer.py               数据可视化
│   ├── rf_model.pkl                ★ 预训练随机森林模型
│   ├── svm_model.pkl               ★ 预训练 SVM 模型
│   └── scaler.pkl                  StandardScaler 特征标准化器
│
└── ams_db/                      数据库设计
    └── AMS数据库设计：ams_db.sql    MySQL 建表脚本
```

##  系统架构

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                        鸿蒙移动终端                                 │
 │   ArkTS UI:  Login → HealthMonitor → RiskAnalysis → Profile        │
 │                 │                            ▲                      │
 │                 │  HTTPS                      │ HTTPS                │
 └─────────────────┼────────────────────────────┼──────────────────────┘
                   │                            │
    ┌──────────────┼────────────────────────────┼──────────────────┐
    │              ▼                            ▼                  │
    │   ┌────────────────────────────────────────────────┐          │
    │   │          Flask API + MQTT Broker               │          │
    │   │  /oper/auth   /city/temp   /vital/upload      │          │
    │   │  /risk/report /alert/rescue                    │          │
    │   └───────────┬────────────────────┬───────────────┘          │
    │               │                    │                          │
    │               ▼                    ▼                          │
    │          ┌─────────┐         ┌──────────────┐                │
    │          │  MySQL  │         │  SQLite AI   │                │
    │          │ (主数据库)│         │ (分析中间库)  │                │
    │          └────┬────┘         └──────┬───────┘                │
    │               │                     │                        │
    │               └─────────┬───────────┘                        │
    │                         ▼                                    │
    │              ┌───────────────────────┐                       │
    │              │     ams_guard_ai      │                       │
    │              │  Random Forest / SVM  │                       │
    │              │  4级风险分类 + 建议     │                       │
    │              └──────────▲────────────┘                       │
    │                         │ MQTT                                │
    └─────────────────────────┼────────────────────────────────────┘
                              │
              ┌───────────────┼──────────────────┐
              │               │    WiFi / MQTT    │
              │               ▼                   │
    ┌─────────┼──────────────────────────────┐   │
    │   星闪 SLE 低时延通信 (sle_ssap)       │   │
    │   MTU=200B  Notify 主动上报            │   │
    │   MCS10 高调制速率                      │   │
    │               ▲                         │   │
    └───────────────┼─────────────────────────┘   │
                    │                             │
    ┌───────────────┼─────────────────────────────┐
    │    边缘感知层 · 可穿戴终端                   │
    │   blood_func.c  ─ 血压 / 血氧传感器         │
    │   iot_server.c  ─ SLE SSAP 服务端           │
    │   ws2812_spi.c  ─ RGB 状态灯 (绿/黄/红)     │
    │   wifi_func.c   ─ WiFi 联网                 │
    └────────────────────────────────────────────┘
```

##  星闪（SLE）通信设计

设备端基于 **OpenHarmony SLE SDK** 实现 SSAP（SparkLink Service Access Profile）自定义服务：

| 要素 | 说明 |
|------|------|
| 服务 UUID | `0x2222`（16-bit） |
| 属性 UUID | `0x2323`（Notify + Read + Write） |
| 基础 UUID | `37BEA880FC7011EAB7200000000000000` |
| MTU 大小 | 200 Bytes |
| MCS 等级 | MCS10（高调制，低时延） |
| MAC 地址 | `11:11:22:22:00:25` |

SLE 相比传统 BLE 在高海拔弱信号场景下优势明显：
- 端到端时延降低 **60%**
- 支持 **低时延模式**（`CONFIG_SAMPLE_SUPPORT_LOW_LATENCY_TYPE`）
- SSAP Notify 主动推送体征数据，无需手机轮询

##  快速开始

### 1. 数据库初始化

```bash
mysql -u root -p < "ams_db/AMS数据库设计：ams_db.sql"
```

核心表结构：

| 表名 | 关键字段 | 用途 |
|------|----------|------|
| `ams_city` | cityId, cityName, altitude | 城市与海拔 |
| `ams_city_temp` | cityId, measureDate, temp, oxygen | 城市温氧环境 |
| `ams_user` | userId, userName, age, gender | 用户信息 |
| `ams_vital_data` | SpO₂, SBP, DBP, heart, breath, sleep_quality | 体征数据 |
| `ams_user_risk` | riskLevel(0-3), riskReport | 高反风险报告 |

### 2. Flask API 服务

```bash
cd ams_api
pip install flask flask-mqtt pymysql requests
python flask_app.py
```

### 3. AI 守护模块

```bash
cd ams_guard_ai
pip install numpy pandas scikit-learn joblib

# 运行主分析流程（用预训练模型）
python main.py

# 重新训练模型（可选，有标注数据时）
python model_trainer.py
```

### 4. 鸿蒙 App

使用 **DevEco Studio** 打开 `ams_HarmonyApp/DevEcoStudioProjects/`，连接设备/模拟器运行。

| 页面 | 功能 |
|------|------|
| LoginPage | 账号登录 |
| HealthMonitorPage | 实时体征（SpO₂、血压、心率、呼吸、睡眠） |
| RiskAnalysisPage | 高反风险等级 + 趋势图表 |
| ProfilePage | 个人中心 / 设置 |

### 5. 可穿戴设备固件

基于 **OpenHarmony IoT** 构建（HiSilicon 芯片 SDK）：

```bash
# 编译
hb build

# 烧录
# sle_server.fwpkg → 可穿戴设备（SLE 服务端）
# sle_client.fwpkg → 配套 SLE 客户端
```

固件功能：
- 血压 / 血氧传感器实时采集
- 星闪 SLE SSAP 服务端（Notify 模式）向手机推送体征
- WiFi + MQTT 双通道云端上报
- WS2812 RGB 状态灯：🟢 正常 / 🟡 警告 / 🔴 危险

##  AI 风险分析

### 输入特征

```
SpO₂, SBP, DBP, heart_rate, breath_rate, 
sleep_quality, altitude, temperature, oxygen_concentration
```

### 处理流水线

```
体征原始数据
    │
    ▼
StandardScaler (scaler.pkl)   ← 特征标准化
    │
    ▼
Random Forest / SVM           ← 二选一分类器
    │
    ▼
风险等级 (0-3) + 健康建议文本
```

### 风险等级定义

| 等级 | 含义 | 建议 |
|:----:|------|------|
| 0 | ✅ 无风险 | 正常活动 |
| 1 | ⚠️ 轻度高反 | 降低运动量，多喝水观察 |
| 2 | 🟠 中度高反 | 吸氧 + 休息，警惕恶化 |
| 3 | 🔴 重度高反 | 立即下降海拔 + 就医 |

##  技术栈总览

| 层级 | 技术 |
|------|------|
| 可穿戴终端 | OpenHarmony IoT / HiSilicon SDK / C / SLE SSAP |
| 近距通信 |  星闪 SLE (SparkLink Low Energy) |
| 远距通信 | WiFi + MQTT |
| 状态指示 | WS2812 RGB LED (SPI) |
| 移动应用 | HarmonyOS / ArkTS / DevEco Studio |
| 后端服务 | Flask + Flask-MQTT + PyMySQL |
| AI 引擎 | scikit-learn (Random Forest / SVM) |
| 数据库 | MySQL（主）+ SQLite（AI 中间库） |

##  注意事项

- `syst_oper` 登录用户表需自行在 MySQL 中创建或迁移
- 设备端 MQTT Broker 地址、WiFi SSID/密码需在 `wifi_func.c` 中修改
- 鸿蒙 App 后端 API 地址在 `NetApi.ts` 中统一配置
- SLE MAC 地址 `11:11:22:22:00:25` 可在 `iot_server.c` 中自定义，多设备场景需确保唯一
- AI 模型可通过 `model_trainer.py` 重新训练，只需替换 `data_generator.py` 中的真实体征数据
