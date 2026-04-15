# InStock 用户指南

本文档详细介绍 InStock 股票分析系统的使用方法和注意事项。

---

## 目录

1. [系统概述](#1-系统概述)
2. [安装部署](#2-安装部署)
3. [配置说明](#3-配置说明)
4. [启动服务](#4-启动服务)
5. [API使用](#5-api使用)
6. [定时任务](#6-定时任务)
7. [常见问题](#7-常见问题)
8. [注意事项](#8-注意事项)

---

## 1. 系统概述

InStock 是一个基于 FastAPI 的股票量化分析平台，主要功能：

- **数据获取**：通过 MOOTDX（通达信数据接口）获取股票实时行情、历史K线、指数数据、财务数据
- **技术分析**：计算 30+ 种技术指标（MACD、KDJ、RSI 等）
- **形态识别**：识别 17 种 K 线形态（锤头、吞没、早晨之星等）
- **策略选股**：内置 7 种选股策略（放量上涨、突破平台等）
- **策略回测**：对选股策略进行历史回测分析

---

## 2. 安装部署

### 2.1 环境要求

| 要求 | 说明 |
|------|------|
| Python | 3.9 或更高版本 |
| 操作系统 | Windows / Linux / macOS |
| 网络 | 能访问通达信数据服务器 |

### 2.2 安装步骤

```bash
# 1. 克隆项目（或下载源码）
git clone <项目地址>
cd stock-analysis

# 2. 安装依赖
pip install -r requirements.txt

# 3. 进入应用目录
cd app
```

### 2.3 验证安装

```bash
# 检查依赖是否安装完整
python -c "import fastapi; import mootdx; import pandas_ta; print('依赖安装成功')"
```

---

## 3. 配置说明

配置文件位于 `app/config/config.py`，主要配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务绑定地址 |
| `PORT` | `9988` | 服务端口 |
| `DEBUG` | `True` | 是否开启调试模式 |
| `DB_FILE` | `data/instock.db` | SQLite 数据库路径 |
| `SCHEDULER_ENABLED` | `True` | 是否启用定时任务 |

### 修改端口示例

```python
# app/config/config.py
class Settings:
    PORT = 8080  # 修改为其他端口
```

---

## 4. 启动服务

### 4.1 正常启动

```bash
# 方式一：直接运行
python -m app.main

# 方式二：使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 9988 --reload
```

### 4.2 启动后自动执行

服务启动后会自动执行以下操作：

1. **初始化数据库**
   - 创建 `data/` 目录
   - 创建 SQLite 数据库文件
   - 自动创建所有数据表

2. **检查当日数据**
   - 判断是否为交易日
   - 若是交易日且数据库无当日数据，自动抓取

3. **启动定时任务**
   - 若 `SCHEDULER_ENABLED = True`，启动后台调度器

### 4.3 验证启动

浏览器访问：
- **Swagger UI**: http://localhost:9988/docs
- **ReDoc**: http://localhost:9988/redoc
- **健康检查**: http://localhost:9988/health

---

## 5. API使用

### 5.1 接口文档

详细接口文档请查看 [interface.md](interface.md)。

### 5.2 快速示例

#### 获取股票列表

```bash
curl "http://localhost:9988/api/stocks/list"
```

#### 获取单只股票详情

```bash
curl "http://localhost:9988/api/stocks/000001"
```

#### 手动抓取当日数据

```bash
curl -X POST "http://localhost:9988/api/stocks/fetch"
```

#### 运行策略选股

```bash
curl -X POST "http://localhost:9988/api/strategy/run-all"
```

#### 添加关注股票

```bash
curl -X POST "http://localhost:9988/api/attention/add/000001"
```

### 5.3 响应格式

所有接口统一响应格式：

```json
{
    "code": 0,        // 0 表示成功，-1 表示失败
    "message": "success",
    "data": {}        // 具体数据
}
```

---

## 6. 定时任务

系统内置三个定时任务，仅在交易日执行：

| 任务 | 执行时间 | 功能说明 |
|------|----------|----------|
| 数据抓取 | 15:30 | 抓取当日全市场股票行情 |
| 指标计算 | 16:00 | 计算所有股票的技术指标 |
| 策略选股 | 16:30 | 运行所有选股策略并保存结果 |

### 任务依赖关系

```
数据抓取 (15:30) → 指标计算 (16:00) → 策略选股 (16:30)
```

**说明**：指标计算依赖当日行情数据，策略选股依赖技术指标，因此按顺序执行。

### 手动触发任务

也可以通过 API 手动触发：

```bash
# 抓取数据
curl -X POST "http://localhost:9988/api/stocks/fetch"

# 计算指标（需先有数据）
curl -X POST "http://localhost:9988/api/indicators/calculate-all"

# 运行策略（需先有指标）
curl -X POST "http://localhost:9988/api/strategy/run-all"
```

---

## 7. 常见问题

### Q1: 启动时报错 "ModuleNotFoundError"

**原因**：依赖未完整安装

**解决**：
```bash
pip install -r requirements.txt
```

### Q2: 数据抓取返回空数据

**可能原因**：
- 当天不是交易日（周末/节假日）
- 网络无法连接通达信服务器
- 当前时间不在交易时段（9:30-15:00）

**解决**：检查网络连接，或在交易日交易时段后抓取

### Q3: 部分股票代码无法获取数据

**原因**：系统已过滤北交所股票（8xxxxx、4xxxxx），MOOTDX 不支持

**说明**：这是设计行为，只支持沪深主板、创业板、科创板

### Q4: 数据库文件在哪里

**位置**：`app/data/instock.db`

**查看数据**：
```bash
# 使用 SQLite 命令行
sqlite3 app/data/instock.db

# 或使用 DB Browser for SQLite 等工具
```

### Q5: 如何关闭定时任务

**方法**：修改配置文件

```python
# app/config/config.py
SCHEDULER_ENABLED = False
```

### Q6: 批次保存报错 "UNIQUE constraint failed"

**错误信息**：
```
UNIQUE constraint failed: cn_stock_spot.date, cn_stock_spot.code
This Session's transaction has been rolled back...
```

**原因**：批次保存时遇到已存在的数据（date+code 主键重复）

**解决**：已修复，使用 upsert 策略（先删除后插入）

**说明**：
- 系统已改用 `upsert_all` 方法处理重复数据
- 同一日期的数据会先删除再插入，避免约束冲突
- 若仍遇到问题，可手动删除当日数据后重试：
```bash
# 通过API重新抓取当日数据
curl -X POST "http://localhost:9988/api/stocks/fetch"
```

---

## 8. 注意事项

### 8.1 数据源限制

| 限制项 | 说明 |
|--------|------|
| **数据来源** | MOOTDX（通达信数据接口），免费数据源 |
| **股票范围** | 仅支持沪深A股，已过滤北交所 |
| **数据时效** | 实时数据延迟约3秒，非实时行情 |
| **财务数据** | 需手动下载 gpcw*.zip 文件后解析 |

### 8.2 使用限制

| 限制项 | 说明 |
|--------|------|
| **请求频率** | 建议不要高频请求，避免被封IP |
| **批量限制** | 批量接口有数量限制（通常50条） |
| **仅供学习** | 本系统仅供学习研究，不建议用于实盘交易 |

### 8.3 已不支持的功能

以下功能因数据源限制已移除：

| 功能 | 原因 |
|------|------|
| ETF基金数据 | MOOTDX 不支持 |
| 资金流向数据 | MOOTDX 不支持 |
| 龙虎榜数据 | MOOTDX 不支持 |
| 大宗交易数据 | MOOTDX 不支持 |
| 分红配送数据 | MOOTDX 不支持 |

### 8.4 数据准确性

- **行情数据**：来源于通达信，与券商数据可能存在微小差异
- **财务数据**：解析自通达信财务文件，字段为精简版（非完整300+字段）
- **技术指标**：使用 pandas-ta 计算，计算逻辑与主流软件一致

### 8.5 系统资源

| 项目 | 占用 |
|------|------|
| 内存 | 约 100-300MB（视数据量） |
| 磁盘 | 数据库约 50-200MB（视数据积累） |
| CPU | 计算指标时会有短暂峰值 |

### 8.6 安全提醒

- 本系统为纯后端 API 服务，无用户认证机制
- 如需对外暴露，建议添加认证中间件
- 投资决策请结合多方面信息，勿完全依赖本系统

---

## 附录：支持的股票代码格式

| 市场 | 代码格式 | 示例 |
|------|----------|------|
| 上证主板 | 60xxxx | 600000、601318 |
| 上证科创板 | 68xxxx | 688001 |
| 深证主板 | 00xxxx | 000001、000002 |
| 深证创业板 | 30xxxx | 300001、300750 |

**已过滤**：北交所（8xxxxx、4xxxxx）不支持