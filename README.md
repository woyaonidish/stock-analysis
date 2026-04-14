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
│   ├── index_service.py           # 指数服务
│   ├── financial_service.py       # 财务数据服务
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
- 股票列表（A股全量，过滤北交所）
- 指数实时行情（上证指数、深证成指、创业板指等9只主要指数）
- 财务数据（300+字段，含每股指标、盈利能力、成长能力、资产负债、现金流等）
- 交易日历

### 5. 指数行情

支持9只主要指数实时行情：
- 上证指数 (000001)
- 上证50 (000016)
- 沪深300 (000300)
- 中证500 (000905)
- 中证1000 (000852)
- 深证成指 (399001)
- 创业板指 (399006)
- 中小板指 (399005)

### 6. 财务数据

精简核心财务指标（26个字段）：
- 每股指标：EPS、扣非EPS、每股净资产、每股现金流
- 盈利能力：ROE、销售净利率、销售毛利率
- 成长能力：营收增长率、净利润增长率
- 资产负债：资产负债率、流动比率、速动比率
- 核心财务：营收、净利润、总资产、净资产
- 现金流：经营/投资/筹资现金流
- 股本数据：总股本、流通A股

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

## 2. 指数行情接口 (/api/index)

### 2.1 获取指数列表

**接口**：`GET /api/index/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD)，默认当天 |

**请求示例**：
```
GET /api/index/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "上证指数",
            "date": "2026-04-08",
            "open_price": 3250.50,
            "close_price": 3280.25,
            "high_price": 3295.00,
            "low_price": 3245.00,
            "pre_close": 3250.00,
            "change_rate": 0.93,
            "volume": 256789000,
            "amount": 3521678900
        },
        {
            "code": "399001",
            "name": "深证成指",
            "date": "2026-04-08",
            "open_price": 10580.00,
            "close_price": 10650.50,
            "high_price": 10700.00,
            "low_price": 10550.00,
            "pre_close": 10580.00,
            "change_rate": 0.67,
            "volume": 189456000,
            "amount": 2895678900
        }
    ]
}
```

---

### 2.2 获取指数详情

**接口**：`GET /api/index/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 指数代码（路径参数） |
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**支持指数**：
- 000001 - 上证指数
- 000016 - 上证50
- 000300 - 沪深300
- 000905 - 中证500
- 000852 - 中证1000
- 399001 - 深证成指
- 399005 - 中小板指
- 399006 - 创业板指

**请求示例**：
```
GET /api/index/000001?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "name": "上证指数",
        "date": "2026-04-08",
        "open_price": 3250.50,
        "close_price": 3280.25,
        "high_price": 3295.00,
        "low_price": 3245.00,
        "pre_close": 3250.00,
        "change_rate": 0.93,
        "volume": 256789000,
        "amount": 3521678900
    }
}
```

---

### 2.3 抓取并保存指数数据

**接口**：`POST /api/index/fetch`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
POST /api/index/fetch?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 8
    }
}
```

---

## 3. 财务数据接口 (/api/financial)

### 3.1 获取股票财务数据

**接口**：`GET /api/financial/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| report_date | string | 否 | 报告期(YYYY-MM-DD)，默认最新 |

**请求示例**：
```
GET /api/financial/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "report_date": "2025-12-31",
        "eps": 1.25,
        "eps_deducted": 1.18,
        "bvps": 18.50,
        "cfps": 2.30,
        "roe": 12.5,
        "roe_weighted": 13.2,
        "net_profit_margin": 25.6,
        "gross_profit_margin": 45.8,
        "revenue_growth": 8.5,
        "net_profit_growth": 12.3,
        "debt_ratio": 62.5,
        "current_ratio": 1.85,
        "quick_ratio": 1.45,
        "revenue": 45678900000,
        "net_profit": 11674500000,
        "net_profit_parent": 11567800000,
        "net_profit_deducted": 10892300000,
        "total_assets": 589678000000,
        "net_assets": 221345000000,
        "operating_cf": 35678900000,
        "investing_cf": -12567800000,
        "financing_cf": -8967800000,
        "total_shares": 19405000000,
        "float_shares_a": 19405000000
    }
}
```

---

### 3.2 获取历史财务数据

**接口**：`GET /api/financial/{code}/history`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| limit | int | 否 | 返回数量，默认8个报告期 |

**请求示例**：
```
GET /api/financial/000001/history?limit=4
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "report_date": "2025-12-31",
            "eps": 1.25,
            "roe": 12.5,
            "revenue_growth": 8.5,
            "net_profit_growth": 12.3,
            "revenue": 45678900000,
            "net_profit": 11674500000
        },
        {
            "code": "000001",
            "report_date": "2025-09-30",
            "eps": 0.95,
            "roe": 9.8,
            "revenue_growth": 7.2,
            "net_profit_growth": 10.5,
            "revenue": 34567800000,
            "net_profit": 8894500000
        }
    ]
}
```

---

### 3.3 获取最新报告期

**接口**：`GET /api/financial/latest-report-date`

**参数**：无

**请求示例**：
```
GET /api/financial/latest-report-date
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "report_date": "2025-12-31"
    }
}
```

---

### 3.4 解析财务数据文件

**接口**：`POST /api/financial/parse`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| filepath | string | 是 | 财务数据文件路径(gpcw*.zip) |

**请求示例**：
```
POST /api/financial/parse?filepath=./data/gpcw20231231.zip
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

**备注**：需先下载财务数据文件：
```bash
python -c "from mootdx.affair import Affair; Affair.fetch(downdir='./data', filename='gpcw20231231.zip')"
```

---

## 4. 技术指标接口 (/api/indicators)

### 4.1 获取股票指标

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

### 4.2 获取所有股票指标

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

### 4.3 获取买入信号

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

### 4.4 获取卖出信号

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

### 4.5 计算并保存指标

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

## 5. 策略选股接口 (/api/strategy)

### 5.1 获取策略类型列表

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

### 5.2 获取策略结果

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

### 5.3 运行策略

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

### 5.4 运行所有策略

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

## 6. 回测接口 (/api/backtest)

### 6.1 运行回测

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

### 6.2 运行所有策略回测

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
- `cn_stock_index_spot` - 指数实时行情
- `cn_stock_financial` - 股票财务数据（核心指标）
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