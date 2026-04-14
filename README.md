# InStock 股票分析系统

InStock股票分析系统是一个基于 FastAPI 的股票量化分析平台，提供股票数据抓取、技术指标计算、K线形态识别、策略选股等功能。采用三层架构设计，纯后端 REST API 服务，使用 MOOTDX（通达信数据接口）作为数据源。

## 技术栈

| 类别 | 技术 |
|------|------|
| Web框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 技术指标 | pandas-ta (纯Python) |
| 数据处理 | Pandas, NumPy |
| HTTP客户端 | httpx (支持异步) |
| 数据源 | MOOTDX (通达信数据接口) |
| 日志 | loguru (支持IDE跳转) |
| 定时任务 | APScheduler |

## 项目结构

```
instock-app/
├── calculator/          # 计算器层
│   ├── indicator_calculator.py    # 技术指标计算
│   └── pattern_recognizer.py      # K线形态识别
├── controller/          # 控制器层 (API接口)
│   ├── stock_controller.py        # 股票数据接口
│   ├── indicator_controller.py    # 技术指标接口
│   ├── strategy_controller.py     # 策略选股接口
│   └── backtest_controller.py     # 回测接口
├── crawler/             # 爬虫层
│   ├── tdx_fetcher.py             # MOOTDX数据获取
│   ├── trade_date_crawler.py      # 交易日历
│   └── base_crawler.py            # 爬虫基类
├── dao/                 # 数据访问层
├── entity/              # 实体类
├── service/             # 服务层
│   ├── stock_service.py           # 股票服务
│   ├── indicator_service.py       # 指标计算服务
│   ├── pattern_service.py         # 形态识别服务
│   └── strategy_service.py        # 策略选股服务
├── scheduler/           # 定时任务
├── data/                # SQLite数据库目录
├── config.py            # 配置文件
├── database.py          # 数据库连接
└── main.py              # 应用入口
```

## 功能特性

### 1. 技术指标计算

支持 30+ 种技术指标：

- 趋势指标：MA、EMA、MACD、BOLL (使用 pandas-ta 计算)
- 动量指标：RSI、KDJ、CCI、WR
- 波动指标：ATR、TR
- 成交量指标：OBV、MFI、VOL_MA
- 其他：TRIX、ROC 等

### 2. K线形态识别

支持 17 种 K 线形态识别 (纯Python实现)：

- 反转形态：锤子线、倒锤子线、吞没形态、启明星、黄昏星
- 持续形态：三白兵、三只乌鸦
- 十字星类：十字星、蜻蜓十字星、墓碑十字星
- 其他：流星线、上吊线、乌云盖顶、刺透形态等

### 3. 策略选股

内置多种选股策略：

- 放量上涨
- 突破平台
- 低ATR
- 海龟交易
- 高紧旗
- 停机坪
- 持续上涨

### 4. 数据抓取 (MOOTDX)

- 股票实时行情（含五档买卖盘）
- 股票历史K线（日线/周线/月线）
- 股票分时数据（1/5/15/30/60分钟）
- 股票列表（A股全量）
- 交易日历

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
cd app
python -m app.main
```

服务启动后会自动：
1. 创建数据库目录 `data/`
2. 创建 SQLite 数据库文件
3. 创建所有数据表
4. 若是交易日且无数据，自动获取当日股票数据

### 访问 API 文档

- Swagger UI: http://localhost:9988/docs
- ReDoc: http://localhost:9988/redoc

## API 接口文档

### 通用响应格式

```json
{
    "code": 0,
    "message": "success",
    "data": {}
}
```

---

## 1. 股票数据接口 (/api/stocks)

### 1.1 获取股票列表

**接口**：`GET /api/stocks/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD)，默认当天 |

**请求示例**：
```
GET /api/stocks/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "平安银行",
            "open_price": 12.10,
            "close_price": 12.34,
            "high_price": 12.50,
            "low_price": 12.05,
            "volume": 12345678,
            "amount": 152345678.90,
            "bid1": 12.33,
            "bid1_vol": 5000,
            "ask1": 12.34,
            "ask1_vol": 3000
        }
    ]
}
```

---

### 1.2 获取股票详情

**接口**：`GET /api/stocks/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
GET /api/stocks/000001?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "name": "平安银行",
        "date": "2026-04-08",
        "open_price": 12.10,
        "close_price": 12.34,
        "high_price": 12.50,
        "low_price": 12.05,
        "pre_close_price": 12.08,
        "volume": 12345678,
        "amount": 152345678.90,
        "bid1": 12.33,
        "bid1_vol": 5000,
        "ask1": 12.34,
        "ask1_vol": 3000
    }
}
```

---

### 1.3 获取股票历史数据

**接口**：`GET /api/stocks/{code}/hist`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| start_date | string | 否 | 开始日期(YYYYMMDD) |
| end_date | string | 否 | 结束日期(YYYYMMDD) |
| period | string | 否 | 周期：daily/weekly/monthly，默认daily |

**请求示例**：
```
GET /api/stocks/000001/hist?start_date=20260101&end_date=20260408&period=daily
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "date": "2026-04-08",
            "open": 12.10,
            "close": 12.34,
            "high": 12.50,
            "low": 12.05,
            "volume": 12345678,
            "amount": 152345678.90
        }
    ]
}
```

---

### 1.4 获取股票分时数据

**接口**：`GET /api/stocks/{code}/min`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| period | string | 否 | 周期：1/5/15/30/60分钟，默认5 |

**请求示例**：
```
GET /api/stocks/000001/min?period=5
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "time": "2026-04-08 09:35:00",
            "open": 12.10,
            "close": 12.15,
            "high": 12.18,
            "low": 12.08,
            "volume": 123456,
            "amount": 1498765.00
        }
    ]
}
```

---

### 1.5 搜索股票

**接口**：`GET /api/stocks/search/{keyword}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | string | 是 | 搜索关键词（代码或名称） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/stocks/search/平安
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "平安银行",
            "close_price": 12.34
        }
    ]
}
```

---

### 1.6 抓取并保存每日数据

**接口**：`POST /api/stocks/fetch`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
POST /api/stocks/fetch?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 5200
    }
}
```

---

## 2. 技术指标接口 (/api/indicators)

### 2.1 获取股票指标

**接口**：`GET /api/indicators/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "date": "2026-04-08",
        "macd": 0.123,
        "macds": 0.456,
        "macdh": 0.067,
        "kdjk": 78.5,
        "kdjd": 65.2,
        "kdjj": 105.1,
        "rsi": 62.3,
        "rsi_6": 65.4,
        "rsi_12": 58.9,
        "rsi_24": 55.2,
        "atr": 0.35,
        "cci": 85.6,
        "wr_6": -25.4,
        "wr_10": -32.1
    }
}
```

---

### 2.2 获取所有股票指标

**接口**：`GET /api/indicators/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "date": "2026-04-08",
            "macd": 0.123,
            "kdjk": 78.5,
            "rsi": 62.3,
            "cci": 85.6
        }
    ]
}
```

---

### 2.3 获取买入信号

**接口**：`GET /api/indicators/signals/buy`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/signals/buy
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {"code": "000001", "date": "2026-04-08"},
        {"code": "000002", "date": "2026-04-08"}
    ]
}
```

---

### 2.4 获取卖出信号

**接口**：`GET /api/indicators/signals/sell`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/signals/sell
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {"code": "600000", "date": "2026-04-08"}
    ]
}
```

---

### 2.5 计算并保存指标

**接口**：`POST /api/indicators/calculate/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
POST /api/indicators/calculate/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001"
    }
}
```

---

## 3. 策略选股接口 (/api/strategy)

### 3.1 获取策略类型列表

**接口**：`GET /api/strategy/types`

**参数**：无

**请求示例**：
```
GET /api/strategy/types
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {"type": "volume_up", "name": "放量上涨"},
        {"type": "breakthrough", "name": "突破平台"},
        {"type": "low_atr", "name": "低ATR"},
        {"type": "turtle", "name": "海龟交易"},
        {"type": "high_tight_flag", "name": "高紧旗"},
        {"type": "parking_apron", "name": "停机坪"},
        {"type": "keep_increasing", "name": "持续上涨"}
    ]
}
```

---

### 3.2 获取策略结果

**接口**：`GET /api/strategy/{strategy_type}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| strategy_type | string | 是 | 策略类型（路径参数） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/strategy/volume_up?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "date": "2026-04-08",
            "strategy_type": "volume_up",
            "score": 1.0
        }
    ]
}
```

---

### 3.3 运行策略

**接口**：`POST /api/strategy/run`

**请求体**：
```json
{
    "strategy_type": "volume_up",
    "trade_date": "2026-04-08"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| strategy_type | string | 是 | 策略类型 |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
POST /api/strategy/run
Content-Type: application/json

{
    "strategy_type": "volume_up",
    "trade_date": "2026-04-08"
}
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "strategy_type": "volume_up",
        "trade_date": "2026-04-08",
        "count": 125
    }
}
```

---

### 3.4 运行所有策略

**接口**：`POST /api/strategy/run-all`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
POST /api/strategy/run-all?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "volume_up": 125,
        "breakthrough": 45,
        "low_atr": 89,
        "turtle": 32,
        "high_tight_flag": 18,
        "parking_apron": 67,
        "keep_increasing": 23
    }
}
```

---

## 4. 回测接口 (/api/backtest)

### 4.1 运行回测

**接口**：`POST /api/backtest/run`

**请求体**：
```json
{
    "strategy_type": "volume_up",
    "start_date": "2025-01-01",
    "end_date": "2026-04-08",
    "initial_capital": 100000.0
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| strategy_type | string | 是 | 策略类型 |
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |
| initial_capital | float | 否 | 初始资金，默认100000 |

**请求示例**：
```
POST /api/backtest/run
Content-Type: application/json

{
    "strategy_type": "volume_up",
    "start_date": "2025-01-01",
    "end_date": "2026-04-08",
    "initial_capital": 100000
}
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "strategy_type": "volume_up",
        "total_return": 15.6,
        "annual_return": 12.3,
        "max_drawdown": -8.5,
        "sharpe_ratio": 1.25,
        "win_rate": 58.5,
        "total_trades": 156
    }
}
```

---

### 4.2 运行所有策略回测

**接口**：`POST /api/backtest/run-all`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |

**请求示例**：
```
POST /api/backtest/run-all?start_date=2025-01-01&end_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "volume_up": {"total_return": 15.6, "sharpe_ratio": 1.25},
        "breakthrough": {"total_return": 12.3, "sharpe_ratio": 1.05},
        "low_atr": {"total_return": 18.9, "sharpe_ratio": 1.45}
    }
}
```

---

## 配置说明

配置文件：`app/config.py`

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务地址 |
| `PORT` | 9988 | 服务端口 |
| `DB_FILE` | data/instock.db | 数据库文件路径 |
| `SCHEDULER_ENABLED` | True | 是否启用定时任务 |
| `PROXY_ENABLED` | False | 是否启用代理 |

## 定时任务

系统内置以下定时任务：

| 任务 | 时间 | 说明 |
|------|------|------|
| 每日数据抓取 | 15:30 | 抓取当日股票数据 |
| 指标计算 | 16:00 | 计算技术指标 |
| 策略选股 | 16:30 | 运行选股策略 |

## 数据库

使用 SQLite 数据库，数据文件位于 `app/data/instock.db`。

主要数据表：
- `cn_stock_spot` - 股票实时行情（含五档买卖盘）
- `cn_stock_indicator` - 技术指标
- `cn_stock_pattern` - K线形态
- `cn_stock_strategy_*` - 策略选股结果

## 开发说明

### 三层架构

```
Controller (API接口)
    ↓
Service (业务逻辑)
    ↓
DAO (数据访问)
    ↓
Entity (数据实体)
```

### 添加新功能

1. 在 `entity/` 创建实体类
2. 在 `dao/` 创建数据访问类
3. 在 `service/` 创建业务服务类
4. 在 `controller/` 创建 API 接口
5. 在 `main.py` 注册路由

## 注意事项

- 数据来源：MOOTDX（通达信数据接口）
- 本系统仅供学习研究使用
- 股市有风险，投资需谨慎

## License

MIT License