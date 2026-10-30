#  ams_api — Flask 后端 API 服务

「峰峦守护」云端服务层，基于 **Flask + Flask-MQTT + PyMySQL** 构建，为鸿蒙移动端提供 RESTful 接口，同时承担 IoT 设备 MQTT Broker 功能。

---

##  文件清单

| 文件 | 功能 |
|------|------|
| [flask_app.py](flask_app.py) | Flask 主应用，所有 HTTP 路由定义 |
| [db_comm.py](db_comm.py) | PyMySQL 数据库操作封装（连接 / 查询 / 事务） |

##  数据库连接配置

在 [db_comm.py](db_comm.py) 头部修改：

```python
user   = 'test'        # MySQL 用户名
pwd    = '123456'      # MySQL 密码
host   = '127.0.0.1'   # MySQL 地址
dbname = 'demo'        # 数据库名
```

##  API 接口清单

### 认证

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/oper/auth` | 账号密码登录 |

### 城市与环境

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/city/temp` | 查询指定城市的温氧数据 |
| POST | `/city/list` | 城市列表查询 |
| POST | `/city/add` | 新增城市 |
| POST | `/city/update` | 修改城市 |
| POST | `/city/delete` | 删除城市 |

### 用户体征

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/user/vital` | 查询用户体征数据 |

### 风险分析

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/user/risk` | 查询用户高反风险报告 |

### 设备管理

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/device/query` | 按类型查询设备列表 |
| POST | `/device/one` | 查询单个设备详情 |

### 报警

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/alarm/query` | 查询设备报警记录 |
| POST | `/alarm/add` | 新增报警记录 |
| POST | `/alarm/update` | 更新报警处理状态 |

### 预警规则

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/rule/query` | 查询预警规则列表 |

##  统一返回格式

```json
{
  "code": 10000,
  "msg": "登录成功",
  "data": [...]
}
```

| code | 含义 |
|------|------|
| 10000 | 成功 |
| 10001 | 参数缺失 |
| 10002 | 账号密码错误 |
| 10003 | 操作失败 |
| 9999  | 系统异常 |

## 

### 1. 安装依赖

```bash
pip install flask flask-mqtt pymysql requests
```

### 2. 确保数据库已初始化

```bash
mysql -u root -p < "../ams_db/AMS数据库设计：ams_db.sql"
```

### 3. 启动服务

```bash
python flask_app.py
```

默认监听端口：**5060**（见 `NetApi.ts` 中 `BaseURL` 对应）

##  注意事项

- 登录接口依赖 `syst_oper` 表（登录用户表），该表不在主 SQL 脚本中，需自行创建或从其他系统迁移
- Flask-MQTT 的 broker host / port / 用户名密码在 `flask_app.py` 顶部配置
- 所有接口均返回 UTF-8 JSON，`db_comm.py` 中已内置 `DateEncoder` 处理 `datetime` 字段
